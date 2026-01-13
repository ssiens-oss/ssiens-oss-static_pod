/**
 * Worker Pool Manager
 * Manages multiple production pod engine workers for parallel processing
 */

import { EventEmitter } from 'events'
import { ProductionPodEngine, EngineConfig, JobRequest } from './ProductionPodEngine'
import { IDatabaseClient } from './DatabaseClient'

export interface WorkerPoolConfig {
  workerCount: number
  engineConfig: EngineConfig
  autoRestart?: boolean
  maxRestarts?: number
  restartDelay?: number
}

export interface WorkerInfo {
  id: string
  index: number
  status: 'starting' | 'running' | 'stopping' | 'stopped' | 'error'
  engine?: ProductionPodEngine
  restarts: number
  startedAt?: Date
  lastError?: string
}

/**
 * Worker Pool
 * Manages multiple engine workers for horizontal scaling
 */
export class WorkerPool extends EventEmitter {
  private config: WorkerPoolConfig
  private workers: Map<string, WorkerInfo> = new Map()
  private db: IDatabaseClient
  private isRunning: boolean = false
  private roundRobinIndex: number = 0

  constructor(config: WorkerPoolConfig, db: IDatabaseClient) {
    super()
    this.config = config
    this.db = db
  }

  /**
   * Start all workers
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      throw new Error('Worker pool is already running')
    }

    console.log(`[WorkerPool] Starting ${this.config.workerCount} workers...`)

    this.isRunning = true

    // Start workers in parallel
    const startPromises = []
    for (let i = 0; i < this.config.workerCount; i++) {
      startPromises.push(this.startWorker(i))
    }

    await Promise.all(startPromises)

    console.log(`[WorkerPool] All workers started`)
    this.emit('started', { workerCount: this.workers.size })
  }

  /**
   * Stop all workers
   */
  async stop(): Promise<void> {
    if (!this.isRunning) {
      return
    }

    console.log('[WorkerPool] Stopping all workers...')

    this.isRunning = false

    // Stop all workers
    const stopPromises = []
    for (const worker of this.workers.values()) {
      stopPromises.push(this.stopWorker(worker.id))
    }

    await Promise.all(stopPromises)

    this.workers.clear()

    console.log('[WorkerPool] All workers stopped')
    this.emit('stopped')
  }

  /**
   * Start a single worker
   */
  private async startWorker(index: number): Promise<void> {
    const workerId = `worker_${index}_${Date.now()}`

    const workerInfo: WorkerInfo = {
      id: workerId,
      index,
      status: 'starting',
      restarts: 0
    }

    this.workers.set(workerId, workerInfo)

    try {
      // Create engine with unique worker ID
      const engineConfig: EngineConfig = {
        ...this.config.engineConfig,
        engine: {
          ...this.config.engineConfig.engine,
          workerId
        }
      }

      const engine = new ProductionPodEngine(engineConfig)

      // Setup event listeners
      this.setupEngineListeners(workerId, engine)

      // Start engine
      await engine.start()

      // Update worker info
      workerInfo.engine = engine
      workerInfo.status = 'running'
      workerInfo.startedAt = new Date()

      this.emit('worker:started', { workerId, index })
      console.log(`[WorkerPool] Worker ${index} (${workerId}) started`)
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error)
      workerInfo.status = 'error'
      workerInfo.lastError = errorMsg

      this.emit('worker:error', { workerId, index, error: errorMsg })
      console.error(`[WorkerPool] Failed to start worker ${index}:`, errorMsg)

      // Auto-restart if enabled
      if (this.config.autoRestart && workerInfo.restarts < (this.config.maxRestarts || 3)) {
        this.scheduleRestart(workerId)
      }
    }
  }

  /**
   * Stop a single worker
   */
  private async stopWorker(workerId: string): Promise<void> {
    const worker = this.workers.get(workerId)
    if (!worker || !worker.engine) {
      return
    }

    worker.status = 'stopping'

    try {
      await worker.engine.stop()
      worker.status = 'stopped'
      this.emit('worker:stopped', { workerId, index: worker.index })
      console.log(`[WorkerPool] Worker ${worker.index} (${workerId}) stopped`)
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error)
      console.error(`[WorkerPool] Error stopping worker ${worker.index}:`, errorMsg)
    }
  }

  /**
   * Schedule worker restart
   */
  private scheduleRestart(workerId: string): void {
    const worker = this.workers.get(workerId)
    if (!worker) return

    const delay = this.config.restartDelay || 5000 // 5 seconds
    worker.restarts++

    console.log(`[WorkerPool] Scheduling restart for worker ${worker.index} in ${delay}ms (attempt ${worker.restarts})`)

    setTimeout(async () => {
      if (this.isRunning) {
        console.log(`[WorkerPool] Restarting worker ${worker.index}...`)
        this.workers.delete(workerId)
        await this.startWorker(worker.index)
      }
    }, delay)
  }

  /**
   * Setup engine event listeners
   */
  private setupEngineListeners(workerId: string, engine: ProductionPodEngine): void {
    // Forward important events
    engine.on('job:submitted', (data) => {
      this.emit('job:submitted', { ...data, workerId })
    })

    engine.on('job:completed', (data) => {
      this.emit('job:completed', { ...data, workerId })
    })

    engine.on('job:failed', (data) => {
      this.emit('job:failed', { ...data, workerId })
    })

    engine.on('log', (data) => {
      this.emit('log', { ...data, workerId })
    })

    // Handle engine errors
    engine.on('error', (error) => {
      const worker = this.workers.get(workerId)
      if (worker) {
        worker.status = 'error'
        worker.lastError = error instanceof Error ? error.message : String(error)
        this.emit('worker:error', { workerId, index: worker.index, error: worker.lastError })

        // Auto-restart if enabled
        if (this.config.autoRestart && worker.restarts < (this.config.maxRestarts || 3)) {
          this.scheduleRestart(workerId)
        }
      }
    })
  }

  /**
   * Submit job to a worker (round-robin load balancing)
   */
  async submitJob(request: JobRequest): Promise<string> {
    const runningWorkers = Array.from(this.workers.values()).filter(
      w => w.status === 'running' && w.engine
    )

    if (runningWorkers.length === 0) {
      throw new Error('No running workers available')
    }

    // Round-robin selection
    const worker = runningWorkers[this.roundRobinIndex % runningWorkers.length]
    this.roundRobinIndex++

    return await worker.engine!.submitJob(request)
  }

  /**
   * Submit job to least loaded worker
   */
  async submitJobToLeastLoaded(request: JobRequest): Promise<string> {
    const runningWorkers = Array.from(this.workers.values()).filter(
      w => w.status === 'running' && w.engine
    )

    if (runningWorkers.length === 0) {
      throw new Error('No running workers available')
    }

    // Get stats from all workers
    const workerStats = await Promise.all(
      runningWorkers.map(async w => ({
        worker: w,
        stats: await w.engine!.getStats()
      }))
    )

    // Find worker with least queue size
    workerStats.sort((a, b) => {
      const aLoad = a.stats.queue.queued + a.stats.queue.processing
      const bLoad = b.stats.queue.queued + b.stats.queue.processing
      return aLoad - bLoad
    })

    const leastLoadedWorker = workerStats[0].worker

    return await leastLoadedWorker.engine!.submitJob(request)
  }

  /**
   * Get pool statistics
   */
  async getStats(): Promise<{
    totalWorkers: number
    runningWorkers: number
    errorWorkers: number
    totalJobs: number
    totalCompleted: number
    totalFailed: number
    workers: Array<{
      id: string
      index: number
      status: string
      stats?: any
    }>
  }> {
    const workers = Array.from(this.workers.values())
    const runningWorkers = workers.filter(w => w.status === 'running')
    const errorWorkers = workers.filter(w => w.status === 'error')

    // Get stats from running workers
    const workerStats = await Promise.all(
      runningWorkers.map(async w => ({
        id: w.id,
        index: w.index,
        status: w.status,
        stats: w.engine ? await w.engine.getStats() : null
      }))
    )

    // Aggregate job counts
    const totalJobs = workerStats.reduce((sum, w) => sum + (w.stats?.database.totalJobs || 0), 0)
    const totalCompleted = workerStats.reduce((sum, w) => sum + (w.stats?.queue.completed || 0), 0)
    const totalFailed = workerStats.reduce((sum, w) => sum + (w.stats?.queue.failed || 0), 0)

    return {
      totalWorkers: workers.length,
      runningWorkers: runningWorkers.length,
      errorWorkers: errorWorkers.length,
      totalJobs,
      totalCompleted,
      totalFailed,
      workers: workerStats
    }
  }

  /**
   * Health check for all workers
   */
  async healthCheck(): Promise<{
    healthy: boolean
    workers: Array<{
      id: string
      index: number
      healthy: boolean
      health?: any
    }>
  }> {
    const workers = Array.from(this.workers.values()).filter(
      w => w.status === 'running' && w.engine
    )

    const checks = await Promise.all(
      workers.map(async w => ({
        id: w.id,
        index: w.index,
        healthy: w.status === 'running',
        health: w.engine ? await w.engine.healthCheck() : null
      }))
    )

    const allHealthy = checks.every(c => c.healthy && c.health?.healthy)

    return {
      healthy: allHealthy && workers.length > 0,
      workers: checks
    }
  }

  /**
   * Get specific worker
   */
  getWorker(workerId: string): WorkerInfo | undefined {
    return this.workers.get(workerId)
  }

  /**
   * List all workers
   */
  listWorkers(): WorkerInfo[] {
    return Array.from(this.workers.values())
  }

  /**
   * Restart a specific worker
   */
  async restartWorker(workerId: string): Promise<void> {
    const worker = this.workers.get(workerId)
    if (!worker) {
      throw new Error(`Worker ${workerId} not found`)
    }

    await this.stopWorker(workerId)
    this.workers.delete(workerId)
    await this.startWorker(worker.index)
  }

  /**
   * Scale worker pool
   */
  async scale(newWorkerCount: number): Promise<void> {
    const currentCount = this.workers.size

    if (newWorkerCount === currentCount) {
      return
    }

    if (newWorkerCount > currentCount) {
      // Scale up
      const workersToAdd = newWorkerCount - currentCount
      console.log(`[WorkerPool] Scaling up by ${workersToAdd} workers`)

      const startPromises = []
      for (let i = currentCount; i < newWorkerCount; i++) {
        startPromises.push(this.startWorker(i))
      }

      await Promise.all(startPromises)
    } else {
      // Scale down
      const workersToRemove = currentCount - newWorkerCount
      console.log(`[WorkerPool] Scaling down by ${workersToRemove} workers`)

      const workersArray = Array.from(this.workers.values())
      const toStop = workersArray.slice(-workersToRemove)

      const stopPromises = toStop.map(w => this.stopWorker(w.id))
      await Promise.all(stopPromises)

      toStop.forEach(w => this.workers.delete(w.id))
    }

    this.config.workerCount = newWorkerCount
    this.emit('scaled', { newWorkerCount, previousCount: currentCount })
  }
}

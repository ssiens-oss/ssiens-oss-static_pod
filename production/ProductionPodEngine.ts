/**
 * Production POD Engine
 * Enterprise-grade pod automation engine with job queuing, persistence, and monitoring
 */

import { EventEmitter } from 'events'
import { Orchestrator } from '../services/orchestrator'
import { JobQueue, JobData, JobResult } from './JobQueue'
import { IDatabaseClient, createDatabaseClient, Job } from './DatabaseClient'
import os from 'os'

export interface EngineConfig {
  // Orchestrator config
  orchestrator: {
    comfyui: {
      apiUrl: string
      outputDir: string
    }
    claude: {
      apiKey: string
    }
    storage: {
      type: 'local' | 's3' | 'gcs'
      basePath: string
    }
    printify?: {
      apiKey: string
      shopId: string
    }
    shopify?: {
      storeUrl: string
      accessToken: string
    }
    tiktok?: {
      appKey: string
      appSecret: string
      shopId: string
      accessToken: string
    }
    etsy?: {
      apiKey: string
      shopId: string
      accessToken: string
    }
    instagram?: {
      accessToken: string
      businessAccountId: string
    }
    facebook?: {
      pageId: string
      accessToken: string
      catalogId: string
    }
    options?: {
      enabledPlatforms?: string[]
      autoPublish?: boolean
      tshirtPrice?: number
      hoodiePrice?: number
    }
  }

  // Engine config
  engine: {
    workerId?: string
    maxConcurrentJobs?: number
    jobTimeout?: number
    retryDelay?: number
    enableAutoRetry?: boolean
    heartbeatInterval?: number
  }

  // Database config
  database?: {
    type?: 'memory' | 'postgres'
    connectionString?: string
  }
}

export interface JobRequest {
  prompt?: string
  theme?: string
  style?: string
  niche?: string
  productTypes: ('tshirt' | 'hoodie')[]
  count?: number
  autoPublish?: boolean
  priority?: number
}

export interface EngineStats {
  worker: {
    id: string
    hostname: string
    status: string
    uptime: number
    jobs_processed: number
    jobs_failed: number
  }
  queue: {
    queued: number
    processing: number
    completed: number
    failed: number
    activeWorkers: number
    maxWorkers: number
  }
  database: {
    connected: boolean
    totalJobs: number
    totalImages: number
    totalProducts: number
  }
}

/**
 * Production POD Engine
 */
export class ProductionPodEngine extends EventEmitter {
  private orchestrator: Orchestrator
  private queue: JobQueue
  private db: IDatabaseClient
  private config: EngineConfig
  private workerId: string
  private hostname: string
  private startTime: Date
  private heartbeatTimer?: NodeJS.Timeout
  private isRunning: boolean = false
  private jobsProcessed: number = 0
  private jobsFailed: number = 0

  constructor(config: EngineConfig) {
    super()

    this.config = config
    this.hostname = os.hostname()
    this.workerId = config.engine.workerId || `worker_${this.hostname}_${Date.now()}`
    this.startTime = new Date()

    // Initialize orchestrator
    this.orchestrator = new Orchestrator(config.orchestrator)

    // Initialize job queue
    this.queue = new JobQueue({
      maxConcurrent: config.engine.maxConcurrentJobs || 5,
      retryDelay: config.engine.retryDelay || 60000,
      jobTimeout: config.engine.jobTimeout || 3600000,
      enableAutoRetry: config.engine.enableAutoRetry ?? true
    })

    // Initialize database
    this.db = createDatabaseClient(config.database)

    // Setup queue event handlers
    this.setupQueueHandlers()

    // Setup orchestrator logger
    this.orchestrator.setLogger((message, type) => {
      this.emit('log', { message, type, workerId: this.workerId })
    })
  }

  /**
   * Start the engine
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      throw new Error('Engine is already running')
    }

    try {
      // Connect to database
      await this.db.connect()

      // Register worker
      await this.db.registerWorker({
        id: this.workerId,
        hostname: this.hostname,
        status: 'idle',
        metadata: {
          pid: process.pid,
          version: '1.0.0',
          config: {
            maxConcurrent: this.config.engine.maxConcurrentJobs,
            platforms: this.config.orchestrator.options?.enabledPlatforms
          }
        }
      })

      // Start heartbeat
      this.startHeartbeat()

      this.isRunning = true

      this.emit('started', { workerId: this.workerId, hostname: this.hostname })
      console.log(`[Engine] Started worker ${this.workerId} on ${this.hostname}`)
    } catch (error) {
      console.error('[Engine] Failed to start:', error)
      throw error
    }
  }

  /**
   * Stop the engine gracefully
   */
  async stop(): Promise<void> {
    if (!this.isRunning) {
      return
    }

    console.log('[Engine] Stopping gracefully...')
    this.isRunning = false

    // Stop heartbeat
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
    }

    // Shutdown queue
    await this.queue.shutdown()

    // Update worker status
    await this.db.updateWorker(this.workerId, { status: 'offline' })

    // Disconnect database
    await this.db.disconnect()

    this.emit('stopped', { workerId: this.workerId })
    console.log('[Engine] Stopped')
  }

  /**
   * Submit a new job
   */
  async submitJob(request: JobRequest): Promise<string> {
    if (!this.isRunning) {
      throw new Error('Engine is not running')
    }

    // Create job in database
    const dbJob = await this.db.createJob({
      status: 'queued',
      priority: request.priority || 0,
      request,
      retry_count: 0,
      max_retries: 3
    })

    // Add to queue
    const jobId = await this.queue.addJob(request, {
      priority: request.priority,
      maxRetries: 3
    })

    // Update database with queue ID
    await this.db.updateJob(dbJob.id, { worker_id: jobId })

    this.emit('job:submitted', { jobId: dbJob.id, workerId: this.workerId })

    return dbJob.id
  }

  /**
   * Get job status
   */
  async getJobStatus(jobId: string): Promise<Job | null> {
    return await this.db.getJob(jobId)
  }

  /**
   * Get job result
   */
  async getJobResult(jobId: string): Promise<any> {
    const job = await this.db.getJob(jobId)
    return job?.result || null
  }

  /**
   * Get engine statistics
   */
  async getStats(): Promise<EngineStats> {
    const queueStats = this.queue.getStats()
    const dbHealth = await this.db.healthCheck()
    const allJobs = await this.db.listJobs()

    return {
      worker: {
        id: this.workerId,
        hostname: this.hostname,
        status: this.isRunning ? 'running' : 'stopped',
        uptime: Date.now() - this.startTime.getTime(),
        jobs_processed: this.jobsProcessed,
        jobs_failed: this.jobsFailed
      },
      queue: queueStats,
      database: {
        connected: dbHealth,
        totalJobs: allJobs.length,
        totalImages: 0, // Would query from DB
        totalProducts: 0 // Would query from DB
      }
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{
    healthy: boolean
    worker: boolean
    queue: boolean
    database: boolean
    orchestrator: boolean
  }> {
    const dbHealth = await this.db.healthCheck()
    const orchestratorHealth = await this.orchestrator.getStats()

    return {
      healthy: this.isRunning && dbHealth && orchestratorHealth.services.comfyui,
      worker: this.isRunning,
      queue: true, // Queue is always healthy if running
      database: dbHealth,
      orchestrator: orchestratorHealth.services.comfyui
    }
  }

  /**
   * Setup queue event handlers
   */
  private setupQueueHandlers(): void {
    // Handle job execution
    this.queue.on('job:execute', async (job: JobData, callback: any) => {
      try {
        await this.recordLog(job.id, 'INFO', 'Job execution started')

        // Update job status in database
        const dbJob = await this.findDbJobByWorkerId(job.id)
        if (dbJob) {
          await this.db.updateJob(dbJob.id, {
            status: 'processing',
            started_at: new Date(),
            worker_id: this.workerId
          })
        }

        // Update worker status
        await this.db.updateWorker(this.workerId, {
          status: 'busy',
          current_job_id: dbJob?.id
        })

        // Execute via orchestrator
        const result = await this.orchestrator.run({
          ...job.request,
          productTypes: job.request.productTypes || ['tshirt']
        })

        // Store images in database
        if (dbJob) {
          for (const img of result.generatedImages) {
            await this.db.createImage({
              job_id: dbJob.id,
              image_url: img.url,
              storage_path: img.url,
              prompt: img.prompt,
              title: 'Generated Design',
              metadata: { generatedAt: new Date() }
            })
          }

          // Store products in database
          const images = await this.db.listImagesByJob(dbJob.id)
          for (const product of result.products) {
            await this.db.createProduct({
              job_id: dbJob.id,
              image_id: images[0]?.id || 'unknown',
              platform: product.platform,
              platform_product_id: product.productId,
              product_type: product.type,
              title: 'POD Product',
              price: this.config.orchestrator.options?.tshirtPrice || 19.99,
              url: product.url,
              status: 'published'
            })
          }

          // Update job completion
          await this.db.updateJob(dbJob.id, {
            status: 'completed',
            completed_at: new Date(),
            result
          })
        }

        // Update worker status
        this.jobsProcessed++
        await this.db.updateWorker(this.workerId, {
          status: 'idle',
          current_job_id: undefined,
          jobs_processed: this.jobsProcessed
        })

        await this.recordLog(job.id, 'INFO', `Job completed successfully in ${result.totalTime}ms`)
        await this.recordMetric('job_duration', result.totalTime, { status: 'success' })

        callback(null, result)
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error)

        await this.recordLog(job.id, 'ERROR', `Job failed: ${errorMsg}`)

        // Update job failure
        const dbJob = await this.findDbJobByWorkerId(job.id)
        if (dbJob) {
          await this.db.updateJob(dbJob.id, {
            status: 'failed',
            error_message: errorMsg,
            completed_at: new Date()
          })
        }

        // Update worker status
        this.jobsFailed++
        await this.db.updateWorker(this.workerId, {
          status: 'idle',
          current_job_id: undefined,
          jobs_failed: this.jobsFailed
        })

        await this.recordMetric('job_duration', 0, { status: 'error' })

        callback(error)
      }
    })

    // Forward queue events
    this.queue.on('job:added', (job) => {
      this.emit('job:added', job)
      this.recordMetric('jobs_added', 1)
    })

    this.queue.on('job:started', (job) => {
      this.emit('job:started', job)
      this.recordMetric('jobs_started', 1)
    })

    this.queue.on('job:completed', (data) => {
      this.emit('job:completed', data)
      this.recordMetric('jobs_completed', 1)
    })

    this.queue.on('job:failed', (data) => {
      this.emit('job:failed', data)
      this.recordMetric('jobs_failed', 1)
    })

    this.queue.on('job:retry', (data) => {
      this.emit('job:retry', data)
      this.recordMetric('jobs_retried', 1)
    })

    this.queue.on('queue:update', (stats) => {
      this.emit('queue:update', stats)
    })
  }

  /**
   * Start heartbeat timer
   */
  private startHeartbeat(): void {
    const interval = this.config.engine.heartbeatInterval || 30000 // 30 seconds

    this.heartbeatTimer = setInterval(async () => {
      try {
        await this.db.updateWorkerHeartbeat(this.workerId)
        this.emit('heartbeat', { workerId: this.workerId, timestamp: new Date() })
      } catch (error) {
        console.error('[Engine] Heartbeat failed:', error)
      }
    }, interval)
  }

  /**
   * Record a log entry
   */
  private async recordLog(jobId: string, level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL', message: string): Promise<void> {
    try {
      const dbJob = await this.findDbJobByWorkerId(jobId)
      if (dbJob) {
        await this.db.addLog({
          job_id: dbJob.id,
          level,
          message,
          metadata: { workerId: this.workerId }
        })
      }
    } catch (error) {
      console.error('[Engine] Failed to record log:', error)
    }
  }

  /**
   * Record a metric
   */
  private async recordMetric(name: string, value: number, labels?: any): Promise<void> {
    try {
      await this.db.recordMetric({
        metric_type: 'engine',
        metric_name: name,
        metric_value: value,
        labels: { workerId: this.workerId, ...labels }
      })
    } catch (error) {
      console.error('[Engine] Failed to record metric:', error)
    }
  }

  /**
   * Find database job by worker/queue ID
   */
  private async findDbJobByWorkerId(workerId: string): Promise<Job | null> {
    const jobs = await this.db.listJobs()
    return jobs.find(j => j.worker_id === workerId) || null
  }
}

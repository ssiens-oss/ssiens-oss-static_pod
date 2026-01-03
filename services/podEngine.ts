/**
 * Production POD Engine
 * Full-featured production-ready engine for POD automation pipeline
 * Includes job queue, state management, monitoring, and error recovery
 */

import { Orchestrator } from './orchestrator'
import { EventEmitter } from 'events'
import * as fs from 'fs'
import * as path from 'path'

// Job status types
export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
export type JobPriority = 'low' | 'normal' | 'high' | 'urgent'

// Job definition
export interface Job {
  id: string
  type: 'generate' | 'batch' | 'custom'
  status: JobStatus
  priority: JobPriority
  request: any
  result?: any
  error?: string
  progress: number
  createdAt: number
  startedAt?: number
  completedAt?: number
  retryCount: number
  maxRetries: number
  logs: Array<{
    timestamp: number
    message: string
    type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR'
  }>
}

// Engine configuration
export interface PodEngineConfig {
  orchestrator: any
  queue: {
    maxConcurrent: number
    maxRetries: number
    retryDelay: number
    jobTimeout: number
  }
  persistence: {
    enabled: boolean
    path: string
    autoSave: boolean
    saveInterval: number
  }
  monitoring: {
    enabled: boolean
    metricsInterval: number
  }
}

// Engine metrics
export interface EngineMetrics {
  totalJobs: number
  completedJobs: number
  failedJobs: number
  runningJobs: number
  pendingJobs: number
  averageJobTime: number
  successRate: number
  uptime: number
  lastActivity: number
}

/**
 * Production POD Engine
 */
export class PodEngine extends EventEmitter {
  private orchestrator: Orchestrator
  private config: PodEngineConfig
  private jobs: Map<string, Job> = new Map()
  private queue: Job[] = []
  private running: Set<string> = new Set()
  private metrics: EngineMetrics
  private startTime: number
  private isRunning: boolean = false
  private saveInterval?: NodeJS.Timeout
  private metricsInterval?: NodeJS.Timeout

  constructor(config: PodEngineConfig) {
    super()
    this.config = config
    this.orchestrator = new Orchestrator(config.orchestrator)
    this.startTime = Date.now()

    // Initialize metrics
    this.metrics = {
      totalJobs: 0,
      completedJobs: 0,
      failedJobs: 0,
      runningJobs: 0,
      pendingJobs: 0,
      averageJobTime: 0,
      successRate: 0,
      uptime: 0,
      lastActivity: Date.now()
    }

    // Setup orchestrator logger
    this.orchestrator.setLogger((message: string, type: string) => {
      this.emit('log', { message, type, timestamp: Date.now() })
    })

    // Load persisted state if enabled
    if (this.config.persistence.enabled) {
      this.loadState()
    }
  }

  /**
   * Start the POD engine
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      throw new Error('Engine is already running')
    }

    this.isRunning = true
    this.emit('engine:start')

    // Start auto-save if enabled
    if (this.config.persistence.enabled && this.config.persistence.autoSave) {
      this.saveInterval = setInterval(() => {
        this.saveState()
      }, this.config.persistence.saveInterval)
    }

    // Start metrics collection
    if (this.config.monitoring.enabled) {
      this.metricsInterval = setInterval(() => {
        this.updateMetrics()
        this.emit('metrics:update', this.metrics)
      }, this.config.monitoring.metricsInterval)
    }

    // Process queue
    this.processQueue()

    console.log('🚀 POD Engine started')
  }

  /**
   * Stop the POD engine
   */
  async stop(): Promise<void> {
    if (!this.isRunning) {
      return
    }

    this.isRunning = false

    // Clear intervals
    if (this.saveInterval) {
      clearInterval(this.saveInterval)
    }
    if (this.metricsInterval) {
      clearInterval(this.metricsInterval)
    }

    // Save final state
    if (this.config.persistence.enabled) {
      await this.saveState()
    }

    this.emit('engine:stop')
    console.log('🛑 POD Engine stopped')
  }

  /**
   * Submit a new job to the queue
   */
  async submitJob(
    type: Job['type'],
    request: any,
    options?: { priority?: JobPriority; maxRetries?: number }
  ): Promise<string> {
    const job: Job = {
      id: this.generateJobId(),
      type,
      status: 'pending',
      priority: options?.priority || 'normal',
      request,
      progress: 0,
      createdAt: Date.now(),
      retryCount: 0,
      maxRetries: options?.maxRetries ?? this.config.queue.maxRetries,
      logs: []
    }

    this.jobs.set(job.id, job)
    this.queue.push(job)
    this.sortQueue()
    this.metrics.totalJobs++
    this.metrics.pendingJobs++

    this.emit('job:submitted', job)
    this.log(job.id, `Job ${job.id} submitted`, 'INFO')

    // Trigger queue processing
    if (this.isRunning) {
      this.processQueue()
    }

    return job.id
  }

  /**
   * Get job by ID
   */
  getJob(jobId: string): Job | undefined {
    return this.jobs.get(jobId)
  }

  /**
   * Get all jobs
   */
  getAllJobs(): Job[] {
    return Array.from(this.jobs.values())
  }

  /**
   * Get jobs by status
   */
  getJobsByStatus(status: JobStatus): Job[] {
    return Array.from(this.jobs.values()).filter(j => j.status === status)
  }

  /**
   * Cancel a job
   */
  async cancelJob(jobId: string): Promise<boolean> {
    const job = this.jobs.get(jobId)
    if (!job) {
      return false
    }

    if (job.status === 'running') {
      // Can't cancel running jobs in this simple implementation
      // In production, you'd need to implement cancellation tokens
      return false
    }

    if (job.status === 'pending') {
      job.status = 'cancelled'
      this.queue = this.queue.filter(j => j.id !== jobId)
      this.metrics.pendingJobs--
      this.emit('job:cancelled', job)
      this.log(jobId, 'Job cancelled', 'WARNING')
      return true
    }

    return false
  }

  /**
   * Retry a failed job
   */
  async retryJob(jobId: string): Promise<boolean> {
    const job = this.jobs.get(jobId)
    if (!job || job.status !== 'failed') {
      return false
    }

    job.status = 'pending'
    job.error = undefined
    job.progress = 0
    this.queue.push(job)
    this.sortQueue()
    this.metrics.failedJobs--
    this.metrics.pendingJobs++

    this.emit('job:retry', job)
    this.log(jobId, 'Job queued for retry', 'INFO')

    if (this.isRunning) {
      this.processQueue()
    }

    return true
  }

  /**
   * Get current metrics
   */
  getMetrics(): EngineMetrics {
    this.updateMetrics()
    return { ...this.metrics }
  }

  /**
   * Get engine health status
   */
  async getHealth(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy'
    uptime: number
    metrics: EngineMetrics
    services: any
  }> {
    const stats = await this.orchestrator.getStats()
    const metrics = this.getMetrics()

    let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy'

    // Check if ComfyUI is accessible
    if (!stats.services.comfyui) {
      status = 'degraded'
    }

    // Check if there are too many failed jobs
    if (metrics.failedJobs > metrics.completedJobs * 0.5) {
      status = 'unhealthy'
    }

    return {
      status,
      uptime: Date.now() - this.startTime,
      metrics,
      services: stats.services
    }
  }

  /**
   * Clear completed jobs older than specified age
   */
  clearOldJobs(maxAge: number = 24 * 60 * 60 * 1000): number {
    const now = Date.now()
    let cleared = 0

    for (const [id, job] of Array.from(this.jobs.entries())) {
      if (
        (job.status === 'completed' || job.status === 'failed' || job.status === 'cancelled') &&
        job.completedAt &&
        now - job.completedAt > maxAge
      ) {
        this.jobs.delete(id)
        cleared++
      }
    }

    if (cleared > 0) {
      this.emit('jobs:cleared', cleared)
      console.log(`🧹 Cleared ${cleared} old jobs`)
    }

    return cleared
  }

  /**
   * Process the job queue
   */
  private async processQueue(): Promise<void> {
    if (!this.isRunning) {
      return
    }

    // Check if we can run more jobs
    const maxConcurrent = this.config.queue.maxConcurrent
    if (this.running.size >= maxConcurrent) {
      return
    }

    // Get next job from queue
    const job = this.queue.shift()
    if (!job) {
      return
    }

    // Start job execution
    this.executeJob(job)

    // Continue processing if there are more jobs
    if (this.queue.length > 0 && this.running.size < maxConcurrent) {
      setImmediate(() => this.processQueue())
    }
  }

  /**
   * Execute a job
   */
  private async executeJob(job: Job): Promise<void> {
    this.running.add(job.id)
    job.status = 'running'
    job.startedAt = Date.now()
    this.metrics.pendingJobs--
    this.metrics.runningJobs++

    this.emit('job:started', job)
    this.log(job.id, `Job started (type: ${job.type})`, 'INFO')

    try {
      // Set timeout for job execution
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Job timeout')), this.config.queue.jobTimeout)
      })

      // Execute job with timeout
      const resultPromise = this.runJob(job)
      const result = await Promise.race([resultPromise, timeoutPromise])

      // Job completed successfully
      job.status = 'completed'
      job.completedAt = Date.now()
      job.result = result
      job.progress = 100
      this.metrics.runningJobs--
      this.metrics.completedJobs++

      this.emit('job:completed', job)
      this.log(job.id, 'Job completed successfully', 'SUCCESS')

    } catch (error) {
      // Job failed
      const errorMsg = error instanceof Error ? error.message : 'Unknown error'
      job.error = errorMsg
      this.log(job.id, `Job failed: ${errorMsg}`, 'ERROR')

      // Check if we should retry
      if (job.retryCount < job.maxRetries) {
        job.retryCount++
        job.status = 'pending'
        this.metrics.runningJobs--
        this.metrics.pendingJobs++

        // Add back to queue with delay
        setTimeout(() => {
          this.queue.push(job)
          this.sortQueue()
          this.log(job.id, `Retrying job (attempt ${job.retryCount}/${job.maxRetries})`, 'WARNING')
          this.emit('job:retry', job)
          this.processQueue()
        }, this.config.queue.retryDelay * job.retryCount)

      } else {
        // Max retries reached
        job.status = 'failed'
        job.completedAt = Date.now()
        this.metrics.runningJobs--
        this.metrics.failedJobs++
        this.emit('job:failed', job)
      }
    } finally {
      this.running.delete(job.id)
      this.metrics.lastActivity = Date.now()

      // Process next job
      if (this.isRunning) {
        setImmediate(() => this.processQueue())
      }
    }
  }

  /**
   * Run the actual job logic
   */
  private async runJob(job: Job): Promise<any> {
    switch (job.type) {
      case 'generate':
        return await this.orchestrator.run(job.request)

      case 'batch':
        return await this.runBatchJob(job)

      case 'custom':
        // Custom job logic can be implemented here
        throw new Error('Custom job type not implemented')

      default:
        throw new Error(`Unknown job type: ${job.type}`)
    }
  }

  /**
   * Run a batch job
   */
  private async runBatchJob(job: Job): Promise<any> {
    const { items } = job.request
    const results = []
    const errors = []

    for (let i = 0; i < items.length; i++) {
      try {
        const result = await this.orchestrator.run(items[i])
        results.push(result)

        // Update progress
        job.progress = Math.floor(((i + 1) / items.length) * 100)
        this.emit('job:progress', job)

      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Unknown error'
        errors.push({ index: i, error: errorMsg })
      }
    }

    return { results, errors, total: items.length }
  }

  /**
   * Log message for a job
   */
  private log(jobId: string, message: string, type: Job['logs'][0]['type']): void {
    const job = this.jobs.get(jobId)
    if (job) {
      job.logs.push({
        timestamp: Date.now(),
        message,
        type
      })
    }
  }

  /**
   * Sort queue by priority
   */
  private sortQueue(): void {
    const priorityOrder = { urgent: 0, high: 1, normal: 2, low: 3 }
    this.queue.sort((a, b) => {
      const diff = priorityOrder[a.priority] - priorityOrder[b.priority]
      if (diff !== 0) return diff
      return a.createdAt - b.createdAt
    })
  }

  /**
   * Generate unique job ID
   */
  private generateJobId(): string {
    return `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Update metrics
   */
  private updateMetrics(): void {
    this.metrics.uptime = Date.now() - this.startTime
    this.metrics.runningJobs = this.running.size
    this.metrics.pendingJobs = this.queue.length

    // Calculate average job time
    const allJobs = Array.from(this.jobs.values())
    const completedJobs = allJobs.filter(j => j.status === 'completed')
    if (completedJobs.length > 0) {
      const totalTime = completedJobs.reduce((sum, job) => {
        if (job.startedAt && job.completedAt) {
          return sum + (job.completedAt - job.startedAt)
        }
        return sum
      }, 0)
      this.metrics.averageJobTime = totalTime / completedJobs.length
    }

    // Calculate success rate
    const finishedJobs = this.metrics.completedJobs + this.metrics.failedJobs
    if (finishedJobs > 0) {
      this.metrics.successRate = (this.metrics.completedJobs / finishedJobs) * 100
    }
  }

  /**
   * Save state to disk
   */
  private async saveState(): Promise<void> {
    if (!this.config.persistence.enabled) {
      return
    }

    try {
      const statePath = this.config.persistence.path
      const stateDir = path.dirname(statePath)

      // Ensure directory exists
      if (!fs.existsSync(stateDir)) {
        fs.mkdirSync(stateDir, { recursive: true })
      }

      const state = {
        jobs: Array.from(this.jobs.entries()),
        metrics: this.metrics,
        savedAt: Date.now()
      }

      fs.writeFileSync(statePath, JSON.stringify(state, null, 2))
      this.emit('state:saved')

    } catch (error) {
      console.error('Failed to save state:', error)
      this.emit('state:save-error', error)
    }
  }

  /**
   * Load state from disk
   */
  private loadState(): void {
    try {
      const statePath = this.config.persistence.path

      if (!fs.existsSync(statePath)) {
        return
      }

      const data = fs.readFileSync(statePath, 'utf-8')
      const state = JSON.parse(data)

      // Restore jobs
      this.jobs = new Map(state.jobs)

      // Restore pending jobs to queue
      for (const job of Array.from(this.jobs.values())) {
        if (job.status === 'pending') {
          this.queue.push(job)
        } else if (job.status === 'running') {
          // Reset running jobs to pending
          job.status = 'pending'
          job.progress = 0
          this.queue.push(job)
        }
      }

      this.sortQueue()

      // Restore metrics
      if (state.metrics) {
        this.metrics = { ...this.metrics, ...state.metrics }
      }

      this.emit('state:loaded')
      console.log(`📂 Loaded state with ${this.jobs.size} jobs`)

    } catch (error) {
      console.error('Failed to load state:', error)
      this.emit('state:load-error', error)
    }
  }
}

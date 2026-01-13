/**
 * Production Job Queue System
 * Manages job queuing, processing, and retry logic using Redis/BullMQ patterns
 */

import { EventEmitter } from 'events'

export interface JobData {
  id: string
  priority: number
  request: {
    prompt?: string
    theme?: string
    style?: string
    niche?: string
    productTypes: ('tshirt' | 'hoodie')[]
    count?: number
    autoPublish?: boolean
  }
  retryCount: number
  maxRetries: number
  createdAt: Date
}

export interface JobResult {
  success: boolean
  generatedImages: Array<{
    id: string
    url: string
    prompt: string
  }>
  products: Array<{
    platform: string
    productId: string
    url: string
    type: string
  }>
  errors: string[]
  totalTime: number
}

export type JobStatus = 'pending' | 'queued' | 'processing' | 'completed' | 'failed' | 'retrying'

export interface QueueConfig {
  maxConcurrent: number
  retryDelay: number
  jobTimeout: number
  enableAutoRetry: boolean
}

/**
 * Priority queue implementation for job management
 */
class PriorityQueue<T> {
  private items: Array<{ priority: number; item: T }> = []

  enqueue(item: T, priority: number = 0): void {
    const entry = { priority, item }
    let added = false

    // Insert in priority order (higher priority first)
    for (let i = 0; i < this.items.length; i++) {
      if (priority > this.items[i].priority) {
        this.items.splice(i, 0, entry)
        added = true
        break
      }
    }

    if (!added) {
      this.items.push(entry)
    }
  }

  dequeue(): T | undefined {
    return this.items.shift()?.item
  }

  peek(): T | undefined {
    return this.items[0]?.item
  }

  size(): number {
    return this.items.length
  }

  isEmpty(): boolean {
    return this.items.length === 0
  }

  clear(): void {
    this.items = []
  }

  toArray(): T[] {
    return this.items.map(entry => entry.item)
  }
}

/**
 * Job Queue Manager
 * Handles job lifecycle, concurrency control, and retry logic
 */
export class JobQueue extends EventEmitter {
  private queue: PriorityQueue<JobData>
  private processing: Map<string, JobData>
  private completed: Map<string, JobResult>
  private failed: Map<string, { job: JobData; error: string }>
  private config: QueueConfig
  private isProcessing: boolean = false
  private activeWorkers: number = 0

  constructor(config: Partial<QueueConfig> = {}) {
    super()

    this.queue = new PriorityQueue<JobData>()
    this.processing = new Map()
    this.completed = new Map()
    this.failed = new Map()

    this.config = {
      maxConcurrent: config.maxConcurrent || 5,
      retryDelay: config.retryDelay || 60000, // 1 minute
      jobTimeout: config.jobTimeout || 3600000, // 1 hour
      enableAutoRetry: config.enableAutoRetry ?? true
    }
  }

  /**
   * Add a job to the queue
   */
  async addJob(
    request: JobData['request'],
    options: { priority?: number; maxRetries?: number } = {}
  ): Promise<string> {
    const job: JobData = {
      id: this.generateJobId(),
      priority: options.priority || 0,
      request,
      retryCount: 0,
      maxRetries: options.maxRetries || 3,
      createdAt: new Date()
    }

    this.queue.enqueue(job, job.priority)

    this.emit('job:added', job)
    this.emit('queue:update', this.getStats())

    // Start processing if not already running
    if (!this.isProcessing) {
      this.processQueue()
    }

    return job.id
  }

  /**
   * Process jobs from the queue
   */
  private async processQueue(): Promise<void> {
    if (this.isProcessing) return

    this.isProcessing = true

    while (!this.queue.isEmpty() || this.processing.size > 0) {
      // Process jobs while we have capacity
      while (this.activeWorkers < this.config.maxConcurrent && !this.queue.isEmpty()) {
        const job = this.queue.dequeue()
        if (job) {
          this.processJob(job)
        }
      }

      // Wait before checking again
      await this.sleep(1000)
    }

    this.isProcessing = false
  }

  /**
   * Process a single job
   */
  private async processJob(job: JobData): Promise<void> {
    this.activeWorkers++
    this.processing.set(job.id, job)

    this.emit('job:started', job)
    this.emit('queue:update', this.getStats())

    const timeout = setTimeout(() => {
      this.handleJobTimeout(job)
    }, this.config.jobTimeout)

    try {
      // Emit event for external processor to handle
      const result = await this.executeJob(job)

      clearTimeout(timeout)
      this.handleJobSuccess(job, result)
    } catch (error) {
      clearTimeout(timeout)
      this.handleJobError(job, error)
    } finally {
      this.activeWorkers--
      this.processing.delete(job.id)
    }
  }

  /**
   * Execute job - this emits an event for the engine to handle
   */
  private async executeJob(job: JobData): Promise<JobResult> {
    return new Promise((resolve, reject) => {
      // Set timeout for response
      const timeout = setTimeout(() => {
        reject(new Error('Job execution timeout'))
      }, this.config.jobTimeout)

      // Emit event with callback
      this.emit('job:execute', job, (error: Error | null, result?: JobResult) => {
        clearTimeout(timeout)
        if (error) {
          reject(error)
        } else {
          resolve(result!)
        }
      })
    })
  }

  /**
   * Handle successful job completion
   */
  private handleJobSuccess(job: JobData, result: JobResult): void {
    this.completed.set(job.id, result)
    this.emit('job:completed', { job, result })
    this.emit('queue:update', this.getStats())
  }

  /**
   * Handle job error
   */
  private handleJobError(job: JobData, error: any): void {
    const errorMessage = error instanceof Error ? error.message : String(error)

    // Check if we should retry
    if (this.config.enableAutoRetry && job.retryCount < job.maxRetries) {
      job.retryCount++

      this.emit('job:retry', { job, error: errorMessage, attempt: job.retryCount })

      // Re-queue with delay
      setTimeout(() => {
        this.queue.enqueue(job, job.priority)
        this.emit('queue:update', this.getStats())
      }, this.config.retryDelay)
    } else {
      // Max retries exceeded or auto-retry disabled
      this.failed.set(job.id, { job, error: errorMessage })
      this.emit('job:failed', { job, error: errorMessage })
      this.emit('queue:update', this.getStats())
    }
  }

  /**
   * Handle job timeout
   */
  private handleJobTimeout(job: JobData): void {
    this.handleJobError(job, new Error('Job execution timeout'))
  }

  /**
   * Get job status
   */
  getJobStatus(jobId: string): JobStatus | null {
    if (this.processing.has(jobId)) return 'processing'
    if (this.completed.has(jobId)) return 'completed'
    if (this.failed.has(jobId)) return 'failed'

    // Check if in queue
    const queuedJobs = this.queue.toArray()
    const inQueue = queuedJobs.find(j => j.id === jobId)
    if (inQueue) {
      return inQueue.retryCount > 0 ? 'retrying' : 'queued'
    }

    return null
  }

  /**
   * Get job result
   */
  getJobResult(jobId: string): JobResult | null {
    return this.completed.get(jobId) || null
  }

  /**
   * Get job error
   */
  getJobError(jobId: string): string | null {
    const failed = this.failed.get(jobId)
    return failed ? failed.error : null
  }

  /**
   * Get queue statistics
   */
  getStats(): {
    queued: number
    processing: number
    completed: number
    failed: number
    activeWorkers: number
    maxWorkers: number
  } {
    return {
      queued: this.queue.size(),
      processing: this.processing.size,
      completed: this.completed.size,
      failed: this.failed.size,
      activeWorkers: this.activeWorkers,
      maxWorkers: this.config.maxConcurrent
    }
  }

  /**
   * Get all jobs by status
   */
  getJobsByStatus(status: JobStatus): JobData[] {
    switch (status) {
      case 'queued':
      case 'retrying':
        return this.queue.toArray()
      case 'processing':
        return Array.from(this.processing.values())
      case 'completed':
        return Array.from(this.completed.keys()).map(id => {
          const job = this.findJob(id)
          return job!
        })
      case 'failed':
        return Array.from(this.failed.values()).map(f => f.job)
      default:
        return []
    }
  }

  /**
   * Find job by ID across all states
   */
  private findJob(jobId: string): JobData | null {
    // Check processing
    if (this.processing.has(jobId)) {
      return this.processing.get(jobId)!
    }

    // Check failed
    const failed = this.failed.get(jobId)
    if (failed) return failed.job

    // Check queue
    const queuedJobs = this.queue.toArray()
    const inQueue = queuedJobs.find(j => j.id === jobId)
    if (inQueue) return inQueue

    return null
  }

  /**
   * Cancel a job
   */
  cancelJob(jobId: string): boolean {
    // Can only cancel queued jobs
    const queuedJobs = this.queue.toArray()
    const jobIndex = queuedJobs.findIndex(j => j.id === jobId)

    if (jobIndex >= 0) {
      // Remove from queue (rebuild queue without this job)
      this.queue.clear()
      queuedJobs.forEach((job, i) => {
        if (i !== jobIndex) {
          this.queue.enqueue(job, job.priority)
        }
      })

      this.emit('job:cancelled', jobId)
      this.emit('queue:update', this.getStats())
      return true
    }

    return false
  }

  /**
   * Clear completed and failed jobs
   */
  clearHistory(): void {
    this.completed.clear()
    this.failed.clear()
    this.emit('queue:update', this.getStats())
  }

  /**
   * Shutdown queue gracefully
   */
  async shutdown(): Promise<void> {
    this.isProcessing = false

    // Wait for active jobs to complete (with timeout)
    const timeout = 30000 // 30 seconds
    const start = Date.now()

    while (this.processing.size > 0 && Date.now() - start < timeout) {
      await this.sleep(1000)
    }

    if (this.processing.size > 0) {
      console.warn(`Forcing shutdown with ${this.processing.size} jobs still processing`)
    }

    this.removeAllListeners()
  }

  /**
   * Generate unique job ID
   */
  private generateJobId(): string {
    return `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Sleep helper
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

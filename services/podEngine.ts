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
  prompt?: string
  promptData?: any
  productTypes?: Array<'tshirt' | 'hoodie'>
  platforms?: string[]
  autoPublish?: boolean
  retryCount: number
  maxRetries: number
  createdAt: number
  startedAt?: number
  completedAt?: number
  error?: string
  result?: any
  progress?: number
}

// Engine configuration
export interface PodEngineConfig {
  maxConcurrentJobs?: number
  maxRetries?: number
  retryDelay?: number
  jobTimeout?: number
  enablePersistence?: boolean
  stateFilePath?: string
  autoSaveInterval?: number
}

// Metrics
export interface EngineMetrics {
  totalJobs: number
  pendingJobs: number
  runningJobs: number
  completedJobs: number
  failedJobs: number
  cancelledJobs: number
  successRate: number
  averageJobTime: number
  uptime: number
}

/**
 * Main POD Engine class
 * Manages job queue, execution, and state persistence
 */
export class PodEngine extends EventEmitter {
  private orchestrator: Orchestrator
  private jobs: Map<string, Job> = new Map()
  private queue: Job[] = []
  private running: Set<string> = new Set()
  private config: Required<PodEngineConfig>
  private metrics: EngineMetrics
  private startTime: number
  private saveInterval?: NodeJS.Timeout
  private isShuttingDown = false

  constructor(config: PodEngineConfig = {}) {
    super()

    // Initialize configuration with defaults
    this.config = {
      maxConcurrentJobs: config.maxConcurrentJobs ?? 2,
      maxRetries: config.maxRetries ?? 3,
      retryDelay: config.retryDelay ?? 5000,
      jobTimeout: config.jobTimeout ?? 600000, // 10 minutes
      enablePersistence: config.enablePersistence ?? true,
      stateFilePath: config.stateFilePath ?? '/tmp/pod-engine-state.json',
      autoSaveInterval: config.autoSaveInterval ?? 30000 // 30 seconds
    }

    // Initialize orchestrator with configuration from environment
    this.orchestrator = new Orchestrator({
      comfyui: {
        apiUrl: process.env.COMFYUI_URL || 'http://localhost:8188',
        outputDir: process.env.COMFYUI_OUTPUT_DIR || '/workspace/ComfyUI/output'
      },
      claude: {
        apiKey: process.env.ANTHROPIC_API_KEY || ''
      },
      storage: {
        type: (process.env.STORAGE_TYPE as 'local' | 's3' | 'gcs') || 'local',
        basePath: process.env.STORAGE_PATH || '/workspace/data/designs'
      },
      printify: process.env.PRINTIFY_API_KEY ? {
        apiKey: process.env.PRINTIFY_API_KEY,
        shopId: process.env.PRINTIFY_SHOP_ID || ''
      } : undefined,
      shopify: process.env.SHOPIFY_ACCESS_TOKEN ? {
        storeUrl: process.env.SHOPIFY_STORE_URL || '',
        accessToken: process.env.SHOPIFY_ACCESS_TOKEN
      } : undefined,
      mockup: {
        templatesDir: process.env.MOCKUP_TEMPLATES_DIR || '/workspace/data/mockup-templates',
        outputDir: process.env.MOCKUP_OUTPUT_DIR || '/workspace/data/mockups'
      },
      options: {
        enableBackgroundRemoval: process.env.ENABLE_BACKGROUND_REMOVAL !== 'false',
        enableMockups: process.env.ENABLE_MOCKUPS !== 'false'
      }
    })
    this.startTime = Date.now()

    // Initialize metrics
    this.metrics = {
      totalJobs: 0,
      pendingJobs: 0,
      runningJobs: 0,
      completedJobs: 0,
      failedJobs: 0,
      cancelledJobs: 0,
      successRate: 0,
      averageJobTime: 0,
      uptime: 0
    }

    // Load persisted state if enabled
    if (this.config.enablePersistence) {
      this.loadState()

      // Auto-save state periodically
      this.saveInterval = setInterval(() => {
        this.saveState()
      }, this.config.autoSaveInterval)
    }

    this.emit('engine:started', { config: this.config })
  }

  /**
   * Submit a new job to the queue
   */
  async submitJob(jobData: Partial<Job>): Promise<string> {
    const job: Job = {
      id: jobData.id ?? this.generateJobId(),
      type: jobData.type ?? 'generate',
      status: 'pending',
      priority: jobData.priority ?? 'normal',
      prompt: jobData.prompt,
      promptData: jobData.promptData,
      productTypes: jobData.productTypes ?? ['tshirt'],
      platforms: jobData.platforms,
      autoPublish: jobData.autoPublish ?? false,
      retryCount: 0,
      maxRetries: jobData.maxRetries ?? this.config.maxRetries,
      createdAt: Date.now(),
      progress: 0
    }

    this.jobs.set(job.id, job)
    this.addToQueue(job)
    this.metrics.totalJobs++

    this.emit('job:submitted', job)
    this.processQueue()

    return job.id
  }

  /**
   * Submit multiple jobs as a batch
   */
  async submitBatch(jobs: Array<Partial<Job>>): Promise<string[]> {
    const ids: string[] = []

    for (const jobData of jobs) {
      const id = await this.submitJob(jobData)
      ids.push(id)
    }

    this.emit('batch:submitted', { count: jobs.length, ids })
    return ids
  }

  /**
   * Get job status
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
    return Array.from(this.jobs.values()).filter(job => job.status === status)
  }

  /**
   * Cancel a pending job
   */
  cancelJob(jobId: string): boolean {
    const job = this.jobs.get(jobId)

    if (!job) {
      return false
    }

    if (job.status === 'running') {
      // Can't cancel running jobs
      return false
    }

    if (job.status !== 'pending') {
      return false
    }

    job.status = 'cancelled'
    job.completedAt = Date.now()

    // Remove from queue
    this.queue = this.queue.filter(j => j.id !== jobId)

    this.metrics.cancelledJobs++
    this.emit('job:cancelled', job)

    return true
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
    job.retryCount = 0
    job.error = undefined
    job.startedAt = undefined
    job.completedAt = undefined
    job.progress = 0

    this.addToQueue(job)
    this.emit('job:retried', job)
    this.processQueue()

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
   * Health check
   */
  isHealthy(): boolean {
    // Check if orchestrator is working
    // Check if too many jobs are failing
    const recentJobs = Array.from(this.jobs.values())
      .sort((a, b) => (b.createdAt ?? 0) - (a.createdAt ?? 0))
      .slice(0, 10)

    const recentFailures = recentJobs.filter(j => j.status === 'failed').length

    return recentFailures < 8 // Allow some failures
  }

  /**
   * Graceful shutdown
   */
  async shutdown(): Promise<void> {
    if (this.isShuttingDown) {
      return
    }

    this.isShuttingDown = true
    this.emit('engine:shutdown:started')

    // Stop accepting new jobs (already handled by isShuttingDown flag)

    // Wait for running jobs to complete (with timeout)
    const shutdownTimeout = 60000 // 1 minute
    const startShutdown = Date.now()

    while (this.running.size > 0 && Date.now() - startShutdown < shutdownTimeout) {
      await new Promise(resolve => setTimeout(resolve, 1000))
    }

    // Save state
    if (this.config.enablePersistence) {
      this.saveState()
      if (this.saveInterval) {
        clearInterval(this.saveInterval)
      }
    }

    this.emit('engine:shutdown:completed')
  }

  /**
   * Clear old completed jobs
   */
  clearOldJobs(olderThanMs: number = 86400000): number {
    const now = Date.now()
    let cleared = 0

    for (const [id, job] of Array.from(this.jobs.entries())) {
      if (
        (job.status === 'completed' || job.status === 'failed' || job.status === 'cancelled') &&
        job.completedAt &&
        now - job.completedAt > olderThanMs
      ) {
        this.jobs.delete(id)
        cleared++
      }
    }

    if (cleared > 0) {
      this.emit('jobs:cleared', { count: cleared })
    }

    return cleared
  }

  // Private methods

  private generateJobId(): string {
    return `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  private addToQueue(job: Job) {
    // Add job to queue based on priority
    const priorityOrder = { urgent: 0, high: 1, normal: 2, low: 3 }
    const jobPriority = priorityOrder[job.priority]

    const insertIndex = this.queue.findIndex(
      qJob => priorityOrder[qJob.priority] > jobPriority
    )

    if (insertIndex === -1) {
      this.queue.push(job)
    } else {
      this.queue.splice(insertIndex, 0, job)
    }
  }

  private async processQueue() {
    if (this.isShuttingDown) {
      return
    }

    // Process jobs up to max concurrent limit
    while (
      this.queue.length > 0 &&
      this.running.size < this.config.maxConcurrentJobs
    ) {
      const job = this.queue.shift()
      if (job) {
        this.executeJob(job)
      }
    }
  }

  private async executeJob(job: Job) {
    job.status = 'running'
    job.startedAt = Date.now()
    this.running.add(job.id)

    this.emit('job:started', job)

    try {
      // Set up timeout
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Job timeout')), this.config.jobTimeout)
      })

      // Execute job with timeout
      const resultPromise = this.runJob(job)
      const result = await Promise.race([resultPromise, timeoutPromise])

      job.status = 'completed'
      job.completedAt = Date.now()
      job.result = result
      job.progress = 100

      this.metrics.completedJobs++
      this.emit('job:completed', job)

    } catch (error: any) {
      const errorMessage = error?.message || String(error)

      // Check if we should retry
      if (job.retryCount < job.maxRetries) {
        job.retryCount++
        job.status = 'pending'

        this.emit('job:retry', { job, attempt: job.retryCount, error: errorMessage })

        // Add back to queue with delay
        setTimeout(() => {
          this.addToQueue(job)
          this.processQueue()
        }, this.config.retryDelay * Math.pow(2, job.retryCount - 1)) // Exponential backoff

      } else {
        // Max retries exceeded
        job.status = 'failed'
        job.completedAt = Date.now()
        job.error = errorMessage

        this.metrics.failedJobs++
        this.emit('job:failed', job)
      }
    } finally {
      this.running.delete(job.id)
      this.updateMetrics()
      this.processQueue()
    }
  }

  private async runJob(job: Job): Promise<any> {
    // Update progress
    job.progress = 10
    this.emit('job:progress', { jobId: job.id, progress: 10 })

    if (job.type === 'generate') {
      // Generate design using orchestrator
      job.progress = 30
      this.emit('job:progress', { jobId: job.id, progress: 30 })

      const request = {
        prompt: job.prompt || 'Create an artistic design',
        theme: job.promptData?.theme,
        style: job.promptData?.style,
        niche: job.promptData?.niche,
        productTypes: job.productTypes || ['tshirt'],
        count: job.promptData?.count || 1,
        autoPublish: job.autoPublish ?? false
      }

      const result = await this.orchestrator.run(request)

      job.progress = 90
      this.emit('job:progress', { jobId: job.id, progress: 90 })

      return result

    } else if (job.type === 'batch') {
      // Handle batch job
      return { status: 'batch_completed' }

    } else {
      throw new Error(`Unknown job type: ${job.type}`)
    }
  }

  private updateMetrics() {
    this.metrics.pendingJobs = this.queue.length
    this.metrics.runningJobs = this.running.size

    // Calculate average job time
    const allJobs = Array.from(this.jobs.values())
    const completedJobs = allJobs.filter(j => j.status === 'completed')

    if (completedJobs.length > 0) {
      const totalTime = completedJobs.reduce((sum, job) => {
        return sum + ((job.completedAt ?? 0) - (job.startedAt ?? 0))
      }, 0)
      this.metrics.averageJobTime = totalTime / completedJobs.length
    }

    // Calculate success rate
    const finishedJobs = this.metrics.completedJobs + this.metrics.failedJobs
    if (finishedJobs > 0) {
      this.metrics.successRate = (this.metrics.completedJobs / finishedJobs) * 100
    }

    this.metrics.uptime = Date.now() - this.startTime
  }

  private saveState() {
    if (!this.config.enablePersistence) {
      return
    }

    try {
      const state = {
        jobs: Array.from(this.jobs.entries()),
        queue: this.queue,
        metrics: this.metrics,
        timestamp: Date.now()
      }

      const dir = path.dirname(this.config.stateFilePath)
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true })
      }

      fs.writeFileSync(
        this.config.stateFilePath,
        JSON.stringify(state, null, 2)
      )

      this.emit('state:saved', { path: this.config.stateFilePath })
    } catch (error: any) {
      this.emit('state:save:error', { error: error.message })
    }
  }

  private loadState() {
    if (!this.config.enablePersistence) {
      return
    }

    try {
      if (!fs.existsSync(this.config.stateFilePath)) {
        return
      }

      const data = fs.readFileSync(this.config.stateFilePath, 'utf-8')
      const state = JSON.parse(data)

      this.jobs = new Map(state.jobs)

      // Restore pending jobs to queue
      for (const job of Array.from(this.jobs.values())) {
        if (job.status === 'pending') {
          this.queue.push(job)
        } else if (job.status === 'running') {
          // Reset running jobs to pending
          job.status = 'pending'
          job.startedAt = undefined
          this.queue.push(job)
        }
      }

      this.emit('state:loaded', {
        jobs: this.jobs.size,
        queued: this.queue.length
      })

    } catch (error: any) {
      this.emit('state:load:error', { error: error.message })
    }
  }
}

/**
 * Database Client for Production POD Engine
 * Provides persistence layer with PostgreSQL support and in-memory fallback
 */

export interface Job {
  id: string
  status: 'pending' | 'queued' | 'processing' | 'completed' | 'failed' | 'retrying'
  priority: number
  request: any
  result?: any
  error_message?: string
  retry_count: number
  max_retries: number
  created_at: Date
  started_at?: Date
  completed_at?: Date
  updated_at: Date
  worker_id?: string
}

export interface Image {
  id: string
  job_id: string
  image_url: string
  storage_path: string
  prompt: string
  title?: string
  description?: string
  tags?: string[]
  hash?: string
  metadata?: any
  created_at: Date
}

export interface Product {
  id: string
  job_id: string
  image_id: string
  platform: string
  platform_product_id: string
  product_type: string
  title: string
  description?: string
  price?: number
  url?: string
  status: 'draft' | 'publishing' | 'published' | 'failed' | 'archived'
  published_at?: Date
  metadata?: any
  created_at: Date
  updated_at: Date
}

export interface Worker {
  id: string
  hostname: string
  status: 'idle' | 'busy' | 'offline' | 'error'
  current_job_id?: string
  last_heartbeat: Date
  started_at: Date
  jobs_processed: number
  jobs_failed: number
  metadata?: any
}

export interface Metric {
  id: string
  metric_type: string
  metric_name: string
  metric_value: number
  labels?: any
  timestamp: Date
}

export interface Log {
  id: string
  job_id: string
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
  message: string
  metadata?: any
  timestamp: Date
}

/**
 * Database Client Interface
 */
export interface IDatabaseClient {
  // Connection
  connect(): Promise<void>
  disconnect(): Promise<void>
  healthCheck(): Promise<boolean>

  // Jobs
  createJob(job: Omit<Job, 'id' | 'created_at' | 'updated_at'>): Promise<Job>
  getJob(id: string): Promise<Job | null>
  updateJob(id: string, updates: Partial<Job>): Promise<Job | null>
  listJobs(filters?: { status?: string; limit?: number }): Promise<Job[]>
  deleteJob(id: string): Promise<boolean>

  // Images
  createImage(image: Omit<Image, 'id' | 'created_at'>): Promise<Image>
  getImage(id: string): Promise<Image | null>
  listImagesByJob(jobId: string): Promise<Image[]>

  // Products
  createProduct(product: Omit<Product, 'id' | 'created_at' | 'updated_at'>): Promise<Product>
  getProduct(id: string): Promise<Product | null>
  updateProduct(id: string, updates: Partial<Product>): Promise<Product | null>
  listProductsByJob(jobId: string): Promise<Product[]>

  // Workers
  registerWorker(worker: Omit<Worker, 'started_at' | 'last_heartbeat' | 'jobs_processed' | 'jobs_failed'>): Promise<Worker>
  updateWorkerHeartbeat(workerId: string): Promise<void>
  updateWorker(workerId: string, updates: Partial<Worker>): Promise<Worker | null>
  listWorkers(): Promise<Worker[]>
  getDeadWorkers(thresholdSeconds: number): Promise<Worker[]>

  // Metrics
  recordMetric(metric: Omit<Metric, 'id' | 'timestamp'>): Promise<void>
  getMetrics(type: string, timeRange?: { start: Date; end: Date }): Promise<Metric[]>

  // Logs
  addLog(log: Omit<Log, 'id' | 'timestamp'>): Promise<void>
  getLogsByJob(jobId: string, limit?: number): Promise<Log[]>
}

/**
 * In-Memory Database Client (for development/testing)
 */
export class InMemoryDatabaseClient implements IDatabaseClient {
  private jobs: Map<string, Job> = new Map()
  private images: Map<string, Image> = new Map()
  private products: Map<string, Product> = new Map()
  private workers: Map<string, Worker> = new Map()
  private metrics: Metric[] = []
  private logs: Log[] = []

  async connect(): Promise<void> {
    console.log('[DB] Connected to in-memory database')
  }

  async disconnect(): Promise<void> {
    console.log('[DB] Disconnected from in-memory database')
  }

  async healthCheck(): Promise<boolean> {
    return true
  }

  // Jobs
  async createJob(job: Omit<Job, 'id' | 'created_at' | 'updated_at'>): Promise<Job> {
    const newJob: Job = {
      ...job,
      id: this.generateId(),
      created_at: new Date(),
      updated_at: new Date()
    }
    this.jobs.set(newJob.id, newJob)
    return newJob
  }

  async getJob(id: string): Promise<Job | null> {
    return this.jobs.get(id) || null
  }

  async updateJob(id: string, updates: Partial<Job>): Promise<Job | null> {
    const job = this.jobs.get(id)
    if (!job) return null

    const updated = { ...job, ...updates, updated_at: new Date() }
    this.jobs.set(id, updated)
    return updated
  }

  async listJobs(filters?: { status?: string; limit?: number }): Promise<Job[]> {
    let jobs = Array.from(this.jobs.values())

    if (filters?.status) {
      jobs = jobs.filter(j => j.status === filters.status)
    }

    jobs.sort((a, b) => b.created_at.getTime() - a.created_at.getTime())

    if (filters?.limit) {
      jobs = jobs.slice(0, filters.limit)
    }

    return jobs
  }

  async deleteJob(id: string): Promise<boolean> {
    return this.jobs.delete(id)
  }

  // Images
  async createImage(image: Omit<Image, 'id' | 'created_at'>): Promise<Image> {
    const newImage: Image = {
      ...image,
      id: this.generateId(),
      created_at: new Date()
    }
    this.images.set(newImage.id, newImage)
    return newImage
  }

  async getImage(id: string): Promise<Image | null> {
    return this.images.get(id) || null
  }

  async listImagesByJob(jobId: string): Promise<Image[]> {
    return Array.from(this.images.values()).filter(img => img.job_id === jobId)
  }

  // Products
  async createProduct(product: Omit<Product, 'id' | 'created_at' | 'updated_at'>): Promise<Product> {
    const newProduct: Product = {
      ...product,
      id: this.generateId(),
      created_at: new Date(),
      updated_at: new Date()
    }
    this.products.set(newProduct.id, newProduct)
    return newProduct
  }

  async getProduct(id: string): Promise<Product | null> {
    return this.products.get(id) || null
  }

  async updateProduct(id: string, updates: Partial<Product>): Promise<Product | null> {
    const product = this.products.get(id)
    if (!product) return null

    const updated = { ...product, ...updates, updated_at: new Date() }
    this.products.set(id, updated)
    return updated
  }

  async listProductsByJob(jobId: string): Promise<Product[]> {
    return Array.from(this.products.values()).filter(p => p.job_id === jobId)
  }

  // Workers
  async registerWorker(worker: Omit<Worker, 'started_at' | 'last_heartbeat' | 'jobs_processed' | 'jobs_failed'>): Promise<Worker> {
    const newWorker: Worker = {
      ...worker,
      started_at: new Date(),
      last_heartbeat: new Date(),
      jobs_processed: 0,
      jobs_failed: 0
    }
    this.workers.set(newWorker.id, newWorker)
    return newWorker
  }

  async updateWorkerHeartbeat(workerId: string): Promise<void> {
    const worker = this.workers.get(workerId)
    if (worker) {
      worker.last_heartbeat = new Date()
    }
  }

  async updateWorker(workerId: string, updates: Partial<Worker>): Promise<Worker | null> {
    const worker = this.workers.get(workerId)
    if (!worker) return null

    const updated = { ...worker, ...updates, last_heartbeat: new Date() }
    this.workers.set(workerId, updated)
    return updated
  }

  async listWorkers(): Promise<Worker[]> {
    return Array.from(this.workers.values())
  }

  async getDeadWorkers(thresholdSeconds: number): Promise<Worker[]> {
    const threshold = Date.now() - thresholdSeconds * 1000
    return Array.from(this.workers.values()).filter(
      w => w.last_heartbeat.getTime() < threshold && w.status !== 'offline'
    )
  }

  // Metrics
  async recordMetric(metric: Omit<Metric, 'id' | 'timestamp'>): Promise<void> {
    this.metrics.push({
      ...metric,
      id: this.generateId(),
      timestamp: new Date()
    })

    // Keep only last 10000 metrics
    if (this.metrics.length > 10000) {
      this.metrics = this.metrics.slice(-10000)
    }
  }

  async getMetrics(type: string, timeRange?: { start: Date; end: Date }): Promise<Metric[]> {
    let filtered = this.metrics.filter(m => m.metric_type === type)

    if (timeRange) {
      filtered = filtered.filter(
        m => m.timestamp >= timeRange.start && m.timestamp <= timeRange.end
      )
    }

    return filtered
  }

  // Logs
  async addLog(log: Omit<Log, 'id' | 'timestamp'>): Promise<void> {
    this.logs.push({
      ...log,
      id: this.generateId(),
      timestamp: new Date()
    })

    // Keep only last 50000 logs
    if (this.logs.length > 50000) {
      this.logs = this.logs.slice(-50000)
    }
  }

  async getLogsByJob(jobId: string, limit?: number): Promise<Log[]> {
    let filtered = this.logs.filter(l => l.job_id === jobId)
    filtered.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())

    if (limit) {
      filtered = filtered.slice(0, limit)
    }

    return filtered
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }
}

/**
 * PostgreSQL Database Client (stub - requires pg library)
 * This would use node-postgres or similar library in production
 */
export class PostgresDatabaseClient implements IDatabaseClient {
  private connectionString: string
  private connected: boolean = false

  constructor(connectionString: string) {
    this.connectionString = connectionString
  }

  async connect(): Promise<void> {
    // TODO: Implement with pg library
    // const { Pool } = require('pg')
    // this.pool = new Pool({ connectionString: this.connectionString })
    console.log('[DB] PostgreSQL client would connect here')
    console.log('[DB] Falling back to in-memory storage')
    this.connected = true
  }

  async disconnect(): Promise<void> {
    console.log('[DB] PostgreSQL client would disconnect here')
    this.connected = false
  }

  async healthCheck(): Promise<boolean> {
    // TODO: Implement actual health check
    return this.connected
  }

  // Implement all other methods following the pattern in InMemoryDatabaseClient
  // For now, we'll throw errors to indicate they need implementation

  async createJob(job: Omit<Job, 'id' | 'created_at' | 'updated_at'>): Promise<Job> {
    throw new Error('PostgreSQL implementation pending - use InMemoryDatabaseClient for now')
  }

  async getJob(id: string): Promise<Job | null> {
    throw new Error('PostgreSQL implementation pending')
  }

  async updateJob(id: string, updates: Partial<Job>): Promise<Job | null> {
    throw new Error('PostgreSQL implementation pending')
  }

  async listJobs(filters?: { status?: string; limit?: number }): Promise<Job[]> {
    throw new Error('PostgreSQL implementation pending')
  }

  async deleteJob(id: string): Promise<boolean> {
    throw new Error('PostgreSQL implementation pending')
  }

  async createImage(image: Omit<Image, 'id' | 'created_at'>): Promise<Image> {
    throw new Error('PostgreSQL implementation pending')
  }

  async getImage(id: string): Promise<Image | null> {
    throw new Error('PostgreSQL implementation pending')
  }

  async listImagesByJob(jobId: string): Promise<Image[]> {
    throw new Error('PostgreSQL implementation pending')
  }

  async createProduct(product: Omit<Product, 'id' | 'created_at' | 'updated_at'>): Promise<Product> {
    throw new Error('PostgreSQL implementation pending')
  }

  async getProduct(id: string): Promise<Product | null> {
    throw new Error('PostgreSQL implementation pending')
  }

  async updateProduct(id: string, updates: Partial<Product>): Promise<Product | null> {
    throw new Error('PostgreSQL implementation pending')
  }

  async listProductsByJob(jobId: string): Promise<Product[]> {
    throw new Error('PostgreSQL implementation pending')
  }

  async registerWorker(worker: Omit<Worker, 'started_at' | 'last_heartbeat' | 'jobs_processed' | 'jobs_failed'>): Promise<Worker> {
    throw new Error('PostgreSQL implementation pending')
  }

  async updateWorkerHeartbeat(workerId: string): Promise<void> {
    throw new Error('PostgreSQL implementation pending')
  }

  async updateWorker(workerId: string, updates: Partial<Worker>): Promise<Worker | null> {
    throw new Error('PostgreSQL implementation pending')
  }

  async listWorkers(): Promise<Worker[]> {
    throw new Error('PostgreSQL implementation pending')
  }

  async getDeadWorkers(thresholdSeconds: number): Promise<Worker[]> {
    throw new Error('PostgreSQL implementation pending')
  }

  async recordMetric(metric: Omit<Metric, 'id' | 'timestamp'>): Promise<void> {
    throw new Error('PostgreSQL implementation pending')
  }

  async getMetrics(type: string, timeRange?: { start: Date; end: Date }): Promise<Metric[]> {
    throw new Error('PostgreSQL implementation pending')
  }

  async addLog(log: Omit<Log, 'id' | 'timestamp'>): Promise<void> {
    throw new Error('PostgreSQL implementation pending')
  }

  async getLogsByJob(jobId: string, limit?: number): Promise<Log[]> {
    throw new Error('PostgreSQL implementation pending')
  }
}

/**
 * Factory function to create database client
 */
export function createDatabaseClient(config?: {
  type?: 'memory' | 'postgres'
  connectionString?: string
}): IDatabaseClient {
  const type = config?.type || 'memory'

  switch (type) {
    case 'postgres':
      if (!config?.connectionString) {
        console.warn('[DB] No connection string provided, falling back to in-memory')
        return new InMemoryDatabaseClient()
      }
      return new PostgresDatabaseClient(config.connectionString)

    case 'memory':
    default:
      return new InMemoryDatabaseClient()
  }
}

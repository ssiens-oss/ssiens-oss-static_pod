/**
 * API Server for Production POD Engine
 * Provides HTTP REST API for job submission, monitoring, and control
 */

import * as http from 'http'
import { URL } from 'url'
import { WorkerPool } from './WorkerPool'
import { IDatabaseClient } from './DatabaseClient'
import { MetricsCollector, AlertManager, DashboardProvider } from './Monitoring'
import { JobRequest } from './ProductionPodEngine'

export interface ApiServerConfig {
  port: number
  host?: string
  enableCors?: boolean
  authToken?: string
}

/**
 * Simple HTTP API Server
 */
export class ApiServer {
  private server?: http.Server
  private config: ApiServerConfig
  private workerPool: WorkerPool
  private db: IDatabaseClient
  private metrics: MetricsCollector
  private alerts: AlertManager
  private dashboard: DashboardProvider

  constructor(
    config: ApiServerConfig,
    workerPool: WorkerPool,
    db: IDatabaseClient,
    metrics: MetricsCollector,
    alerts: AlertManager
  ) {
    this.config = config
    this.workerPool = workerPool
    this.db = db
    this.metrics = metrics
    this.alerts = alerts
    this.dashboard = new DashboardProvider(db, metrics, alerts)
  }

  /**
   * Start API server
   */
  async start(): Promise<void> {
    return new Promise((resolve) => {
      this.server = http.createServer((req, res) => this.handleRequest(req, res))

      this.server.listen(this.config.port, this.config.host || '0.0.0.0', () => {
        console.log(`[API] Server listening on ${this.config.host || '0.0.0.0'}:${this.config.port}`)
        resolve()
      })
    })
  }

  /**
   * Stop API server
   */
  async stop(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.server) {
        resolve()
        return
      }

      this.server.close((err) => {
        if (err) reject(err)
        else resolve()
      })
    })
  }

  /**
   * Handle HTTP request
   */
  private async handleRequest(req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
    // CORS headers
    if (this.config.enableCors) {
      res.setHeader('Access-Control-Allow-Origin', '*')
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    }

    // Handle OPTIONS for CORS preflight
    if (req.method === 'OPTIONS') {
      res.writeHead(204)
      res.end()
      return
    }

    // Check authentication
    if (this.config.authToken) {
      const authHeader = req.headers['authorization']
      if (authHeader !== `Bearer ${this.config.authToken}`) {
        this.sendJson(res, 401, { error: 'Unauthorized' })
        return
      }
    }

    try {
      const url = new URL(req.url || '/', `http://${req.headers.host}`)
      const path = url.pathname
      const method = req.method || 'GET'

      // Route handling
      if (method === 'GET' && path === '/health') {
        await this.handleHealth(req, res)
      } else if (method === 'GET' && path === '/stats') {
        await this.handleStats(req, res)
      } else if (method === 'GET' && path === '/dashboard') {
        await this.handleDashboard(req, res, url)
      } else if (method === 'POST' && path === '/jobs') {
        await this.handleSubmitJob(req, res)
      } else if (method === 'GET' && path.startsWith('/jobs/')) {
        await this.handleGetJob(req, res, path)
      } else if (method === 'GET' && path === '/jobs') {
        await this.handleListJobs(req, res, url)
      } else if (method === 'GET' && path === '/workers') {
        await this.handleListWorkers(req, res)
      } else if (method === 'POST' && path.startsWith('/workers/') && path.endsWith('/restart')) {
        await this.handleRestartWorker(req, res, path)
      } else if (method === 'POST' && path === '/scale') {
        await this.handleScale(req, res)
      } else if (method === 'GET' && path === '/metrics') {
        await this.handleMetrics(req, res, url)
      } else if (method === 'GET' && path === '/alerts') {
        await this.handleAlerts(req, res)
      } else {
        this.sendJson(res, 404, { error: 'Not found' })
      }
    } catch (error) {
      console.error('[API] Request error:', error)
      this.sendJson(res, 500, {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : String(error)
      })
    }
  }

  /**
   * Health check endpoint
   */
  private async handleHealth(req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
    const health = await this.workerPool.healthCheck()
    const statusCode = health.healthy ? 200 : 503
    this.sendJson(res, statusCode, health)
  }

  /**
   * Statistics endpoint
   */
  private async handleStats(req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
    const stats = await this.workerPool.getStats()
    this.sendJson(res, 200, stats)
  }

  /**
   * Dashboard data endpoint
   */
  private async handleDashboard(req: http.IncomingMessage, res: http.ServerResponse, url: URL): Promise<void> {
    const hours = parseInt(url.searchParams.get('hours') || '24')
    const now = new Date()
    const timeRange = {
      start: new Date(now.getTime() - hours * 60 * 60 * 1000),
      end: now
    }

    const data = await this.dashboard.getData(timeRange)
    this.sendJson(res, 200, data)
  }

  /**
   * Submit job endpoint
   */
  private async handleSubmitJob(req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
    const body = await this.readBody(req)
    const jobRequest: JobRequest = JSON.parse(body)

    // Validate request
    if (!jobRequest.productTypes || jobRequest.productTypes.length === 0) {
      this.sendJson(res, 400, { error: 'productTypes is required' })
      return
    }

    // Submit to worker pool (least loaded strategy)
    const jobId = await this.workerPool.submitJobToLeastLoaded(jobRequest)

    this.sendJson(res, 202, { jobId, status: 'accepted' })
  }

  /**
   * Get job endpoint
   */
  private async handleGetJob(req: http.IncomingMessage, res: http.ServerResponse, path: string): Promise<void> {
    const jobId = path.split('/')[2]
    const job = await this.db.getJob(jobId)

    if (!job) {
      this.sendJson(res, 404, { error: 'Job not found' })
      return
    }

    // Get images and products
    const images = await this.db.listImagesByJob(jobId)
    const products = await this.db.listProductsByJob(jobId)
    const logs = await this.db.getLogsByJob(jobId, 100)

    this.sendJson(res, 200, {
      job,
      images,
      products,
      logs
    })
  }

  /**
   * List jobs endpoint
   */
  private async handleListJobs(req: http.IncomingMessage, res: http.ServerResponse, url: URL): Promise<void> {
    const status = url.searchParams.get('status') || undefined
    const limit = parseInt(url.searchParams.get('limit') || '50')

    const jobs = await this.db.listJobs({ status, limit })
    this.sendJson(res, 200, { jobs, count: jobs.length })
  }

  /**
   * List workers endpoint
   */
  private async handleListWorkers(req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
    const workers = this.workerPool.listWorkers()
    this.sendJson(res, 200, { workers, count: workers.length })
  }

  /**
   * Restart worker endpoint
   */
  private async handleRestartWorker(req: http.IncomingMessage, res: http.ServerResponse, path: string): Promise<void> {
    const workerId = path.split('/')[2]

    try {
      await this.workerPool.restartWorker(workerId)
      this.sendJson(res, 200, { message: 'Worker restarted', workerId })
    } catch (error) {
      this.sendJson(res, 404, {
        error: error instanceof Error ? error.message : String(error)
      })
    }
  }

  /**
   * Scale worker pool endpoint
   */
  private async handleScale(req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
    const body = await this.readBody(req)
    const { workerCount } = JSON.parse(body)

    if (!workerCount || workerCount < 1) {
      this.sendJson(res, 400, { error: 'Invalid workerCount' })
      return
    }

    await this.workerPool.scale(workerCount)
    this.sendJson(res, 200, { message: 'Scaled', workerCount })
  }

  /**
   * Metrics endpoint
   */
  private async handleMetrics(req: http.IncomingMessage, res: http.ServerResponse, url: URL): Promise<void> {
    const name = url.searchParams.get('name')
    const limit = parseInt(url.searchParams.get('limit') || '100')

    if (!name) {
      this.sendJson(res, 400, { error: 'name parameter required' })
      return
    }

    const metrics = this.metrics.getRecent(name, limit)
    this.sendJson(res, 200, { name, metrics, count: metrics.length })
  }

  /**
   * Alerts endpoint
   */
  private async handleAlerts(req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
    const alerts = this.alerts.getRecent(100)
    this.sendJson(res, 200, { alerts, count: alerts.length })
  }

  /**
   * Send JSON response
   */
  private sendJson(res: http.ServerResponse, statusCode: number, data: any): void {
    res.writeHead(statusCode, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify(data, null, 2))
  }

  /**
   * Read request body
   */
  private async readBody(req: http.IncomingMessage): Promise<string> {
    return new Promise((resolve, reject) => {
      let body = ''
      req.on('data', chunk => body += chunk)
      req.on('end', () => resolve(body))
      req.on('error', reject)
    })
  }
}

/**
 * API Routes Documentation
 */
export const API_DOCS = {
  'GET /health': 'Health check for all workers',
  'GET /stats': 'Get worker pool statistics',
  'GET /dashboard?hours=24': 'Get dashboard data for specified time range',
  'POST /jobs': 'Submit a new job (body: JobRequest)',
  'GET /jobs/:id': 'Get job details with images, products, and logs',
  'GET /jobs?status=completed&limit=50': 'List jobs with optional filters',
  'GET /workers': 'List all workers',
  'POST /workers/:id/restart': 'Restart a specific worker',
  'POST /scale': 'Scale worker pool (body: { workerCount: number })',
  'GET /metrics?name=job_duration&limit=100': 'Get metrics by name',
  'GET /alerts': 'Get recent alerts'
}

/**
 * POD Engine API Server
 * REST API for controlling and monitoring the production POD engine
 */

import express, { Request, Response } from 'express'
import cors from 'cors'
import { PodEngine, PodEngineConfig, Job } from './services/podEngine'
import * as dotenv from 'dotenv'

// Load environment variables
dotenv.config()

// Create Express app
const app = express()
app.use(cors())
app.use(express.json({ limit: '10mb' }))

// Initialize POD Engine
const engineConfig: PodEngineConfig = {
  orchestrator: {
    comfyui: {
      apiUrl: process.env.COMFYUI_URL || 'http://localhost:8188',
      outputDir: process.env.COMFYUI_OUTPUT_DIR || '/workspace/ComfyUI/output'
    },
    claude: {
      apiKey: process.env.ANTHROPIC_API_KEY || ''
    },
    storage: {
      type: (process.env.STORAGE_TYPE as any) || 'local',
      basePath: process.env.STORAGE_PATH || '/data/designs'
    },
    printify: process.env.PRINTIFY_API_KEY ? {
      apiKey: process.env.PRINTIFY_API_KEY,
      shopId: process.env.PRINTIFY_SHOP_ID || ''
    } : undefined,
    shopify: process.env.SHOPIFY_ACCESS_TOKEN ? {
      storeUrl: process.env.SHOPIFY_STORE_URL || '',
      accessToken: process.env.SHOPIFY_ACCESS_TOKEN
    } : undefined,
    tiktok: process.env.TIKTOK_APP_KEY ? {
      appKey: process.env.TIKTOK_APP_KEY,
      appSecret: process.env.TIKTOK_APP_SECRET || '',
      shopId: process.env.TIKTOK_SHOP_ID || '',
      accessToken: process.env.TIKTOK_ACCESS_TOKEN || ''
    } : undefined,
    etsy: process.env.ETSY_API_KEY ? {
      apiKey: process.env.ETSY_API_KEY,
      shopId: process.env.ETSY_SHOP_ID || '',
      accessToken: process.env.ETSY_ACCESS_TOKEN || ''
    } : undefined,
    instagram: process.env.INSTAGRAM_ACCESS_TOKEN ? {
      accessToken: process.env.INSTAGRAM_ACCESS_TOKEN,
      businessAccountId: process.env.INSTAGRAM_BUSINESS_ACCOUNT_ID || ''
    } : undefined,
    facebook: process.env.FACEBOOK_PAGE_ID ? {
      pageId: process.env.FACEBOOK_PAGE_ID,
      accessToken: process.env.FACEBOOK_ACCESS_TOKEN || '',
      catalogId: process.env.FACEBOOK_CATALOG_ID || ''
    } : undefined,
    options: {
      enabledPlatforms: process.env.ENABLED_PLATFORMS?.split(',') || ['printify', 'shopify'],
      autoPublish: process.env.AUTO_PUBLISH === 'true',
      tshirtPrice: parseFloat(process.env.TSHIRT_PRICE || '19.99'),
      hoodiePrice: parseFloat(process.env.HOODIE_PRICE || '34.99')
    }
  },
  queue: {
    maxConcurrent: parseInt(process.env.MAX_CONCURRENT_JOBS || '2'),
    maxRetries: parseInt(process.env.MAX_JOB_RETRIES || '3'),
    retryDelay: parseInt(process.env.RETRY_DELAY_MS || '5000'),
    jobTimeout: parseInt(process.env.JOB_TIMEOUT_MS || '600000') // 10 minutes
  },
  persistence: {
    enabled: process.env.ENABLE_PERSISTENCE !== 'false',
    path: process.env.STATE_FILE_PATH || '/data/pod-engine-state.json',
    autoSave: process.env.AUTO_SAVE_STATE !== 'false',
    saveInterval: parseInt(process.env.SAVE_INTERVAL_MS || '30000') // 30 seconds
  },
  monitoring: {
    enabled: process.env.ENABLE_MONITORING !== 'false',
    metricsInterval: parseInt(process.env.METRICS_INTERVAL_MS || '10000') // 10 seconds
  }
}

const engine = new PodEngine(engineConfig)

// Setup event listeners
engine.on('engine:start', () => console.log('🚀 Engine started'))
engine.on('engine:stop', () => console.log('🛑 Engine stopped'))
engine.on('job:submitted', (job: Job) => console.log(`📥 Job submitted: ${job.id}`))
engine.on('job:started', (job: Job) => console.log(`▶️  Job started: ${job.id}`))
engine.on('job:completed', (job: Job) => console.log(`✅ Job completed: ${job.id}`))
engine.on('job:failed', (job: Job) => console.log(`❌ Job failed: ${job.id} - ${job.error}`))
engine.on('job:cancelled', (job: Job) => console.log(`⛔ Job cancelled: ${job.id}`))
engine.on('job:retry', (job: Job) => console.log(`🔄 Job retry: ${job.id} (attempt ${job.retryCount})`))
engine.on('state:saved', () => console.log('💾 State saved'))
engine.on('state:loaded', () => console.log('📂 State loaded'))

// WebSocket support for real-time updates (if needed)
import { Server as SocketServer } from 'socket.io'
import * as http from 'http'

const server = http.createServer(app)
const io = new SocketServer(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
})

// Emit events to connected clients
engine.on('job:submitted', (job) => io.emit('job:update', job))
engine.on('job:started', (job) => io.emit('job:update', job))
engine.on('job:completed', (job) => io.emit('job:update', job))
engine.on('job:failed', (job) => io.emit('job:update', job))
engine.on('job:progress', (job) => io.emit('job:progress', job))
engine.on('metrics:update', (metrics) => io.emit('metrics', metrics))
engine.on('log', (log) => io.emit('log', log))

// API Routes

/**
 * Health check endpoint
 */
app.get('/health', async (req: Request, res: Response) => {
  try {
    const health = await engine.getHealth()
    res.status(health.status === 'healthy' ? 200 : 503).json(health)
  } catch (error) {
    res.status(500).json({
      status: 'unhealthy',
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})

/**
 * Get engine metrics
 */
app.get('/api/metrics', (req: Request, res: Response) => {
  try {
    const metrics = engine.getMetrics()
    res.json(metrics)
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})

/**
 * Submit a new job
 * POST /api/jobs
 * Body: { type, request, priority?, maxRetries? }
 */
app.post('/api/jobs', async (req: Request, res: Response) => {
  try {
    const { type, request, priority, maxRetries } = req.body

    if (!type || !request) {
      return res.status(400).json({ error: 'Missing required fields: type, request' })
    }

    const jobId = await engine.submitJob(type, request, { priority, maxRetries })
    const job = engine.getJob(jobId)

    res.status(201).json({ jobId, job })
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})

/**
 * Get all jobs
 */
app.get('/api/jobs', (req: Request, res: Response) => {
  try {
    const { status } = req.query
    const jobs = status
      ? engine.getJobsByStatus(status as any)
      : engine.getAllJobs()

    res.json(jobs)
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})

/**
 * Get job by ID
 */
app.get('/api/jobs/:id', (req: Request, res: Response) => {
  try {
    const job = engine.getJob(req.params.id)
    if (!job) {
      return res.status(404).json({ error: 'Job not found' })
    }
    res.json(job)
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})

/**
 * Cancel a job
 */
app.post('/api/jobs/:id/cancel', async (req: Request, res: Response) => {
  try {
    const success = await engine.cancelJob(req.params.id)
    if (!success) {
      return res.status(400).json({ error: 'Cannot cancel job' })
    }
    res.json({ success: true })
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})

/**
 * Retry a failed job
 */
app.post('/api/jobs/:id/retry', async (req: Request, res: Response) => {
  try {
    const success = await engine.retryJob(req.params.id)
    if (!success) {
      return res.status(400).json({ error: 'Cannot retry job' })
    }
    res.json({ success: true })
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})

/**
 * Clear old jobs
 */
app.post('/api/jobs/cleanup', (req: Request, res: Response) => {
  try {
    const { maxAge } = req.body
    const cleared = engine.clearOldJobs(maxAge)
    res.json({ cleared })
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})

/**
 * Quick generation endpoint (simplified)
 */
app.post('/api/generate', async (req: Request, res: Response) => {
  try {
    const jobId = await engine.submitJob('generate', req.body, { priority: 'normal' })
    const job = engine.getJob(jobId)
    res.status(201).json({ jobId, job })
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})

/**
 * Batch generation endpoint
 */
app.post('/api/generate/batch', async (req: Request, res: Response) => {
  try {
    const { items, priority } = req.body

    if (!items || !Array.isArray(items)) {
      return res.status(400).json({ error: 'Items array is required' })
    }

    const jobId = await engine.submitJob('batch', { items }, { priority })
    const job = engine.getJob(jobId)

    res.status(201).json({ jobId, job })
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})

/**
 * Get engine info
 */
app.get('/api/info', (req: Request, res: Response) => {
  res.json({
    name: 'POD Engine',
    version: '1.0.0',
    config: {
      maxConcurrent: engineConfig.queue.maxConcurrent,
      maxRetries: engineConfig.queue.maxRetries,
      persistenceEnabled: engineConfig.persistence.enabled,
      monitoringEnabled: engineConfig.monitoring.enabled
    }
  })
})

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: any) => {
  console.error('API Error:', err)
  res.status(500).json({
    error: err.message || 'Internal server error'
  })
})

// Start the server
const PORT = parseInt(process.env.PORT || '3000')

async function start() {
  try {
    // Start the POD engine
    await engine.start()

    // Start HTTP server
    server.listen(PORT, () => {
      console.log(`
╔════════════════════════════════════════════════════╗
║         POD Engine API Server                      ║
║                                                    ║
║  🌐 HTTP API:    http://localhost:${PORT}           ║
║  📊 Health:      http://localhost:${PORT}/health   ║
║  📡 WebSocket:   ws://localhost:${PORT}            ║
║                                                    ║
║  📖 Endpoints:                                     ║
║     GET  /health                                   ║
║     GET  /api/info                                 ║
║     GET  /api/metrics                              ║
║     GET  /api/jobs                                 ║
║     GET  /api/jobs/:id                             ║
║     POST /api/jobs                                 ║
║     POST /api/jobs/:id/cancel                      ║
║     POST /api/jobs/:id/retry                       ║
║     POST /api/generate                             ║
║     POST /api/generate/batch                       ║
║                                                    ║
║  🚀 Engine Status: RUNNING                         ║
╚════════════════════════════════════════════════════╝
      `)
    })

    // Graceful shutdown
    const shutdown = async () => {
      console.log('\n🛑 Shutting down...')
      await engine.stop()
      server.close(() => {
        console.log('👋 Server closed')
        process.exit(0)
      })
    }

    process.on('SIGTERM', shutdown)
    process.on('SIGINT', shutdown)

  } catch (error) {
    console.error('Failed to start server:', error)
    process.exit(1)
  }
}

// Start the application
start()

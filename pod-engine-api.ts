/**
 * POD Engine API Server
 * REST API for controlling and monitoring the production POD engine
 */

import express, { Request, Response } from 'express'
import cors from 'cors'
import { PodEngine, PodEngineConfig, Job } from './services/podEngine'
import dotenv from 'dotenv'
import http from 'http'

// Load environment variables
dotenv.config()

// Create Express app
const app = express()
app.use(cors())
app.use(express.json({ limit: '10mb' }))

// Initialize POD Engine
const engineConfig: PodEngineConfig = {
  maxConcurrentJobs: parseInt(process.env.MAX_CONCURRENT_JOBS || '2'),
  maxRetries: parseInt(process.env.MAX_JOB_RETRIES || '3'),
  retryDelay: parseInt(process.env.RETRY_DELAY_MS || '5000'),
  jobTimeout: parseInt(process.env.JOB_TIMEOUT_MS || '600000'),
  enablePersistence: process.env.ENABLE_PERSISTENCE === 'true',
  stateFilePath: process.env.STATE_FILE_PATH || '/tmp/pod-engine-state.json',
  autoSaveInterval: parseInt(process.env.SAVE_INTERVAL_MS || '30000')
}

const engine = new PodEngine(engineConfig)

// Event listeners for logging
engine.on('engine:started', (data) => {
  console.log('🚀 POD Engine started', data)
})

engine.on('job:submitted', (job) => {
  console.log(`📝 Job submitted: ${job.id}`)
})

engine.on('job:started', (job) => {
  console.log(`▶️  Job started: ${job.id}`)
})

engine.on('job:completed', (job) => {
  console.log(`✅ Job completed: ${job.id}`)
})

engine.on('job:failed', (job) => {
  console.error(`❌ Job failed: ${job.id} - ${job.error}`)
})

engine.on('job:retry', (data) => {
  console.log(`🔄 Job retry: ${data.job.id} (attempt ${data.attempt})`)
})

engine.on('job:progress', (data) => {
  console.log(`📊 Job progress: ${data.jobId} - ${data.progress}%`)
})

// API Routes

// Health check
app.get('/health', (req: Request, res: Response) => {
  const healthy = engine.isHealthy()
  const metrics = engine.getMetrics()

  res.status(healthy ? 200 : 503).json({
    status: healthy ? 'healthy' : 'unhealthy',
    uptime: metrics.uptime,
    timestamp: new Date().toISOString()
  })
})

// Get metrics
app.get('/api/metrics', (req: Request, res: Response) => {
  const metrics = engine.getMetrics()
  res.json(metrics)
})

// Get all jobs
app.get('/api/jobs', (req: Request, res: Response) => {
  const { status, limit } = req.query

  let jobs = engine.getAllJobs()

  if (status) {
    jobs = engine.getJobsByStatus(status as any)
  }

  if (limit) {
    jobs = jobs.slice(0, parseInt(limit as string))
  }

  res.json({
    total: jobs.length,
    jobs
  })
})

// Get specific job
app.get('/api/jobs/:id', (req: Request, res: Response) => {
  const job = engine.getJob(req.params.id)

  if (!job) {
    return res.status(404).json({ error: 'Job not found' })
  }

  res.json(job)
})

// Submit a generation job
app.post('/api/generate', async (req: Request, res: Response) => {
  try {
    const {
      prompt,
      promptData,
      productTypes = ['tshirt'],
      platforms,
      autoPublish = false,
      priority = 'normal'
    } = req.body

    if (!prompt && !promptData) {
      return res.status(400).json({
        error: 'Either prompt or promptData is required'
      })
    }

    const jobId = await engine.submitJob({
      type: 'generate',
      prompt,
      promptData,
      productTypes,
      platforms,
      autoPublish,
      priority
    })

    res.status(202).json({
      jobId,
      message: 'Job submitted successfully',
      status: 'pending'
    })
  } catch (error: any) {
    res.status(500).json({
      error: error.message || 'Failed to submit job'
    })
  }
})

// Submit batch jobs
app.post('/api/generate/batch', async (req: Request, res: Response) => {
  try {
    const { jobs } = req.body

    if (!Array.isArray(jobs) || jobs.length === 0) {
      return res.status(400).json({
        error: 'jobs array is required and must not be empty'
      })
    }

    const jobIds = await engine.submitBatch(jobs.map(j => ({
      type: 'generate',
      ...j
    })))

    res.status(202).json({
      jobIds,
      count: jobIds.length,
      message: 'Batch jobs submitted successfully'
    })
  } catch (error: any) {
    res.status(500).json({
      error: error.message || 'Failed to submit batch jobs'
    })
  }
})

// Cancel a job
app.post('/api/jobs/:id/cancel', (req: Request, res: Response) => {
  const success = engine.cancelJob(req.params.id)

  if (!success) {
    return res.status(400).json({
      error: 'Job cannot be cancelled (not found or not pending)'
    })
  }

  res.json({
    message: 'Job cancelled successfully',
    jobId: req.params.id
  })
})

// Retry a failed job
app.post('/api/jobs/:id/retry', async (req: Request, res: Response) => {
  const success = await engine.retryJob(req.params.id)

  if (!success) {
    return res.status(400).json({
      error: 'Job cannot be retried (not found or not failed)'
    })
  }

  res.json({
    message: 'Job retry initiated',
    jobId: req.params.id
  })
})

// Clear old jobs
app.post('/api/jobs/cleanup', (req: Request, res: Response) => {
  const { olderThanMs = 86400000 } = req.body // Default 24 hours

  const cleared = engine.clearOldJobs(olderThanMs)

  res.json({
    message: 'Cleanup completed',
    jobsCleared: cleared
  })
})

// Get engine info
app.get('/api/info', (req: Request, res: Response) => {
  res.json({
    name: 'POD Engine API',
    version: '1.0.0',
    config: engineConfig,
    timestamp: new Date().toISOString()
  })
})

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: any) => {
  console.error('API Error:', err)
  res.status(500).json({
    error: 'Internal server error',
    message: err.message
  })
})

// Create HTTP server
const server = http.createServer(app)

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('🛑 SIGTERM received, shutting down gracefully...')
  server.close(() => {
    console.log('📪 HTTP server closed')
  })
  await engine.shutdown()
  process.exit(0)
})

process.on('SIGINT', async () => {
  console.log('🛑 SIGINT received, shutting down gracefully...')
  server.close(() => {
    console.log('📪 HTTP server closed')
  })
  await engine.shutdown()
  process.exit(0)
})

// Start server
const PORT = process.env.PORT || 3000
server.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════╗
║            POD Engine API Server                   ║
║                                                    ║
║  Status: Running                                   ║
║  Port:   ${PORT}                                      ║
║  Health: http://localhost:${PORT}/health              ║
║  API:    http://localhost:${PORT}/api                 ║
╚════════════════════════════════════════════════════╝
  `)
})

export { engine, app, server }

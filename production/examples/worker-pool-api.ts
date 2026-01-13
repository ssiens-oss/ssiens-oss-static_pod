/**
 * Worker Pool with API Server Example
 * Demonstrates production deployment with multiple workers and HTTP API
 */

import { WorkerPool, WorkerPoolConfig } from '../WorkerPool'
import { ApiServer } from '../ApiServer'
import { createDatabaseClient } from '../DatabaseClient'
import { MetricsCollector, AlertManager, HealthChecker } from '../Monitoring'
import { EngineConfig } from '../ProductionPodEngine'
import * as fs from 'fs'
import * as path from 'path'

async function main() {
  console.log('=== Production POD Engine Worker Pool ===\n')

  // Load configuration from file or environment
  const configPath = process.env.CONFIG_PATH || path.join(__dirname, '../config.example.json')
  let config: any

  if (fs.existsSync(configPath)) {
    console.log(`Loading configuration from: ${configPath}`)
    config = JSON.parse(fs.readFileSync(configPath, 'utf-8'))
  } else {
    console.error(`Configuration file not found: ${configPath}`)
    console.log('Please copy config.example.json to config.json and update values')
    process.exit(1)
  }

  // Override with environment variables
  if (process.env.CLAUDE_API_KEY) {
    config.orchestrator.claude.apiKey = process.env.CLAUDE_API_KEY
  }
  if (process.env.COMFYUI_API_URL) {
    config.orchestrator.comfyui.apiUrl = process.env.COMFYUI_API_URL
  }
  if (process.env.WORKER_COUNT) {
    config.workerPool.workerCount = parseInt(process.env.WORKER_COUNT)
  }
  if (process.env.API_PORT) {
    config.api.port = parseInt(process.env.API_PORT)
  }

  // Create database client
  const db = createDatabaseClient(config.database)
  await db.connect()

  // Create monitoring components
  const metrics = new MetricsCollector(db)
  const alerts = new AlertManager()
  const health = new HealthChecker()

  // Register health checks
  health.register('database', async () => await db.healthCheck())

  // Setup alert listeners
  alerts.on('alert', (alert) => {
    console.log(`\n[ALERT:${alert.severity.toUpperCase()}] ${alert.name}: ${alert.message}\n`)
  })

  // Create worker pool configuration
  const workerPoolConfig: WorkerPoolConfig = {
    workerCount: config.workerPool.workerCount,
    engineConfig: config as EngineConfig,
    autoRestart: config.workerPool.autoRestart,
    maxRestarts: config.workerPool.maxRestarts,
    restartDelay: config.workerPool.restartDelay
  }

  // Create worker pool
  console.log(`Creating worker pool with ${workerPoolConfig.workerCount} workers...`)
  const workerPool = new WorkerPool(workerPoolConfig, db)

  // Setup worker pool event listeners
  workerPool.on('started', (data) => {
    console.log(`✓ Worker pool started with ${data.workerCount} workers`)
    alerts.trigger('worker_pool_started', 'info', `Started with ${data.workerCount} workers`)
  })

  workerPool.on('worker:started', (data) => {
    console.log(`✓ Worker ${data.index} (${data.workerId}) started`)
  })

  workerPool.on('worker:stopped', (data) => {
    console.log(`✗ Worker ${data.index} (${data.workerId}) stopped`)
  })

  workerPool.on('worker:error', (data) => {
    console.error(`✗ Worker ${data.index} (${data.workerId}) error: ${data.error}`)
    alerts.trigger('worker_error', 'error', `Worker ${data.index} failed: ${data.error}`, {
      workerId: data.workerId,
      index: data.index
    })
  })

  workerPool.on('job:submitted', (data) => {
    console.log(`→ Job submitted to worker ${data.workerId}`)
    metrics.counter('jobs_submitted')
  })

  workerPool.on('job:completed', (data) => {
    console.log(`✓ Job completed on worker ${data.workerId}`)
    metrics.counter('jobs_completed')
  })

  workerPool.on('job:failed', (data) => {
    console.error(`✗ Job failed on worker ${data.workerId}: ${data.error}`)
    metrics.counter('jobs_failed')
    alerts.trigger('job_failed', 'warning', `Job failed: ${data.error}`, {
      workerId: data.workerId,
      jobId: data.job.id
    })
  })

  workerPool.on('scaled', (data) => {
    console.log(`⚖ Pool scaled from ${data.previousCount} to ${data.newWorkerCount} workers`)
    alerts.trigger('pool_scaled', 'info', `Scaled to ${data.newWorkerCount} workers`)
  })

  // Start worker pool
  console.log('\nStarting worker pool...')
  await workerPool.start()

  // Create API server
  console.log('\nStarting API server...')
  const apiServer = new ApiServer(config.api, workerPool, db, metrics, alerts)
  await apiServer.start()

  console.log(`✓ API server listening on http://${config.api.host}:${config.api.port}`)
  console.log('\n=== Available API Endpoints ===')
  console.log(`  GET  http://localhost:${config.api.port}/health`)
  console.log(`  GET  http://localhost:${config.api.port}/stats`)
  console.log(`  GET  http://localhost:${config.api.port}/dashboard`)
  console.log(`  POST http://localhost:${config.api.port}/jobs`)
  console.log(`  GET  http://localhost:${config.api.port}/jobs/:id`)
  console.log(`  GET  http://localhost:${config.api.port}/jobs`)
  console.log(`  GET  http://localhost:${config.api.port}/workers`)
  console.log(`  POST http://localhost:${config.api.port}/workers/:id/restart`)
  console.log(`  POST http://localhost:${config.api.port}/scale`)
  console.log(`  GET  http://localhost:${config.api.port}/metrics`)
  console.log(`  GET  http://localhost:${config.api.port}/alerts`)
  console.log('\n================================\n')

  // Periodic stats logging
  const statsInterval = setInterval(async () => {
    const stats = await workerPool.getStats()
    console.log(`[Stats] Workers: ${stats.runningWorkers}/${stats.totalWorkers} | ` +
                `Jobs: ${stats.totalCompleted} completed, ${stats.totalFailed} failed`)

    // Record metrics
    await metrics.gauge('workers_running', stats.runningWorkers)
    await metrics.gauge('workers_error', stats.errorWorkers)
    await metrics.gauge('total_jobs_completed', stats.totalCompleted)
    await metrics.gauge('total_jobs_failed', stats.totalFailed)

    // Check for issues
    if (stats.runningWorkers === 0 && stats.totalWorkers > 0) {
      alerts.trigger('no_workers_running', 'critical', 'No workers are running!')
    }
    if (stats.errorWorkers > stats.totalWorkers / 2) {
      alerts.trigger('high_worker_errors', 'critical', `${stats.errorWorkers} workers in error state`)
    }
  }, 30000) // Every 30 seconds

  // Graceful shutdown
  async function shutdown() {
    console.log('\n\n=== Shutting down gracefully ===')

    clearInterval(statsInterval)

    console.log('Stopping API server...')
    await apiServer.stop()

    console.log('Stopping worker pool...')
    await workerPool.stop()

    console.log('Disconnecting database...')
    await db.disconnect()

    console.log('✓ Shutdown complete')
    process.exit(0)
  }

  // Handle shutdown signals
  process.on('SIGINT', shutdown)
  process.on('SIGTERM', shutdown)

  // Handle uncaught errors
  process.on('uncaughtException', (error) => {
    console.error('Uncaught exception:', error)
    alerts.trigger('uncaught_exception', 'critical', error.message, { stack: error.stack })
  })

  process.on('unhandledRejection', (reason) => {
    console.error('Unhandled rejection:', reason)
    alerts.trigger('unhandled_rejection', 'critical', String(reason))
  })

  console.log('✓ System ready and running')
  console.log('Press Ctrl+C to shutdown\n')
}

main().catch(error => {
  console.error('Fatal error:', error)
  process.exit(1)
})

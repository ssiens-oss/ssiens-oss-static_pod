/**
 * Simple Single Worker Example
 * Demonstrates basic usage of ProductionPodEngine
 */

import { ProductionPodEngine, EngineConfig } from '../ProductionPodEngine'
import { createDatabaseClient } from '../DatabaseClient'

async function main() {
  // Load configuration
  const config: EngineConfig = {
    orchestrator: {
      comfyui: {
        apiUrl: process.env.COMFYUI_API_URL || 'http://127.0.0.1:8188',
        outputDir: process.env.COMFYUI_OUTPUT_DIR || './comfyui_output'
      },
      claude: {
        apiKey: process.env.CLAUDE_API_KEY || ''
      },
      storage: {
        type: 'local',
        basePath: './storage'
      },
      printify: {
        apiKey: process.env.PRINTIFY_API_KEY,
        shopId: process.env.PRINTIFY_SHOP_ID
      },
      options: {
        enabledPlatforms: ['printify'],
        autoPublish: false,
        tshirtPrice: 19.99,
        hoodiePrice: 34.99
      }
    },
    engine: {
      maxConcurrentJobs: 3,
      jobTimeout: 3600000, // 1 hour
      retryDelay: 60000, // 1 minute
      enableAutoRetry: true
    },
    database: {
      type: 'memory' // Use in-memory for development
    }
  }

  // Create and start engine
  const engine = new ProductionPodEngine(config)

  // Setup event listeners
  engine.on('started', (data) => {
    console.log('Engine started:', data)
  })

  engine.on('job:submitted', (data) => {
    console.log('Job submitted:', data.jobId)
  })

  engine.on('job:completed', (data) => {
    console.log('Job completed:', data.job.id)
    console.log('Generated images:', data.result.generatedImages.length)
    console.log('Created products:', data.result.products.length)
  })

  engine.on('job:failed', (data) => {
    console.error('Job failed:', data.job.id, data.error)
  })

  engine.on('log', (log) => {
    console.log(`[${log.type}] ${log.message}`)
  })

  // Start engine
  await engine.start()

  // Submit a test job
  const jobId = await engine.submitJob({
    theme: 'Cyber Punk',
    style: 'Neon Art',
    niche: 'Gaming',
    productTypes: ['tshirt', 'hoodie'],
    count: 2,
    autoPublish: false,
    priority: 10
  })

  console.log('Submitted job:', jobId)

  // Monitor job status
  const checkInterval = setInterval(async () => {
    const status = await engine.getJobStatus(jobId)
    console.log('Job status:', status?.status)

    if (status?.status === 'completed' || status?.status === 'failed') {
      clearInterval(checkInterval)

      // Get final stats
      const stats = await engine.getStats()
      console.log('\nFinal Stats:', JSON.stringify(stats, null, 2))

      // Graceful shutdown
      console.log('\nShutting down...')
      await engine.stop()
      process.exit(0)
    }
  }, 5000)

  // Handle shutdown signals
  process.on('SIGINT', async () => {
    console.log('\nReceived SIGINT, shutting down...')
    clearInterval(checkInterval)
    await engine.stop()
    process.exit(0)
  })
}

main().catch(error => {
  console.error('Fatal error:', error)
  process.exit(1)
})

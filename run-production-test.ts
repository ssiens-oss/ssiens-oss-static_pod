/**
 * Production POD Pipeline Test
 * Runs a complete end-to-end test of the POD pipeline
 */

import { config as loadEnv } from 'dotenv'
import { Orchestrator } from './services/orchestrator'
import { loadConfig } from './services/config'
import { getLogger, LogLevel } from './services/utils/logger'

// Load environment variables
loadEnv()

// Initialize logger
const logger = getLogger()
logger.setLevel(LogLevel.INFO)

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('  🚀 POD Pipeline Production Test')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log()

async function runProductionTest() {
  try {
    // Step 1: Load configuration
    console.log('📋 Step 1: Loading configuration...')
    const config = loadConfig()
    console.log('✅ Configuration loaded successfully')
    console.log(`   Enabled Platforms: ${config.options?.enabledPlatforms?.join(', ') || 'none'}`)
    console.log(`   Auto-Publish: ${config.options?.autoPublish ? 'Yes' : 'No'}`)
    console.log()

    // Step 2: Create orchestrator
    console.log('🔧 Step 2: Initializing orchestrator...')
    const orchestrator = new Orchestrator({
      comfyui: config.comfyui,
      claude: config.claude,
      storage: config.storage,
      printify: config.printify,
      shopify: config.shopify,
      options: config.options
    })

    // Set up logging
    orchestrator.setLogger((message, type) => {
      const emoji = {
        INFO: 'ℹ️',
        SUCCESS: '✅',
        WARNING: '⚠️',
        ERROR: '❌'
      }[type] || 'ℹ️'

      console.log(`${emoji} ${message}`)
    })

    console.log('✅ Orchestrator initialized')
    console.log()

    // Step 3: Run pipeline
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    console.log('  🎨 Running POD Pipeline')
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    console.log()

    const result = await orchestrator.run({
      theme: 'cyberpunk neon city',
      style: 'futuristic, vibrant colors',
      niche: 'tech enthusiasts and gamers',
      productTypes: ['tshirt'],
      count: 1,
      autoPublish: config.options?.autoPublish
    })

    // Step 4: Display results
    console.log()
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    console.log('  📊 Pipeline Results')
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    console.log()

    console.log(`Status: ${result.success ? '✅ SUCCESS' : '❌ FAILED'}`)
    console.log(`Total Time: ${(result.totalTime / 1000).toFixed(2)}s`)
    console.log()

    if (result.generatedImages.length > 0) {
      console.log('🎨 Generated Images:')
      result.generatedImages.forEach((img, i) => {
        console.log(`   ${i + 1}. ${img.id}`)
        console.log(`      URL: ${img.url}`)
        console.log(`      Prompt: ${img.prompt.substring(0, 60)}...`)
      })
      console.log()
    }

    if (result.products.length > 0) {
      console.log('📦 Created Products:')
      result.products.forEach((prod, i) => {
        console.log(`   ${i + 1}. ${prod.platform.toUpperCase()} - ${prod.type}`)
        console.log(`      Product ID: ${prod.productId}`)
        console.log(`      URL: ${prod.url}`)
      })
      console.log()
    }

    if (result.errors.length > 0) {
      console.log('⚠️  Errors:')
      result.errors.forEach((err, i) => {
        console.log(`   ${i + 1}. ${err}`)
      })
      console.log()
    }

    // Step 5: Summary
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    console.log('  ✅ Test Complete!')
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    console.log()

    console.log('Next Steps:')
    console.log('  1. Check ./designs/ for generated images')
    console.log('  2. Check Printify dashboard for products')
    if (!config.options?.autoPublish) {
      console.log('  3. Enable AUTO_PUBLISH=true in .env to auto-publish')
    }
    console.log()

    process.exit(result.success ? 0 : 1)

  } catch (error) {
    console.error()
    console.error('❌ Pipeline Error:', error)
    console.error()

    if (error instanceof Error) {
      console.error('Error Details:')
      console.error(`  Message: ${error.message}`)
      if (error.stack) {
        console.error(`  Stack: ${error.stack.split('\n').slice(0, 5).join('\n')}`)
      }
    }

    console.error()
    console.error('💡 Troubleshooting:')
    console.error('  - Make sure ComfyUI is running at http://localhost:8188')
    console.error('  - Verify API keys in .env are correct')
    console.error('  - Run: npm run test:config')
    console.error()

    process.exit(1)
  }
}

// Run the test
runProductionTest()

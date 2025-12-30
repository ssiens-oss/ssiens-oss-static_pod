#!/usr/bin/env node
/**
 * POD Pipeline Runner - Batch Mode
 * Generates multiple designs in batch and auto-publishes to all platforms
 */

import { Orchestrator } from '../services/orchestrator.js'
import dotenv from 'dotenv'

dotenv.config()

// Configuration (same as run-pipeline.js)
const config = {
  comfyui: {
    apiUrl: process.env.COMFYUI_API_URL || 'http://localhost:8188',
    outputDir: process.env.COMFYUI_OUTPUT_DIR || '/workspace/ComfyUI/output'
  },
  claude: {
    apiKey: process.env.ANTHROPIC_API_KEY
  },
  storage: {
    type: process.env.STORAGE_TYPE || 'local',
    basePath: process.env.STORAGE_PATH || '/data/designs'
  },
  printify: process.env.PRINTIFY_API_KEY ? {
    apiKey: process.env.PRINTIFY_API_KEY,
    shopId: process.env.PRINTIFY_SHOP_ID
  } : undefined,
  shopify: process.env.SHOPIFY_ACCESS_TOKEN ? {
    storeUrl: process.env.SHOPIFY_STORE_URL,
    accessToken: process.env.SHOPIFY_ACCESS_TOKEN,
    apiVersion: process.env.SHOPIFY_API_VERSION || '2024-01'
  } : undefined
}

// Batch themes
const themes = [
  'retro gaming',
  'cyberpunk aesthetic',
  'nature and wildlife',
  'space and astronomy',
  'vintage music',
  'abstract geometry',
  'motivational quotes',
  'cute animals',
  'travel and adventure',
  'food and cooking'
]

const batchSize = parseInt(process.argv[2]) || 10
const autoPublish = !process.argv.includes('--no-publish')

console.log('╔════════════════════════════════════════════════════╗')
console.log('║  POD Studio - Batch Pipeline                      ║')
console.log('╚════════════════════════════════════════════════════╝')
console.log('')
console.log(`Running batch of ${batchSize} designs...`)
console.log(`Auto-publish: ${autoPublish ? 'Yes' : 'No'}`)
console.log('')

if (!config.claude.apiKey) {
  console.error('❌ Error: ANTHROPIC_API_KEY is required!')
  process.exit(1)
}

async function main() {
  const orchestrator = new Orchestrator(config)
  const results = []

  console.log('🚀 Starting batch generation...\n')

  for (let i = 0; i < batchSize; i++) {
    const theme = themes[i % themes.length]
    console.log(`\n[${i + 1}/${batchSize}] Theme: ${theme}`)
    console.log('─'.repeat(50))

    try {
      const result = await orchestrator.run({
        theme,
        count: 1,
        productTypes: ['tshirt', 'hoodie'],
        autoPublish,
        platforms: {
          printify: !!config.printify,
          shopify: !!config.shopify
        }
      })

      results.push(result)
      console.log(`✓ Generated ${result.generatedImages.length} image(s)`)
      console.log(`✓ Created ${result.products.length} product(s)`)

    } catch (error) {
      console.error(`✗ Failed: ${error.message}`)
    }

    // Small delay between batches
    if (i < batchSize - 1) {
      console.log('\nWaiting 5 seconds before next batch...')
      await new Promise(resolve => setTimeout(resolve, 5000))
    }
  }

  // Summary
  console.log('\n╔════════════════════════════════════════════════════╗')
  console.log('║  Batch Complete!                                  ║')
  console.log('╚════════════════════════════════════════════════════╝\n')

  const totalImages = results.reduce((sum, r) => sum + r.generatedImages.length, 0)
  const totalProducts = results.reduce((sum, r) => sum + r.products.length, 0)

  console.log(`✓ Total images: ${totalImages}`)
  console.log(`✓ Total products: ${totalProducts}`)
  console.log(`✓ Success rate: ${results.length}/${batchSize}`)
  console.log('\n✨ All done!\n')
}

main().catch(console.error)

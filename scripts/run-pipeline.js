#!/usr/bin/env node
/**
 * POD Pipeline Runner - Single Design
 * Generates a single design and auto-publishes to all platforms
 */

import { Orchestrator } from '../services/orchestrator.js'
import dotenv from 'dotenv'

// Load environment variables
dotenv.config()

// Configuration from environment
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
  } : undefined,
  tiktok: process.env.TIKTOK_ACCESS_TOKEN ? {
    appKey: process.env.TIKTOK_APP_KEY,
    appSecret: process.env.TIKTOK_APP_SECRET,
    shopId: process.env.TIKTOK_SHOP_ID,
    accessToken: process.env.TIKTOK_ACCESS_TOKEN
  } : undefined,
  etsy: process.env.ETSY_ACCESS_TOKEN ? {
    apiKey: process.env.ETSY_API_KEY,
    shopId: process.env.ETSY_SHOP_ID,
    accessToken: process.env.ETSY_ACCESS_TOKEN
  } : undefined
}

// Parse command line arguments
const args = process.argv.slice(2)
const theme = args.find(arg => arg.startsWith('--theme='))?.split('=')[1] || 'random'
const count = parseInt(args.find(arg => arg.startsWith('--count='))?.split('=')[1] || '1')
const autoPublish = !args.includes('--no-publish')
const productTypes = args.find(arg => arg.startsWith('--products='))?.split('=')[1]?.split(',') || ['tshirt', 'hoodie']

console.log('╔════════════════════════════════════════════════════╗')
console.log('║  POD Studio - Auto Pipeline                       ║')
console.log('╚════════════════════════════════════════════════════╝')
console.log('')
console.log('Configuration:')
console.log(`  Theme:        ${theme}`)
console.log(`  Count:        ${count} design(s)`)
console.log(`  Products:     ${productTypes.join(', ')}`)
console.log(`  Auto-publish: ${autoPublish ? 'Yes' : 'No'}`)
console.log('')
console.log('Platforms configured:')
console.log(`  ✓ ComfyUI:    ${config.comfyui.apiUrl}`)
console.log(`  ${config.printify ? '✓' : '✗'} Printify:   ${config.printify ? 'Enabled' : 'Not configured'}`)
console.log(`  ${config.shopify ? '✓' : '✗'} Shopify:    ${config.shopify ? 'Enabled' : 'Not configured'}`)
console.log(`  ${config.tiktok ? '✓' : '✗'} TikTok:     ${config.tiktok ? 'Enabled' : 'Not configured'}`)
console.log(`  ${config.etsy ? '✓' : '✗'} Etsy:       ${config.etsy ? 'Enabled' : 'Not configured'}`)
console.log('')

// Validate required configuration
if (!config.claude.apiKey) {
  console.error('❌ Error: ANTHROPIC_API_KEY is required!')
  console.error('   Set it in your .env file or environment variables.')
  process.exit(1)
}

async function main() {
  try {
    console.log('🚀 Starting POD automation pipeline...\n')

    // Initialize orchestrator
    const orchestrator = new Orchestrator(config)

    // Run pipeline
    const result = await orchestrator.run({
      theme,
      count,
      productTypes,
      autoPublish,
      platforms: {
        printify: !!config.printify,
        shopify: !!config.shopify,
        tiktok: !!config.tiktok,
        etsy: !!config.etsy
      }
    })

    // Display results
    console.log('\n╔════════════════════════════════════════════════════╗')
    console.log('║  Pipeline Complete!                               ║')
    console.log('╚════════════════════════════════════════════════════╝\n')

    console.log(`✓ Generated ${result.generatedImages.length} image(s)`)
    console.log(`✓ Created ${result.products.length} product(s)`)

    if (result.published.length > 0) {
      console.log(`✓ Published to ${result.published.length} platform(s):`)
      result.published.forEach(pub => {
        console.log(`  - ${pub.platform}: ${pub.count} product(s)`)
      })
    }

    console.log('\nImages saved to:', config.storage.basePath)

    if (result.generatedImages.length > 0) {
      console.log('\nGenerated designs:')
      result.generatedImages.forEach((img, i) => {
        console.log(`  ${i + 1}. ${img.title}`)
        console.log(`     File: ${img.url}`)
      })
    }

    console.log('\n✨ All done! Your designs are live!\n')

  } catch (error) {
    console.error('\n❌ Pipeline failed:', error.message)
    console.error(error.stack)
    process.exit(1)
  }
}

// Run the pipeline
main()

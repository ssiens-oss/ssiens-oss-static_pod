#!/usr/bin/env node
const fs = require('fs')
const path = require('path')
require('dotenv').config()

const COMFYUI_OUTPUT_DIR = process.env.COMFYUI_OUTPUT_DIR || '/workspace/ComfyUI/output'
const PRINTIFY_API_KEY = process.env.PRINTIFY_API_KEY
const PRINTIFY_SHOP_ID = process.env.PRINTIFY_SHOP_ID

// Simple logger
const log = {
  info: (msg) => console.log(`[INFO] ${msg}`),
  warn: (msg) => console.warn(`[WARN] ${msg}`),
  error: (msg) => console.error(`[ERROR] ${msg}`)
}

// Simple metrics
const metrics = {
  inc: (key, val) => {}
}

async function main() {
  console.log('╔════════════════════════════════════════════════════╗')
  console.log('║  Static Waves Batch Publisher                     ║')
  console.log('╚════════════════════════════════════════════════════╝')
  console.log('')

  // Validate config
  if (!PRINTIFY_API_KEY || !PRINTIFY_SHOP_ID) {
    log.error('Missing PRINTIFY_API_KEY or PRINTIFY_SHOP_ID in .env')
    process.exit(1)
  }

  log.info(`ComfyUI Output: ${COMFYUI_OUTPUT_DIR}`)
  log.info(`Shop ID: ${PRINTIFY_SHOP_ID}`)
  console.log('')

  // Get all images
  const files = fs.readdirSync(COMFYUI_OUTPUT_DIR)
    .filter(f => f.match(/\.(png|jpg|jpeg)$/i))
    .sort()

  log.info(`Found ${files.length} images to process`)
  console.log('')

  if (files.length === 0) {
    log.error('No images found!')
    process.exit(1)
  }

  // Load publish stage
  const publishStage = require('./stages/publish.cjs')

  // Process each image
  let successCount = 0
  let failCount = 0

  for (let i = 0; i < files.length; i++) {
    const filename = files[i]
    const filepath = path.join(COMFYUI_OUTPUT_DIR, filename)

    console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`)
    console.log(`📦 Processing [${i + 1}/${files.length}]: ${filename}`)
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`)

    // Create job context
    const job = {
      output: {
        image: filename,
        path: filepath
      }
    }

    const ctx = {
      env: {
        PRINTIFY_API_KEY,
        PRINTIFY_SHOP_ID
      },
      log,
      metrics
    }

    try {
      const result = await publishStage(job, ctx)

      if (result.published) {
        successCount++
        console.log(`\n✅ Success! Drop #${result.drop_number} - ${result.products.length} products created`)
      } else {
        failCount++
        console.log(`\n⚠️  Skipped: ${result.reason || result.error}`)
      }
    } catch (error) {
      failCount++
      console.log(`\n❌ Error: ${error.message}`)
    }

    // Rate limiting - wait 2 seconds between batches to avoid API throttling
    if (i < files.length - 1) {
      console.log('\n⏳ Waiting 2s before next batch...')
      await new Promise(resolve => setTimeout(resolve, 2000))
    }
  }

  // Summary
  console.log('\n\n╔════════════════════════════════════════════════════╗')
  console.log('║  Batch Complete!                                  ║')
  console.log('╚════════════════════════════════════════════════════╝')
  console.log('')
  console.log(`✅ Successful: ${successCount}`)
  console.log(`❌ Failed: ${failCount}`)
  console.log(`📊 Total: ${files.length}`)
  console.log(`🛍️  Products Created: ${successCount * 5}`)
  console.log('')
}

main().catch(err => {
  console.error('Fatal error:', err)
  process.exit(1)
})

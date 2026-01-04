#!/usr/bin/env node
/**
 * Printify Diagnostics Script
 * Helps you find the correct blueprint and provider IDs for your shop
 */

import dotenv from 'dotenv'

dotenv.config()

const apiKey = process.env.PRINTIFY_API_KEY
const shopId = process.env.PRINTIFY_SHOP_ID
const baseUrl = 'https://api.printify.com/v1'

async function diagnose() {
  console.log('🔍 Printify Diagnostics\n')
  console.log(`Shop ID: ${shopId}`)
  console.log(`API Key: ${apiKey ? '✓ Set' : '✗ Not set'}\n`)

  if (!apiKey || !shopId) {
    console.error('❌ Missing PRINTIFY_API_KEY or PRINTIFY_SHOP_ID in .env file')
    process.exit(1)
  }

  try {
    // Test 1: Verify shop access
    console.log('📋 Test 1: Verifying shop access...')
    const shopResponse = await fetch(`${baseUrl}/shops/${shopId}.json`, {
      headers: { 'Authorization': `Bearer ${apiKey}` }
    })

    if (!shopResponse.ok) {
      const error = await shopResponse.json()
      console.error(`❌ Shop verification failed:`, error)
      console.log('\n💡 Tip: Double-check your PRINTIFY_SHOP_ID in .env')
      process.exit(1)
    }

    const shop = await shopResponse.json()
    console.log(`✅ Shop verified: ${shop.title || 'Unnamed Shop'}`)

    // Test 2: List available blueprints
    console.log('\n📋 Test 2: Fetching available blueprints...')
    const blueprintsResponse = await fetch(`${baseUrl}/catalog/blueprints.json`, {
      headers: { 'Authorization': `Bearer ${apiKey}` }
    })

    if (!blueprintsResponse.ok) {
      console.error('❌ Failed to fetch blueprints')
      process.exit(1)
    }

    const blueprints = await blueprintsResponse.json()

    // Find T-shirt and Hoodie blueprints
    const tshirts = blueprints.filter((b: any) =>
      b.title.toLowerCase().includes('t-shirt') || b.title.toLowerCase().includes('tee')
    )
    const hoodies = blueprints.filter((b: any) =>
      b.title.toLowerCase().includes('hoodie')
    )

    console.log('\n👕 Available T-Shirt Blueprints:')
    tshirts.slice(0, 5).forEach((b: any) => {
      console.log(`   ID: ${b.id} - ${b.title}`)
    })

    console.log('\n🧥 Available Hoodie Blueprints:')
    hoodies.slice(0, 5).forEach((b: any) => {
      console.log(`   ID: ${b.id} - ${b.title}`)
    })

    // Test 3: Check providers for a common T-shirt blueprint
    if (tshirts.length > 0) {
      const tshirtId = tshirts[0].id
      console.log(`\n📋 Test 3: Checking providers for blueprint ${tshirtId}...`)

      const providersResponse = await fetch(
        `${baseUrl}/catalog/blueprints/${tshirtId}/print_providers.json`,
        {
          headers: { 'Authorization': `Bearer ${apiKey}` }
        }
      )

      if (providersResponse.ok) {
        const providers = await providersResponse.json()
        console.log(`\n🏭 Available Print Providers for ${tshirts[0].title}:`)
        providers.slice(0, 5).forEach((p: any) => {
          console.log(`   ID: ${p.id} - ${p.title}`)
        })
      }
    }

    console.log('\n' + '='.repeat(60))
    console.log('✅ Diagnostics Complete!')
    console.log('='.repeat(60))
    console.log('\n💡 Next Steps:')
    console.log('1. Choose a blueprint ID from the lists above')
    console.log('2. Update services/printify.ts with the correct IDs')
    console.log('3. Re-run the printify-push script')

  } catch (error) {
    console.error('❌ Error:', error)
    process.exit(1)
  }
}

diagnose()

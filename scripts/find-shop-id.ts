#!/usr/bin/env node
/**
 * Find your Printify Shop ID
 * This script lists all shops associated with your API key
 */

import dotenv from 'dotenv'

dotenv.config()

const apiKey = process.env.PRINTIFY_API_KEY
const baseUrl = 'https://api.printify.com/v1'

async function findShops() {
  console.log('🔍 Finding your Printify shops...\n')

  if (!apiKey || apiKey === 'your-printify-api-key') {
    console.error('❌ PRINTIFY_API_KEY is not set or still has placeholder value')
    console.log('\n📝 Steps to get your API key:')
    console.log('1. Go to: https://printify.com/app/account/api')
    console.log('2. Click "Create Token" or copy an existing token')
    console.log('3. Update PRINTIFY_API_KEY in your .env file')
    process.exit(1)
  }

  console.log('✓ API Key is set\n')

  try {
    console.log('📡 Fetching your shops from Printify...\n')

    const response = await fetch(`${baseUrl}/shops.json`, {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      const error = await response.json()
      console.error('❌ API Error:', error)
      console.log('\n💡 This usually means your API key is invalid.')
      console.log('Please double-check your PRINTIFY_API_KEY in .env')
      process.exit(1)
    }

    const shops = await response.json()

    if (!shops || shops.length === 0) {
      console.log('⚠️  No shops found in your Printify account')
      console.log('Please create a shop at: https://printify.com/app/stores')
      process.exit(1)
    }

    console.log('✅ Found your shop(s):\n')
    console.log('='.repeat(60))

    shops.forEach((shop: any, index: number) => {
      console.log(`\nShop #${index + 1}:`)
      console.log(`  ID: ${shop.id}`)
      console.log(`  Title: ${shop.title}`)
      console.log(`  Sales Channel: ${shop.sales_channel}`)
    })

    console.log('\n' + '='.repeat(60))
    console.log('\n📝 Next Steps:')
    console.log('1. Copy the Shop ID from above')
    console.log('2. Update PRINTIFY_SHOP_ID in your .env file')
    console.log('3. Run: npm run printify:diagnostics')

    if (shops.length === 1) {
      console.log(`\n💡 Tip: Your Shop ID is: ${shops[0].id}`)
      console.log(`   Update your .env with: PRINTIFY_SHOP_ID=${shops[0].id}`)
    }

  } catch (error) {
    console.error('❌ Error:', error)
    console.log('\n💡 Please check your internet connection and API key')
    process.exit(1)
  }
}

findShops()

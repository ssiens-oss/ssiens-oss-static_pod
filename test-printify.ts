/**
 * Quick test script to verify Printify integration with print_areas
 */

import { PrintifyService } from './services/printify'
import * as dotenv from 'dotenv'

dotenv.config()

async function testPrintify() {
  console.log('🧪 Testing Printify Integration...\n')

  const printify = new PrintifyService({
    apiKey: process.env.PRINTIFY_API_KEY!,
    shopId: process.env.PRINTIFY_SHOP_ID!
  })

  try {
    // Test 1: Get variants for T-shirt blueprint
    console.log('📋 Step 1: Fetching T-shirt variants (Blueprint 3, Provider 99)...')
    const tshirtVariants = await printify.getVariants(3, 99)
    console.log(`✅ Found ${tshirtVariants.variants?.length || 0} T-shirt variants\n`)

    // Test 2: Create a test T-shirt product
    console.log('👕 Step 2: Creating test T-shirt product...')
    const placeholderImage = 'https://via.placeholder.com/1024x1024/000000/ffffff?text=Test+Design'

    const product = await printify.createTShirt(
      placeholderImage,
      'Test Product - Printify Integration',
      'Testing the new print_areas integration with Printify API',
      {
        price: 19.99,
        tags: ['test', 'integration']
      }
    )

    console.log('✅ Product created successfully!')
    console.log(`   Product ID: ${product.id}`)
    console.log(`   Title: ${product.title}`)
    console.log(`   Variants: ${product.variants}`)
    console.log(`   View at: https://printify.com/app/products/${product.id}\n`)

    console.log('🎉 All tests passed! Printify integration is working correctly.')

  } catch (error: any) {
    console.error('❌ Test failed:', error.message)
    if (error.message.includes('print_areas')) {
      console.error('\n💡 The print_areas field is still missing. Make sure the latest code is deployed.')
    }
    process.exit(1)
  }
}

testPrintify()

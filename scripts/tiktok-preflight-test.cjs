#!/usr/bin/env node
/**
 * Test TikTok Preflight Checker
 */

const TikTokPreflight = require('./tiktok-preflight.cjs')

console.log('🧪 Testing TikTok Preflight Checker\n')

const preflight = new TikTokPreflight()

// Test 1: Price too low (BLOCKER)
console.log('Test 1: Low price (should BLOCK storefront)')
const test1 = {
  id: 'test-001',
  title: 'Static Waves Drop #001 - Tee (Black)',
  price: 8.99, // Below $12 floor
  variants: [
    { id: 12126, price: 8.99, inventory: 100 }
  ],
  images: ['test.png']
}

let result1 = preflight.check(test1)
console.log(`  Storefront: ${result1.canPublishStorefront ? '✅ PASS' : '❌ BLOCKED'}`)
console.log(`  LIVE: ${result1.canPublishLive ? '✅ PASS' : '❌ BLOCKED'}`)
console.log(`  Recommendation: ${result1.recommendation}`)
if (result1.blockers.length > 0) {
  console.log(`  Blockers:`)
  result1.blockers.forEach(b => console.log(`    - ${b.message}`))
}

// Test auto-fix
console.log('\n  Applying auto-fix...')
preflight.autoFix(test1)
result1 = preflight.check(test1)
console.log(`  After fix - Storefront: ${result1.canPublishStorefront ? '✅ PASS' : '❌ BLOCKED'}`)
console.log(`  New price: $${test1.price}\n`)

// Test 2: Low inventory (WARNING)
console.log('Test 2: Low inventory (should WARN but allow)')
const test2 = {
  id: 'test-002',
  title: 'Static Waves Drop #002 - Hoodie',
  price: 25.00,
  variants: [
    { id: 12345, price: 25.00, inventory: 3 } // Below 10
  ],
  images: ['test.png']
}

const result2 = preflight.check(test2)
console.log(`  Storefront: ${result2.canPublishStorefront ? '✅ PASS' : '❌ BLOCKED'}`)
console.log(`  Warnings: ${result2.warnings.length}`)
if (result2.warnings.length > 0) {
  console.log(`  Issues:`)
  result2.warnings.forEach(w => console.log(`    - ${w.message}`))
}

// Test 3: Perfect product (PASS)
console.log('\nTest 3: Perfect product (should PASS)')
const test3 = {
  id: 'test-003',
  title: 'Static Waves Drop #003 - Poster',
  price: 19.99,
  variants: [
    { id: 33742, price: 14.99, inventory: 100 },
    { id: 33743, price: 19.99, inventory: 100 }
  ],
  images: ['test1.png', 'test2.png']
}

const result3 = preflight.check(test3)
console.log(`  Storefront: ${result3.canPublishStorefront ? '✅ PASS' : '❌ BLOCKED'}`)
console.log(`  LIVE: ${result3.canPublishLive ? '✅ PASS' : '❌ BLOCKED'}`)
console.log(`  Recommendation: ${result3.recommendation}`)

console.log('\n✅ Preflight checker is working!\n')
console.log('Next steps:')
console.log('1. Integrate into pipeline/stages/publish.cjs')
console.log('2. Set TIKTOK_LIVE_FALLBACK=true in .env')
console.log('3. Run: node pipeline/runner.cjs --count 1')

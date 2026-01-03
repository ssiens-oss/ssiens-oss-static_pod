/**
 * Configuration Test Script
 * Tests that all required API keys and configuration are set correctly
 * Does NOT display actual keys for security
 */

import { getConfigManager, ConfigurationError } from './services/config'
import { getLogger, LogLevel } from './services/utils/logger'

// Initialize logger
const logger = getLogger()
logger.setLevel(LogLevel.INFO)

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('  POD Pipeline Configuration Test')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log()

// Function to mask sensitive data
function maskSecret(value: string | undefined, showLength: number = 4): string {
  if (!value) return '❌ NOT SET'
  if (value.startsWith('your-') || value.startsWith('sk-ant-your')) {
    return '❌ PLACEHOLDER (not a real key)'
  }
  const visiblePart = value.substring(0, showLength)
  const masked = '*'.repeat(Math.max(value.length - showLength, 8))
  return `✓ ${visiblePart}${masked}`
}

// Test configuration loading
let config: any
let manager: any

try {
  console.log('📋 Loading configuration...')
  manager = getConfigManager()
  config = manager.loadFromEnv()
  console.log('✅ Configuration loaded successfully!\n')
} catch (error) {
  if (error instanceof ConfigurationError) {
    console.error('❌ Configuration Error:', error.message)
    console.log('\n💡 Fix: Edit your .env file and set the required values')
    console.log('   Run: ./setup-keys.sh\n')
    process.exit(1)
  }
  throw error
}

// Display configuration summary
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('  CORE CONFIGURATION')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log()

// ComfyUI
console.log('🎨 ComfyUI:')
console.log(`   URL: ${config.comfyui.apiUrl}`)
console.log(`   Output Dir: ${config.comfyui.outputDir}`)
console.log(`   Timeout: ${config.comfyui.timeout}ms`)
console.log()

// Claude
console.log('🤖 Claude AI:')
console.log(`   API Key: ${maskSecret(config.claude.apiKey, 7)}`)
console.log(`   Model: ${config.claude.model}`)
console.log()

// Storage
console.log('💾 Storage:')
console.log(`   Type: ${config.storage.type}`)
console.log(`   Path: ${config.storage.basePath}`)
if (config.storage.type === 's3' && config.storage.s3Config) {
  console.log(`   S3 Bucket: ${config.storage.s3Config.bucket}`)
  console.log(`   S3 Region: ${config.storage.s3Config.region}`)
  console.log(`   Access Key: ${maskSecret(config.storage.s3Config.accessKeyId)}`)
} else if (config.storage.type === 'gcs' && config.storage.gcsConfig) {
  console.log(`   GCS Bucket: ${config.storage.gcsConfig.bucket}`)
  console.log(`   GCS Project: ${config.storage.gcsConfig.projectId}`)
}
console.log()

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('  PLATFORM INTEGRATIONS')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log()

const enabledPlatforms = manager.getEnabledPlatforms()
console.log(`Enabled Platforms: ${enabledPlatforms.join(', ') || 'none'}`)
console.log()

// Printify
if (config.printify) {
  console.log('✅ Printify:')
  console.log(`   API Key: ${maskSecret(config.printify.apiKey)}`)
  console.log(`   Shop ID: ${config.printify.shopId}`)
  console.log()
} else {
  console.log('⚪ Printify: Not configured')
  console.log()
}

// Shopify
if (config.shopify) {
  console.log('✅ Shopify:')
  console.log(`   Store URL: ${config.shopify.storeUrl}`)
  console.log(`   Access Token: ${maskSecret(config.shopify.accessToken)}`)
  console.log(`   API Version: ${config.shopify.apiVersion}`)
  console.log()
} else {
  console.log('⚪ Shopify: Not configured')
  console.log()
}

// TikTok
if (config.tiktok) {
  console.log('✅ TikTok Shop:')
  console.log(`   App Key: ${maskSecret(config.tiktok.appKey)}`)
  console.log(`   App Secret: ${maskSecret(config.tiktok.appSecret)}`)
  console.log(`   Shop ID: ${config.tiktok.shopId}`)
  console.log(`   Access Token: ${maskSecret(config.tiktok.accessToken)}`)
  console.log()
} else {
  console.log('⚪ TikTok Shop: Not configured')
  console.log()
}

// Etsy
if (config.etsy) {
  console.log('✅ Etsy:')
  console.log(`   API Key: ${maskSecret(config.etsy.apiKey)}`)
  console.log(`   Shop ID: ${config.etsy.shopId}`)
  console.log(`   Access Token: ${maskSecret(config.etsy.accessToken)}`)
  console.log()
} else {
  console.log('⚪ Etsy: Not configured')
  console.log()
}

// Instagram
if (config.instagram) {
  console.log('✅ Instagram:')
  console.log(`   Access Token: ${maskSecret(config.instagram.accessToken)}`)
  console.log(`   Business Account ID: ${config.instagram.businessAccountId}`)
  console.log()
} else {
  console.log('⚪ Instagram: Not configured')
  console.log()
}

// Facebook
if (config.facebook) {
  console.log('✅ Facebook:')
  console.log(`   Page ID: ${config.facebook.pageId}`)
  console.log(`   Access Token: ${maskSecret(config.facebook.accessToken)}`)
  console.log(`   Catalog ID: ${config.facebook.catalogId}`)
  console.log()
} else {
  console.log('⚪ Facebook: Not configured')
  console.log()
}

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('  PIPELINE OPTIONS')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log()

if (config.options) {
  console.log(`Auto-Publish: ${config.options.autoPublish ? 'Yes' : 'No'}`)
  console.log(`Batch Size: ${config.options.batchSize}`)
  console.log(`T-Shirt Price: $${config.options.tshirtPrice}`)
  console.log(`Hoodie Price: $${config.options.hoodiePrice}`)
}
console.log()

// Test ComfyUI connection
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('  CONNECTION TESTS')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log()

console.log('Testing ComfyUI connection...')
try {
  const response = await fetch(`${config.comfyui.apiUrl}/system_stats`, {
    signal: AbortSignal.timeout(5000)
  })
  if (response.ok) {
    const stats = await response.json()
    console.log('✅ ComfyUI is reachable')
    console.log(`   System: ${stats.system?.os || 'Unknown'}`)
    console.log(`   Device: ${stats.system?.device_type || 'Unknown'}`)
  } else {
    console.log('⚠️  ComfyUI responded but returned an error')
    console.log(`   Status: ${response.status} ${response.statusText}`)
  }
} catch (error: any) {
  console.log('❌ Cannot reach ComfyUI')
  console.log(`   Error: ${error.message}`)
  console.log(`   Make sure ComfyUI is running at: ${config.comfyui.apiUrl}`)
}
console.log()

// Validation summary
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('  VALIDATION SUMMARY')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log()

const issues: string[] = []
const warnings: string[] = []

// Check for placeholder values
if (config.claude.apiKey.includes('your-api-key')) {
  issues.push('Claude API key is still a placeholder')
}

if (enabledPlatforms.length === 0) {
  warnings.push('No platforms enabled - products won\'t be published')
}

if (enabledPlatforms.includes('printify') && !config.printify) {
  issues.push('Printify is enabled but not configured')
}

if (enabledPlatforms.includes('shopify') && !config.shopify) {
  issues.push('Shopify is enabled but not configured')
}

if (config.options?.autoPublish && enabledPlatforms.length === 0) {
  warnings.push('Auto-publish is enabled but no platforms are configured')
}

if (issues.length > 0) {
  console.log('❌ Issues Found:')
  issues.forEach(issue => console.log(`   • ${issue}`))
  console.log()
  console.log('💡 Fix: Run ./setup-keys.sh to configure your API keys')
  console.log()
  process.exit(1)
}

if (warnings.length > 0) {
  console.log('⚠️  Warnings:')
  warnings.forEach(warning => console.log(`   • ${warning}`))
  console.log()
}

console.log('✅ All checks passed!')
console.log()
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('  NEXT STEPS')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log()
console.log('Your configuration is ready! You can now:')
console.log()
console.log('  1. Start the web UI:')
console.log('     npm run dev')
console.log()
console.log('  2. Run a test pipeline:')
console.log('     npx tsx examples/test-pipeline.ts')
console.log()
console.log('  3. Read the documentation:')
console.log('     docs/QUICK_START.md')
console.log()

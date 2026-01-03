# POD Pipeline Setup & Usage Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Pipeline](#running-the-pipeline)
6. [Platform Integrations](#platform-integrations)
7. [Error Handling](#error-handling)
8. [Logging](#logging)
9. [Cloud Storage](#cloud-storage)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The POD (Print-on-Demand) Pipeline is an automated system that:

1. **Generates AI Prompts** using Claude AI
2. **Creates Designs** with ComfyUI (Stable Diffusion)
3. **Saves Images** to local/cloud storage
4. **Creates Products** on Printify
5. **Publishes** to multiple platforms (Shopify, TikTok, Etsy, Instagram, Facebook)

### Architecture

```
User Input → Claude → ComfyUI → Storage → Printify → Multi-Platform Distribution
```

### Key Features

- ✅ **Automated Workflow** - Complete end-to-end automation
- ✅ **Multi-Platform** - Publish to 6+ platforms simultaneously
- ✅ **Robust Error Handling** - Automatic retries with exponential backoff
- ✅ **Cloud Storage** - S3 and GCS support
- ✅ **Structured Logging** - Professional logging system
- ✅ **Configuration Management** - Centralized environment-based config
- ✅ **Batch Processing** - Process multiple designs efficiently

---

## Prerequisites

### Required

- **Node.js 20+**
- **ComfyUI** running locally or on RunPod
- **Anthropic API Key** for Claude
- **Printify Account** (optional but recommended)

### Optional

- **Shopify Store** for e-commerce
- **TikTok Shop** account
- **Etsy Shop** account
- **Instagram Business** account
- **Facebook Page** with Commerce Manager
- **AWS S3** or **Google Cloud Storage** for cloud storage

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ssiens-oss-static_pod
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Set Up ComfyUI

#### Local Setup

```bash
./scripts/setup-comfyui.sh
```

#### RunPod Setup

```bash
./scripts/deploy-runpod.sh
```

---

## Configuration

### 1. Create Environment File

Copy the example configuration:

```bash
cp .env.example .env
```

### 2. Configure Required Settings

Edit `.env` and set the following **required** variables:

```env
# ComfyUI Configuration
COMFYUI_API_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=/data/comfyui/output

# Claude API
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Storage Configuration
STORAGE_TYPE=local
STORAGE_PATH=/data/designs
```

### 3. Configure Optional Platform Integrations

Enable platforms you want to use:

```env
# Enable specific platforms (comma-separated)
ENABLE_PLATFORMS=printify,shopify,etsy

# Printify
PRINTIFY_API_KEY=your-printify-api-key
PRINTIFY_SHOP_ID=your-shop-id

# Shopify
SHOPIFY_STORE_URL=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-access-token

# Etsy
ETSY_API_KEY=your-api-key
ETSY_SHOP_ID=your-shop-id
ETSY_ACCESS_TOKEN=your-oauth-token

# TikTok Shop
TIKTOK_APP_KEY=your-app-key
TIKTOK_APP_SECRET=your-app-secret
TIKTOK_SHOP_ID=your-shop-id
TIKTOK_ACCESS_TOKEN=your-access-token

# Instagram
INSTAGRAM_ACCESS_TOKEN=your-access-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-account-id

# Facebook
FACEBOOK_PAGE_ID=your-page-id
FACEBOOK_ACCESS_TOKEN=your-access-token
FACEBOOK_CATALOG_ID=your-catalog-id
```

### 4. Configure Pipeline Options

```env
# Pipeline Configuration
AUTO_PUBLISH=true
BATCH_SIZE=5
DEFAULT_TSHIRT_PRICE=19.99
DEFAULT_HOODIE_PRICE=34.99
```

---

## Running the Pipeline

### Web UI (Recommended)

```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

**Features:**
- Live preview of generated designs
- Real-time progress tracking
- Interactive editor with zoom/pan
- Product queue monitoring
- Terminal logs view

### Programmatic Usage

```typescript
import { Orchestrator } from './services/orchestrator'
import { loadConfig } from './services/config'

// Load configuration
const config = loadConfig()

// Create orchestrator
const orchestrator = new Orchestrator(config)

// Set up logging callback
orchestrator.setLogger((message, type) => {
  console.log(`[${type}] ${message}`)
})

// Run pipeline
const result = await orchestrator.run({
  theme: 'abstract art',
  style: 'minimalist',
  niche: 'tech enthusiasts',
  productTypes: ['tshirt', 'hoodie'],
  count: 5,
  autoPublish: true
})

console.log('Pipeline Results:', result)
```

---

## Platform Integrations

### Printify

**Setup:**
1. Create account at https://printify.com
2. Get API key from Settings → Connections
3. Note your Shop ID from URL

**Features:**
- Automatic T-shirt creation (Gildan 5000)
- Automatic Hoodie creation (Gildan 18500)
- Support for multiple sizes (S-3XL)
- Auto-publishing to connected sales channels

### Shopify

**Setup:**
1. Create Shopify store
2. Generate Admin API access token
3. Configure API version (default: 2024-01)

**Features:**
- Direct product creation
- Variant management (sizes)
- Collection support
- SEO optimization

### TikTok Shop

**Setup:**
1. Apply for TikTok Shop Seller account
2. Create developer app
3. Get OAuth access token

**Features:**
- Product uploads with images
- SKU management
- Inventory sync
- Product activation

### Etsy

**Setup:**
1. Create Etsy shop
2. Register OAuth application
3. Get API key and access token

**Features:**
- Listing creation (max 13 tags)
- Draft → Active publishing
- Taxonomy support
- Image uploads

### Instagram & Facebook

**Setup:**
1. Convert to Instagram Business Account
2. Create Facebook Page
3. Set up Commerce Manager
4. Generate long-lived access tokens

**Features:**
- Product catalog sync
- Shopping tags
- Multi-image support

---

## Error Handling

The pipeline includes robust error handling with:

### Automatic Retries

- **Network Errors:** Auto-retry with exponential backoff
- **Rate Limits:** Respects `Retry-After` headers
- **Server Errors:** 3 retries with 2s, 4s, 8s delays

### Circuit Breaker

Prevents cascading failures:
- Opens after 5 consecutive failures
- Auto-recovery after 30 seconds

### Error Categories

```typescript
// Retryable errors (will auto-retry)
- Network timeouts
- 429 Rate Limit
- 502/503/504 Server Errors

// Non-retryable errors (immediate fail)
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
```

### Example: Manual Retry

```typescript
import { retryWithBackoff } from './services/utils/errorHandler'

const result = await retryWithBackoff(
  async () => {
    // Your operation here
    return await someAPICall()
  },
  {
    maxRetries: 5,
    initialDelay: 1000,
    maxDelay: 30000,
    onRetry: (error, attempt) => {
      console.log(`Retry attempt ${attempt}: ${error.message}`)
    }
  }
)
```

---

## Logging

### Log Levels

```typescript
import { LogLevel } from './services/utils/logger'

// Available levels
LogLevel.DEBUG    // Detailed debug information
LogLevel.INFO     // General information
LogLevel.WARN     // Warning messages
LogLevel.ERROR    // Error messages
LogLevel.CRITICAL // Critical errors
```

### Usage

```typescript
import { getLogger } from './services/utils/logger'

const logger = getLogger()

// Set log level
logger.setLevel(LogLevel.DEBUG)

// Log messages
logger.debug('Debug message', { context: 'value' })
logger.info('Info message')
logger.warn('Warning message')
logger.error('Error occurred', error, { additionalContext: 'data' })
logger.critical('Critical failure', error)

// Get log history
const history = logger.getHistory()

// Export logs
const jsonLogs = logger.exportJSON()
const textLogs = logger.exportText()
```

### Performance Logging

```typescript
import { PerformanceLogger } from './services/utils/logger'

const perfLogger = new PerformanceLogger()

// Manual timing
perfLogger.start('image-generation')
// ... operation ...
const duration = perfLogger.end('image-generation')

// Automatic timing
const result = await perfLogger.measure(
  'api-call',
  async () => {
    return await apiCall()
  },
  { endpoint: '/prompt' }
)
```

---

## Cloud Storage

### Local Storage

```env
STORAGE_TYPE=local
STORAGE_PATH=/data/designs
```

### AWS S3

```env
STORAGE_TYPE=s3
STORAGE_PATH=designs
AWS_S3_BUCKET=my-pod-designs
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

**Note:** Install AWS SDK for production:

```bash
npm install @aws-sdk/client-s3
```

### Google Cloud Storage

```env
STORAGE_TYPE=gcs
STORAGE_PATH=designs
GCS_BUCKET=my-pod-designs
GCS_PROJECT_ID=my-project
GCS_KEY_FILENAME=/path/to/service-account-key.json
```

**Note:** Install GCS SDK for production:

```bash
npm install @google-cloud/storage
```

---

## Troubleshooting

### ComfyUI Connection Failed

**Problem:** `ECONNREFUSED` when connecting to ComfyUI

**Solutions:**
1. Check ComfyUI is running: `curl http://localhost:8188/system_stats`
2. Verify `COMFYUI_API_URL` in `.env`
3. Check firewall settings
4. For RunPod: Ensure correct pod ID and API key

### Claude API Errors

**Problem:** `401 Unauthorized` from Claude API

**Solutions:**
1. Verify `ANTHROPIC_API_KEY` is correct
2. Check API key has not expired
3. Ensure account has credits

### Printify Product Creation Failed

**Problem:** Products not creating on Printify

**Solutions:**
1. Verify API key and Shop ID
2. Check blueprint ID (3 for T-shirts, 165 for Hoodies)
3. Ensure shop is active and connected
4. Check image URL is accessible

### Rate Limit Errors

**Problem:** `429 Too Many Requests`

**Solutions:**
- The pipeline automatically handles rate limits
- Check platform-specific rate limits in their documentation
- Reduce `BATCH_SIZE` in configuration
- Add delays between operations

### Image Upload Failures

**Problem:** Images not uploading to platforms

**Solutions:**
1. Check image URL is publicly accessible
2. Verify image format (PNG/JPG)
3. Ensure image size is within platform limits
4. Check network connectivity

### Configuration Errors

**Problem:** `ConfigurationError: XXXX is required`

**Solutions:**
1. Check `.env` file exists
2. Verify all required variables are set
3. Ensure no typos in variable names
4. Restart application after `.env` changes

---

## Best Practices

### 1. Start Small

Begin with a single platform and low batch size:

```env
ENABLE_PLATFORMS=printify
BATCH_SIZE=1
```

### 2. Test Mode

Use manual publishing initially:

```env
AUTO_PUBLISH=false
```

### 3. Monitor Logs

Enable debug logging for troubleshooting:

```typescript
logger.setLevel(LogLevel.DEBUG)
```

### 4. Backup Configuration

Keep a backup of your `.env` file in a secure location.

### 5. Use Cloud Storage

For production, use S3 or GCS for reliability and scalability.

### 6. Set Reasonable Timeouts

```env
COMFYUI_TIMEOUT=300000  # 5 minutes
```

### 7. Monitor Costs

- ComfyUI/RunPod GPU costs
- Claude API usage
- Storage costs (S3/GCS)
- Platform fees

---

## API Reference

### Configuration Manager

```typescript
import { loadConfig, getConfigManager } from './services/config'

// Load configuration
const config = loadConfig()

// Get config manager
const manager = getConfigManager()

// Check if platform is enabled
if (manager.isPlatformEnabled('shopify')) {
  // Platform is enabled
}

// Get enabled platforms
const platforms = manager.getEnabledPlatforms()

// Print configuration summary
manager.printSummary()
```

### Orchestrator

```typescript
import { Orchestrator } from './services/orchestrator'

const orchestrator = new Orchestrator(config)

// Set logger callback
orchestrator.setLogger((message, type) => {
  console.log(`[${type}] ${message}`)
})

// Run pipeline
const result = await orchestrator.run({
  prompt: 'optional custom prompt',
  theme: 'nature',
  style: 'watercolor',
  niche: 'outdoor enthusiasts',
  productTypes: ['tshirt', 'hoodie'],
  count: 3,
  autoPublish: true
})

// Get statistics
const stats = await orchestrator.getStats()
```

---

## Support

For issues and questions:

1. Check this documentation
2. Review error logs
3. Check platform-specific documentation
4. Open an issue on GitHub

---

## License

See LICENSE file for details.

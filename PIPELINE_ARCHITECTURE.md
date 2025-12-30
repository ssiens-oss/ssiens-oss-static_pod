# POD Automation Pipeline Architecture

## Overview

Complete automation pipeline for AI-generated print-on-demand products with multi-platform distribution.

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       POD AUTOMATION PIPELINE                            │
└─────────────────────────────────────────────────────────────────────────┘

1. DESIGN GENERATION (ComfyUI + Claude)
   ├── Claude generates creative prompts
   ├── Chrome automation drives ComfyUI interface
   ├── ComfyUI generates AI images
   └── Auto-save to local storage

2. PRODUCT CREATION (Printify)
   ├── Upload generated designs to Printify
   ├── Create products (T-shirts, Hoodies)
   ├── Set pricing and variants
   └── Publish to Printify catalog

3. STORE PUBLISHING (Shopify)
   ├── Sync products from Printify to Shopify
   ├── Add product descriptions & SEO
   ├── Set inventory and pricing
   └── Publish to online store

4. MULTI-PLATFORM DISTRIBUTION
   ├── TikTok Shop: Create product listings
   ├── Etsy: List products in shop
   ├── Instagram Shopping: Tag products in posts
   └── Facebook Shop: Sync catalog
```

## Components

### 1. ComfyUI Integration (`services/comfyui.ts`)
- REST API client for ComfyUI backend
- WebSocket connection for real-time generation status
- Queue management for batch processing
- Image retrieval and storage

### 2. Claude Prompting Engine (`services/claudePrompting.ts`)
- Claude API integration
- Prompt template system
- Chrome/Playwright automation
- ComfyUI workflow automation

### 3. Auto-Save System (`services/storage.ts`)
- Local file system storage
- Cloud storage integration (S3, Google Cloud Storage)
- Image versioning and metadata
- Duplicate detection

### 4. Printify Integration (`services/printify.ts`)
- Product creation API
- Blueprint management (T-shirts: 3, Hoodies: 165)
- Variant configuration (sizes, colors)
- Pricing rules engine
- Publish products to catalog

### 5. Shopify Integration (`services/shopify.ts`)
- Product import from Printify
- SEO optimization
- Inventory synchronization
- Collection management
- Product variant mapping

### 6. Multi-Platform Distribution

#### TikTok Shop (`services/platforms/tiktok.ts`)
- TikTok Shop API integration
- Product catalog sync
- Live shopping integration
- Analytics tracking

#### Etsy (`services/platforms/etsy.ts`)
- Etsy API v3 integration
- Listing creation and management
- Shipping profiles
- Shop section organization

#### Instagram (`services/platforms/instagram.ts`)
- Meta Graph API integration
- Shopping catalog sync
- Product tagging in posts
- Instagram Shop management

#### Facebook Shop (`services/platforms/facebook.ts`)
- Meta Commerce API integration
- Catalog sync from Shopify
- Product sets and collections
- Ad integration

### 7. Orchestration Engine (`services/orchestrator.ts`)
- Pipeline state management
- Error handling and retries
- Parallel processing
- Progress tracking
- Webhook notifications

## Configuration

### Environment Variables

```bash
# ComfyUI
COMFYUI_API_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=/path/to/comfyui/output

# Claude
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Chrome Automation
CHROME_HEADLESS=false
CHROME_USER_DATA_DIR=/path/to/chrome/profile

# Storage
STORAGE_TYPE=local  # local, s3, gcs
STORAGE_PATH=/data/designs
AWS_S3_BUCKET=my-pod-designs  # if using S3

# Printify
PRINTIFY_API_KEY=...
PRINTIFY_SHOP_ID=...

# Shopify
SHOPIFY_STORE_URL=mystore.myshopify.com
SHOPIFY_ACCESS_TOKEN=...
SHOPIFY_API_VERSION=2024-01

# TikTok Shop
TIKTOK_APP_KEY=...
TIKTOK_APP_SECRET=...
TIKTOK_SHOP_ID=...

# Etsy
ETSY_API_KEY=...
ETSY_SHOP_ID=...
ETSY_OAUTH_TOKEN=...

# Instagram
INSTAGRAM_ACCESS_TOKEN=...
INSTAGRAM_BUSINESS_ACCOUNT_ID=...

# Facebook
FACEBOOK_PAGE_ID=...
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_CATALOG_ID=...
```

### Product Configuration (`config/products.json`)

```json
{
  "products": [
    {
      "type": "tshirt",
      "printify_blueprint_id": 3,
      "printify_provider_id": 99,
      "variants": ["S", "M", "L", "XL", "2XL", "3XL"],
      "colors": ["Black", "White", "Navy", "Heather Grey"],
      "base_price": 19.99,
      "markup_percentage": 40
    },
    {
      "type": "hoodie",
      "printify_blueprint_id": 165,
      "printify_provider_id": 99,
      "variants": ["S", "M", "L", "XL", "2XL"],
      "colors": ["Black", "Navy", "Heather Grey"],
      "base_price": 34.99,
      "markup_percentage": 45
    }
  ]
}
```

## Installation

### Prerequisites

1. **Node.js 20+**
2. **ComfyUI** running locally or remote
3. **Chrome/Chromium** for automation
4. **Docker** (optional, for containerized deployment)

### Setup Steps

```bash
# 1. Install dependencies
npm install

# 2. Set up ComfyUI
./scripts/setup-comfyui.sh

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Initialize platform integrations
npm run setup:platforms

# 5. Run the pipeline
npm run pipeline:start
```

## Usage

### Single Product Run

```bash
npm run pipeline:single -- \
  --prompt "Minimalist mountain landscape sunset" \
  --products "tshirt,hoodie" \
  --platforms "shopify,etsy"
```

### Batch Processing

```bash
npm run pipeline:batch -- \
  --prompts-file prompts.txt \
  --products "tshirt,hoodie" \
  --platforms "all" \
  --count 10
```

### Custom Workflow

```typescript
import { Orchestrator } from './services/orchestrator'

const orchestrator = new Orchestrator({
  comfyui: { apiUrl: 'http://localhost:8188' },
  claude: { apiKey: process.env.ANTHROPIC_API_KEY },
  platforms: ['shopify', 'etsy', 'tiktok']
})

await orchestrator.run({
  prompt: 'Abstract geometric patterns',
  productTypes: ['tshirt', 'hoodie'],
  count: 5,
  autoPublish: true
})
```

## Monitoring & Logging

- Real-time progress in web UI (http://localhost:5173)
- Logs stored in `logs/` directory
- Webhook notifications on completion/errors
- Integration with monitoring services (optional)

## Error Handling

- Automatic retry with exponential backoff
- Failed items queued for manual review
- Error notifications via email/webhook
- Partial success handling (some platforms may fail)

## Security

- API keys stored in environment variables
- OAuth tokens encrypted at rest
- Rate limiting for all API calls
- Audit logging for all operations

## Performance

- Parallel image generation (multiple ComfyUI workers)
- Batch API calls where supported
- Image optimization before upload
- Caching for repeated operations

## Future Enhancements

1. **AI Prompt Optimization**: Learn from successful designs
2. **A/B Testing**: Test multiple designs, promote best performers
3. **Trend Analysis**: Scrape trending topics for prompt generation
4. **Auto-pricing**: Dynamic pricing based on demand
5. **Analytics Dashboard**: Track sales across all platforms

# POD Pipeline - Quick Start Guide

Get up and running with the POD Pipeline in under 5 minutes!

## Prerequisites

- Node.js 20+
- ComfyUI running (local or RunPod)
- Anthropic API key

## Installation

```bash
# 1. Install dependencies
npm install

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env and add your API keys
nano .env
```

## Minimum Configuration

Edit `.env` with these **required** settings:

```env
# ComfyUI
COMFYUI_API_URL=http://localhost:8188

# Claude
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Storage
STORAGE_TYPE=local
STORAGE_PATH=./designs

# Enable platforms (start with just Printify)
ENABLE_PLATFORMS=printify

# Printify (optional for testing without real products)
PRINTIFY_API_KEY=your-key-here
PRINTIFY_SHOP_ID=your-shop-id
```

## Run the Pipeline

### Option 1: Web UI (Recommended)

```bash
npm run dev
```

Open http://localhost:5173

### Option 2: Command Line

```typescript
// test-pipeline.ts
import { Orchestrator } from './services/orchestrator'
import { loadConfig } from './services/config'

const config = loadConfig()
const orchestrator = new Orchestrator(config)

orchestrator.setLogger((msg, type) => console.log(`[${type}] ${msg}`))

const result = await orchestrator.run({
  theme: 'cyberpunk',
  style: 'neon',
  niche: 'gamers',
  productTypes: ['tshirt'],
  count: 1,
  autoPublish: false  // Set to false for testing
})

console.log('Results:', result)
```

Run it:

```bash
npx tsx test-pipeline.ts
```

## What Happens?

1. **Claude generates** a creative prompt for your theme
2. **ComfyUI creates** the design image
3. **Storage saves** the image locally (or to S3/GCS)
4. **Printify creates** T-shirt/Hoodie products
5. **Platforms publish** to enabled stores (if `AUTO_PUBLISH=true`)

## Expected Output

```
[INFO] 🚀 Starting POD automation pipeline...
[INFO] 📝 Generating creative prompts with Claude...
[SUCCESS] ✓ Generated 1 creative prompts
[INFO] 🎨 Generating AI images with ComfyUI...
[SUCCESS] ✓ Generated 1 images
[INFO] 💾 Saving images to storage...
[SUCCESS] ✓ Saved 1 images
[INFO] 📦 Creating tshirt products for: Cyberpunk Neon Dreams
[SUCCESS] ✓ Created 1 products
[SUCCESS] ✅ Pipeline complete! Created 1 products in 45.23s
```

## Next Steps

### 1. Enable More Platforms

Add to `.env`:

```env
ENABLE_PLATFORMS=printify,shopify,etsy

# Shopify
SHOPIFY_STORE_URL=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxx

# Etsy
ETSY_API_KEY=xxx
ETSY_SHOP_ID=xxx
ETSY_ACCESS_TOKEN=xxx
```

### 2. Enable Auto-Publishing

```env
AUTO_PUBLISH=true
```

### 3. Batch Processing

```env
BATCH_SIZE=5
```

Then run with multiple designs:

```typescript
const result = await orchestrator.run({
  theme: 'nature',
  style: 'minimalist',
  productTypes: ['tshirt', 'hoodie'],
  count: 5,  // Generate 5 designs
  autoPublish: true
})
```

### 4. Use Cloud Storage

**AWS S3:**

```env
STORAGE_TYPE=s3
AWS_S3_BUCKET=my-designs
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
```

**Google Cloud Storage:**

```env
STORAGE_TYPE=gcs
GCS_BUCKET=my-designs
GCS_PROJECT_ID=my-project
GCS_KEY_FILENAME=/path/to/key.json
```

### 5. Customize Prices

```env
DEFAULT_TSHIRT_PRICE=24.99
DEFAULT_HOODIE_PRICE=39.99
```

## Common Issues

### "ComfyUI connection failed"

Check ComfyUI is running:

```bash
curl http://localhost:8188/system_stats
```

### "Claude API error"

Verify your API key:

```bash
# Check it starts with sk-ant-
echo $ANTHROPIC_API_KEY
```

### "Configuration error"

Make sure all required variables are set in `.env`:

- `COMFYUI_API_URL`
- `ANTHROPIC_API_KEY`
- `STORAGE_TYPE`
- `STORAGE_PATH`

## Testing Without Real Products

Set `AUTO_PUBLISH=false` and leave platform keys empty to test the pipeline without creating real products:

```env
AUTO_PUBLISH=false
ENABLE_PLATFORMS=
```

This will generate designs and save them locally without publishing.

## Performance Tips

### Faster Generation

- Use local ComfyUI instead of RunPod
- Reduce `steps` in workflow (default: 20)
- Use smaller image sizes (512x512 vs 1024x1024)

### Cost Optimization

- **Claude:** ~$0.01 per design
- **ComfyUI (RunPod):** ~$0.05 per design
- **Total:** ~$0.06 per design

Reduce costs by:
- Batching designs
- Using local ComfyUI
- Reusing prompts

## Documentation

- **Full Guide:** [POD_PIPELINE_GUIDE.md](./POD_PIPELINE_GUIDE.md)
- **Configuration:** See `.env.example`
- **Platform Setup:** Check platform-specific sections in full guide

## Getting Help

1. Check logs for detailed error messages
2. Enable debug logging: `logger.setLevel(LogLevel.DEBUG)`
3. Review configuration: `manager.printSummary()`
4. Check platform documentation

## What's Next?

Explore advanced features:

- **Batch Processing** - Process multiple designs
- **Multi-Platform** - Publish to 6+ platforms
- **Cloud Storage** - Use S3/GCS for scalability
- **Custom Workflows** - Customize ComfyUI workflows
- **Webhooks** - Get notifications on completion
- **Error Handling** - Auto-retries and circuit breakers

Happy designing! 🎨

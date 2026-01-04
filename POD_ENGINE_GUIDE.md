# Pod Engine Pipeline Guide

Complete automation pipeline for AI-generated Print-on-Demand products with ComfyUI, RunPod, proofing, and multi-platform publishing.

## 🚀 Overview

The Pod Engine Pipeline is a comprehensive system that automates the entire process of creating and publishing POD products:

1. **Generation** - Create AI art with ComfyUI (local or RunPod)
2. **Proofing** - Review and approve generated assets
3. **Publishing** - Automatically create products on multiple platforms
4. **Monitoring** - Real-time pipeline status and logs

## 📋 Features

### Core Pipeline
- ✅ **AI Image Generation** with Claude + ComfyUI
- ✅ **RunPod Integration** for cloud GPU acceleration
- ✅ **Local Save from RunPod** - Automatically sync outputs locally
- ✅ **Proofing System** - Manual or auto-approval workflow
- ✅ **Multi-Platform Publishing** - Printify, Shopify, TikTok, Etsy, Instagram, Facebook
- ✅ **Real-time Monitoring** - Live logs and progress tracking
- ✅ **Batch Processing** - Generate multiple designs in one run

### Services

#### PodEngine (`services/podEngine.ts`)
Core orchestration engine that manages the entire pipeline workflow.

**Key Methods:**
- `run(request)` - Execute complete pipeline
- `setLogger(callback)` - Subscribe to log messages
- `setStatusCallback(callback)` - Subscribe to status updates
- `getAssets()` - Get all generated assets
- `getProducts()` - Get all published products
- `updateAssetProof(assetId, status, notes)` - Manually approve/reject assets

#### ProofingService (`services/proofing.ts`)
Manages content review and approval workflow.

**Features:**
- Manual review queue
- Auto-approval mode
- Approval/rejection tracking
- Custom review notes

#### RunPodService (`services/runpod.ts`)
Handles RunPod pod interactions and file syncing.

**Features:**
- Pod status monitoring
- File listing and downloading
- ComfyUI output syncing
- Command execution (SSH)

#### StorageService (`services/storage.ts`)
Enhanced with RunPod local save support.

**Storage Types:**
- `local` - Local filesystem
- `s3` - AWS S3 (placeholder)
- `gcs` - Google Cloud Storage (placeholder)
- `runpod` - RunPod with local sync

## 🎯 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create a `.env` file with your API keys:

```env
# Core Services
ANTHROPIC_API_KEY=your_claude_api_key
COMFYUI_API_URL=http://localhost:8188

# Storage
STORAGE_TYPE=local
STORAGE_BASE_PATH=./pod-output

# RunPod (Optional)
RUNPOD_API_KEY=your_runpod_api_key
RUNPOD_POD_ID=your_pod_id
RUNPOD_MODE=false

# Publishing Platforms
PRINTIFY_API_KEY=your_printify_key
PRINTIFY_SHOP_ID=your_shop_id

SHOPIFY_STORE_URL=your_store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_access_token

# Pricing
TSHIRT_PRICE=19.99
HOODIE_PRICE=34.99
```

### 3. Start Pod Engine

```bash
npm run pod-engine
```

This will start the Pod Engine GUI at `http://localhost:5174`

### 4. Configure Pipeline

In the GUI:

1. **Generate Tab**
   - Set theme, style, and niche
   - Enter custom prompt (optional)
   - Choose number of designs
   - Select product types

2. **Proof Tab**
   - Enable/disable auto-approval
   - Configure manual review workflow

3. **Publish Tab**
   - Select enabled platforms
   - Set product pricing
   - Enable/disable auto-publish

4. **Settings Tab**
   - Configure ComfyUI URL
   - Enable RunPod mode
   - Enter RunPod credentials
   - Test connection

### 5. Run Pipeline

Click "Run Pipeline" to start the automated workflow!

## 🔧 Usage Examples

### Basic Pipeline Run

```typescript
import { PodEngine } from './services/podEngine'

const engine = new PodEngine({
  comfyui: {
    apiUrl: 'http://localhost:8188',
    outputDir: './comfyui-output'
  },
  claude: {
    apiKey: process.env.ANTHROPIC_API_KEY
  },
  storage: {
    type: 'local',
    basePath: './pod-output'
  },
  proofing: {
    enabled: true,
    autoApprove: false
  }
})

// Set up logging
engine.setLogger((message, type) => {
  console.log(`[${type}] ${message}`)
})

// Set up status updates
engine.setStatusCallback((status) => {
  console.log(`Stage: ${status.stage}, Progress: ${status.progress}%`)
})

// Run pipeline
const result = await engine.run({
  theme: 'Abstract Art',
  style: 'Digital',
  niche: 'Modern',
  productTypes: ['tshirt', 'hoodie'],
  count: 3,
  autoProof: false,
  autoPublish: true
})

console.log(`Generated ${result.assets.length} assets`)
console.log(`Published ${result.products.length} products`)
```

### RunPod Mode

```typescript
const engine = new PodEngine({
  comfyui: {
    apiUrl: 'https://pod-id.runpod.io:8188',
    outputDir: '/workspace/ComfyUI/output',
    runpodMode: true,
    runpodApiKey: process.env.RUNPOD_API_KEY,
    runpodPodId: process.env.RUNPOD_POD_ID
  },
  storage: {
    type: 'runpod',
    basePath: './local-sync',
    runpodSyncEnabled: true,
    runpodConfig: {
      apiKey: process.env.RUNPOD_API_KEY,
      podId: process.env.RUNPOD_POD_ID,
      outputDir: '/workspace/ComfyUI/output',
      localSyncDir: './runpod-sync'
    }
  },
  // ... other config
})

// Run pipeline - images will be generated on RunPod and synced locally
const result = await engine.run({
  theme: 'Cyberpunk',
  productTypes: ['tshirt'],
  count: 5
})
```

### Manual Proofing Workflow

```typescript
// Enable proofing without auto-approve
const engine = new PodEngine({
  // ... config
  proofing: {
    enabled: true,
    autoApprove: false,
    requireManualReview: true
  }
})

// Run pipeline (will pause at proofing stage)
await engine.run({
  theme: 'Nature',
  productTypes: ['poster'],
  count: 10,
  autoProof: false  // Manual review required
})

// Review assets
const assets = engine.getAssets()

// Approve specific assets
await engine.updateAssetProof(assets[0].id, 'approved', 'Great design!')
await engine.updateAssetProof(assets[1].id, 'rejected', 'Colors too dark')

// Continue with approved assets...
```

### Batch Processing

```typescript
// Process multiple themes in sequence
const themes = ['Minimalist', 'Vintage', 'Abstract', 'Geometric']

for (const theme of themes) {
  const result = await engine.run({
    theme,
    style: 'Digital',
    productTypes: ['tshirt'],
    count: 5,
    autoProof: true,
    autoPublish: true
  })

  console.log(`${theme}: ${result.products.length} products published`)
}
```

## 📊 Pipeline Stages

### 1. Generating
- Generate creative prompts with Claude AI
- Create images using ComfyUI
- Save to local storage or sync from RunPod

### 2. Proofing
- Review generated assets
- Approve or reject based on quality
- Add notes for rejected items

### 3. Publishing
- Create products on enabled platforms
- Upload images and metadata
- Set pricing and variants
- Publish or save as draft

### 4. Completed
- All products published
- Statistics available
- Assets and products accessible

## 🎨 GUI Features

### Left Sidebar
- **Tab Navigation** - Generate, Proof, Publish, Settings
- **Pipeline Controls** - Theme, style, count, product types
- **Platform Selection** - Enable/disable platforms
- **Pricing Configuration** - Set product prices
- **RunPod Settings** - API key, pod ID, connection test

### Main Area
- **Asset Gallery** - Visual grid of generated images
- **Proof Status** - Pending, Approved, Rejected badges
- **Quick Actions** - Approve/reject buttons
- **Product List** - Published products with status

### Bottom Panel
- **Live Logs** - Real-time pipeline messages
- **Progress Bar** - Visual progress indicator
- **Statistics** - Generated, approved, published counts

## 🔌 RunPod Integration

### Setup

1. Create a RunPod pod with ComfyUI installed
2. Get your API key from RunPod dashboard
3. Note your pod ID
4. Configure in Settings tab

### Features

- **Connection Testing** - Verify pod is accessible
- **File Syncing** - Download outputs to local machine
- **Status Monitoring** - Check pod running state
- **Remote Execution** - Generate on GPU, save locally

### Local Save Workflow

1. Pipeline generates images on RunPod
2. Images saved to pod's output directory
3. Storage service automatically syncs files locally
4. Local copies used for proofing and publishing
5. Original RunPod paths preserved in metadata

## 🚀 Deployment

### Local Development

```bash
npm run pod-engine
```

### Production Build

```bash
npm run build:podengine
```

Outputs to `dist-podengine/`

### RunPod Deployment

Deploy the entire pipeline to RunPod:

```bash
# Build Docker image
docker build -f Dockerfile.podengine -t pod-engine .

# Push to registry
docker push your-registry/pod-engine

# Deploy to RunPod
# Use RunPod dashboard to create pod from image
```

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude API key | Yes |
| `COMFYUI_API_URL` | ComfyUI endpoint | Yes |
| `STORAGE_TYPE` | Storage backend | Yes |
| `STORAGE_BASE_PATH` | Local storage path | Yes |
| `RUNPOD_API_KEY` | RunPod API key | No |
| `RUNPOD_POD_ID` | RunPod pod ID | No |
| `PRINTIFY_API_KEY` | Printify API key | No |
| `SHOPIFY_ACCESS_TOKEN` | Shopify token | No |

## 🛠️ Troubleshooting

### ComfyUI Connection Failed
- Verify ComfyUI is running
- Check API URL is correct
- Ensure port 8188 is accessible

### RunPod Connection Failed
- Verify API key is valid
- Check pod ID is correct
- Ensure pod is running

### Images Not Syncing from RunPod
- Check pod has outputs in directory
- Verify local sync directory exists
- Ensure sufficient disk space

### Products Not Publishing
- Verify platform API keys are correct
- Check platform service is enabled
- Review logs for specific errors

## 🎯 Best Practices

1. **Start Small** - Test with 1-2 designs first
2. **Use Proofing** - Always review before publishing
3. **Configure Pricing** - Set appropriate margins
4. **Monitor Logs** - Watch for errors in real-time
5. **Backup Assets** - Save generated images locally
6. **Test Platforms** - Verify each platform works individually

## 📚 API Reference

See inline documentation in:
- `services/podEngine.ts` - Main pipeline orchestrator
- `services/proofing.ts` - Proofing workflow
- `services/runpod.ts` - RunPod integration
- `services/storage.ts` - Storage with RunPod sync

## 🆘 Support

For issues or questions:
1. Check logs in the GUI terminal
2. Review error messages
3. Verify configuration
4. Open an issue on GitHub

---

**Built with:** React, TypeScript, Vite, TailwindCSS, ComfyUI, RunPod, Claude AI

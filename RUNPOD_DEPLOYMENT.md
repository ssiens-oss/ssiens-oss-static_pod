# RunPod Deployment Guide

## ✅ Current Status

The POD pipeline is now **fully configured** and ready for deployment to RunPod. All services are implemented and TypeScript compilation is successful.

## 🚀 Deployment Steps

### 1. Push Docker Image to RunPod

The `Dockerfile.runpod` is configured and ready. To deploy:

```bash
# Build and push to Docker Hub (or use RunPod's template system)
docker build -f Dockerfile.runpod -t your-dockerhub-username/pod-studio:latest .
docker push your-dockerhub-username/pod-studio:latest
```

Or use the existing deployment script:
```bash
./deploy.sh
```

### 2. Configure RunPod Pod

1. **Create new Pod** on RunPod with:
   - GPU: A4000 or better (for ComfyUI)
   - Disk: 50GB minimum
   - Port 8188 exposed (ComfyUI)
   - Port 3000 exposed (Web UI)

2. **SSH into RunPod**:
   ```bash
   ssh <pod-id>@ssh.runpod.io -i ~/.ssh/id_ed25519
   ```

3. **Navigate to app directory**:
   ```bash
   cd /workspace/app
   ```

### 3. Install Dependencies

```bash
# Install all Node.js dependencies
npm install

# Verify installation
npm list @anthropic-ai/sdk axios dotenv
```

### 4. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit with your API keys
nano .env
```

**Required Variables**:
```bash
# REQUIRED
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
COMFYUI_API_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=/workspace/ComfyUI/output

# STORAGE
STORAGE_TYPE=local
STORAGE_PATH=/data/designs

# PRINTIFY (optional but recommended)
PRINTIFY_API_KEY=your-printify-jwt-token
PRINTIFY_SHOP_ID=your-shop-id

# SHOPIFY (optional)
SHOPIFY_STORE_URL=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_API_VERSION=2024-01
```

### 5. Start ComfyUI

```bash
cd /workspace/ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188 &

# Verify it's running
curl http://localhost:8188/system_stats
```

### 6. Test the Pipeline

#### Test Single Design
```bash
cd /workspace/app

# Test without publishing (dry run)
npm run pipeline:single -- --theme="cyberpunk cats" --no-publish

# Test with auto-publish (requires valid API keys)
npm run pipeline:single -- --theme="retro gaming"
```

#### Test Batch Generation
```bash
# Generate 5 designs
npm run pipeline:batch -- 5

# Generate 10 designs with auto-publish
npm run pipeline:batch -- 10
```

## 📦 What's Included

### Core Services (TypeScript)

- ✅ **Orchestrator** (`services/orchestrator.ts`) - Main pipeline coordinator
- ✅ **ComfyUI Service** (`services/comfyui.ts`) - AI image generation
- ✅ **Claude Prompting** (`services/claudePrompting.ts`) - Creative prompt generation
- ✅ **Storage Service** (`services/storage.ts`) - Image storage (local/S3/GCS)
- ✅ **Printify Service** (`services/printify.ts`) - Product creation
- ✅ **Shopify Service** (`services/shopify.ts`) - Shopify integration

### Platform Integrations

- ✅ **TikTok Shop** (`services/platforms/tiktok.ts`)
- ✅ **Etsy** (`services/platforms/etsy.ts`)
- ✅ **Instagram Shopping** (`services/platforms/instagram.ts`)
- ✅ **Facebook Shop** (`services/platforms/facebook.ts`)

### Pipeline Runners

- ✅ **Single Design** (`scripts/run-pipeline.js`) - Generate one design
- ✅ **Batch Mode** (`scripts/run-batch.js`) - Generate multiple designs

### Auto-Download Scripts (Local Machine)

- ✅ **One-time Download** (`scripts/download-images.sh`)
- ✅ **Auto-Sync** (`scripts/auto-download-images.sh`)

## 🔧 Dependencies

All dependencies are now properly configured in `package.json`:

**Runtime Dependencies**:
- `@anthropic-ai/sdk` - Claude AI API
- `axios` - HTTP requests
- `dotenv` - Environment variables
- `form-data` - Multipart uploads

**Development Dependencies**:
- `tsx` - TypeScript execution (no compilation needed!)
- `typescript` - Type checking
- `@types/node` - Node.js types

## 🎯 Pipeline Features

### Automatic Workflow

1. **Prompt Generation** → Claude generates creative prompts based on theme/style
2. **Image Generation** → ComfyUI creates AI artwork
3. **Storage** → Images saved to `/data/designs` (or S3/GCS)
4. **Product Creation** → Automatic T-shirt and Hoodie products on Printify
5. **Multi-Platform Publishing** → Shopify, TikTok, Etsy, Instagram, Facebook

### Command Options

```bash
# Specific theme
npm run pipeline:single -- --theme="vintage music posters"

# Multiple designs
npm run pipeline:single -- --count=3

# Only T-shirts
npm run pipeline:single -- --products=tshirt

# Dry run (no publishing)
npm run pipeline:single -- --no-publish

# Combine options
npm run pipeline:single -- --theme="space art" --count=5 --products=tshirt,hoodie
```

## 📊 Monitoring

### Check Pipeline Status

```bash
# View logs
tail -f /var/log/pod-pipeline.log

# Check created products
ls -la /data/designs/

# View ComfyUI queue
curl http://localhost:8188/queue
```

### Health Checks

```bash
# Test ComfyUI
curl http://localhost:8188/system_stats

# Test Printify connection
curl -H "Authorization: Bearer $PRINTIFY_API_KEY" \
  https://api.printify.com/v1/shops.json
```

## 🔄 Auto-Download to Local Machine

While the pipeline runs on RunPod, you can automatically download images to your local machine:

```bash
# On your LOCAL machine
export RUNPOD_SSH_HOST="<pod-id>@ssh.runpod.io"
export REMOTE_PATH="/data/designs"

# Start auto-sync (runs continuously)
./scripts/auto-download-images.sh
```

Images will appear in `~/POD-Designs/` automatically!

## 🤖 Automated Daily Batches

Set up a cron job on RunPod to generate designs daily:

```bash
# Edit crontab
crontab -e

# Add this line (runs at 3 AM daily, generates 10 designs)
0 3 * * * cd /workspace/app && npm run pipeline:batch -- 10 >> /var/log/pod-pipeline.log 2>&1
```

## 📝 Next Steps

1. **Deploy to RunPod** using `Dockerfile.runpod`
2. **Configure environment variables** with your API keys
3. **Test the pipeline** with a single design
4. **Scale up** to batch mode
5. **Set up auto-download** on your local machine
6. **Configure cron job** for daily automation

## 🐛 Troubleshooting

### "Module not found" errors
```bash
cd /workspace/app
rm -rf node_modules package-lock.json
npm install
```

### "ANTHROPIC_API_KEY is required"
Make sure `.env` exists and has valid API keys:
```bash
cat .env | grep ANTHROPIC_API_KEY
```

### "ComfyUI not responding"
```bash
# Check if running
curl http://localhost:8188/system_stats

# Restart if needed
cd /workspace/ComfyUI
pkill -f main.py
python3 main.py --listen 0.0.0.0 --port 8188 &
```

### TypeScript errors
All TypeScript is compiled on-the-fly with `tsx`. No build step needed!

## 📚 Documentation

- `QUICK_START.md` - Quick start guide for daily usage
- `SETUP_GUIDE.md` - Detailed setup instructions
- `PIPELINE_ARCHITECTURE.md` - Technical architecture
- `AUTO_DOWNLOAD_GUIDE.md` - Local sync setup

---

**Status**: ✅ Ready for production deployment
**Last Updated**: 2025-12-30

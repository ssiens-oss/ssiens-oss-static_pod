# 🚀 Production Deployment Guide

Complete guide for deploying StaticWaves POD Studio to RunPod with Printify integration.

## 📋 Prerequisites

Before deploying, ensure you have:

### Required Accounts

1. **Anthropic Claude API** ([Get API Key](https://console.anthropic.com/))
   - Used for AI prompt generation and product descriptions
   - Cost: ~$0.01 per design

2. **Printify Account** ([Sign Up](https://printify.com/))
   - Print-on-demand product creation
   - Get API key from: https://printify.com/app/account/api
   - Find Shop ID in your dashboard

3. **RunPod Account** ([Sign Up](https://runpod.io/))
   - GPU cloud hosting for AI image generation
   - Get API key from: https://www.runpod.io/console/user/settings
   - Cost: ~$0.50-1.00/hour for RTX A4000

4. **DockerHub Account** ([Sign Up](https://hub.docker.com/))
   - For pushing your container image
   - Free tier available

### Optional Integrations

- **Shopify Store** - Multi-channel e-commerce
- **TikTok Shop** - Social commerce
- **Etsy Shop** - Marketplace listing
- **Instagram Business** - Social shopping
- **Facebook Page** - Commerce manager

---

## ⚙️ Step 1: Local Setup

### Clone and Install

```bash
# Clone repository
git clone <your-repo-url>
cd ssiens-oss-static_pod

# Install dependencies
npm install
```

### Configure Environment

Run the interactive setup script:

```bash
./scripts/setup-env.sh
```

This will guide you through configuring:
- ✅ Claude API key
- ✅ Printify API credentials
- ⚙️ Optional platform integrations
- 💰 Product pricing
- 🚀 Auto-publish settings

**Or manually edit `.env`:**

```bash
cp .env.example .env
nano .env  # or your preferred editor
```

**Required variables:**

```env
# Claude API
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Printify
PRINTIFY_API_KEY=your-printify-api-key
PRINTIFY_SHOP_ID=your-shop-id

# ComfyUI (auto-configured on RunPod)
COMFYUI_API_URL=http://localhost:8188

# Storage
STORAGE_TYPE=local
STORAGE_PATH=/data/designs

# Pipeline
AUTO_PUBLISH=true
DEFAULT_TSHIRT_PRICE=19.99
DEFAULT_HOODIE_PRICE=34.99
ENABLE_PLATFORMS=printify,shopify
```

---

## 🧪 Step 2: Test Locally (Optional)

Before deploying to RunPod, test the system locally:

### Start Development Server

```bash
# Terminal 1: Start frontend (development mode with mock engine)
npm run dev

# Terminal 2: Start backend API
npm run dev:server
```

### Test Production Mode Locally

```bash
# Build frontend
npm run build:production

# Start production server
npm run start:production
```

Access at: http://localhost:3000

**Note:** This runs without ComfyUI (will fail at image generation). For full local testing with GPU:

```bash
# Install ComfyUI separately
./scripts/setup-comfyui.sh

# Start ComfyUI
cd ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188

# In another terminal, start the app
npm run start:production
```

---

## 🐳 Step 3: Build Docker Image

### Set Environment Variables

```bash
export DOCKER_USERNAME=your-dockerhub-username
export RUNPOD_API_KEY=your-runpod-api-key
```

### Build and Push

```bash
# Build image (this takes 10-20 minutes)
docker build -f Dockerfile.runpod -t staticwaves-pod-studio:latest .

# Tag for DockerHub
docker tag staticwaves-pod-studio:latest $DOCKER_USERNAME/staticwaves-pod-studio:latest

# Login to DockerHub
docker login

# Push image
docker push $DOCKER_USERNAME/staticwaves-pod-studio:latest
```

**What gets installed:**
- ✅ CUDA 12.1 + GPU drivers
- ✅ ComfyUI + Stable Diffusion XL model (~6.5GB)
- ✅ Node.js 20 + all app dependencies
- ✅ Nginx for serving frontend
- ✅ Complete POD pipeline backend

---

## ☁️ Step 4: Deploy to RunPod

### Automated Deployment

Use the deployment script:

```bash
./scripts/deploy-runpod.sh
```

This will:
1. Build Docker image
2. Push to DockerHub
3. Create RunPod pod with GPU
4. Configure ports and volumes
5. Start all services

### Manual Deployment

1. **Go to RunPod Console:** https://www.runpod.io/console/pods

2. **Click "Deploy"**

3. **Select GPU:**
   - Recommended: **NVIDIA RTX A4000** (16GB VRAM, ~$0.50/hr)
   - Minimum: RTX 3090 or better
   - Avoid: Less than 12GB VRAM

4. **Configure Pod:**
   - **Container Image:** `your-username/staticwaves-pod-studio:latest`
   - **Disk Size:** 50GB
   - **Container Disk:** 50GB
   - **Volume:** `/data` → Persistent storage

5. **Expose Ports:**
   - `80/http` - Web UI
   - `8188/http` - ComfyUI (optional)
   - `3000/http` - API (optional)

6. **Environment Variables:**
   Add these in RunPod's "Environment Variables" section:

   ```
   ANTHROPIC_API_KEY=sk-ant-xxx
   PRINTIFY_API_KEY=xxx
   PRINTIFY_SHOP_ID=xxx
   SHOPIFY_STORE_URL=yourstore.myshopify.com
   SHOPIFY_ACCESS_TOKEN=xxx
   AUTO_PUBLISH=true
   DEFAULT_TSHIRT_PRICE=19.99
   DEFAULT_HOODIE_PRICE=34.99
   ENABLE_PLATFORMS=printify,shopify
   ```

7. **Deploy Pod**

---

## 🎯 Step 5: Access Your Deployment

### Get Your Pod URL

After deployment, RunPod will provide:

- **Pod ID:** e.g., `abc123def456`
- **Public URL:** e.g., `https://abc123def456-80.proxy.runpod.net`

### Access Web UI

Open your public URL in a browser:

```
https://your-pod-id-80.proxy.runpod.net
```

### Check Health

```bash
curl https://your-pod-id-80.proxy.runpod.net/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "config": {
    "comfyui": true,
    "claude": true,
    "printify": true,
    "shopify": true
  }
}
```

### Test Configuration

```bash
curl https://your-pod-id-80.proxy.runpod.net/api/config/test
```

This tests all API connections (Claude, Printify, Shopify, etc.)

---

## 🔧 Step 6: Use the Pipeline

### Via Web UI

1. Open your RunPod URL
2. Configure drop name and design count
3. Click "Run Pipeline"
4. Watch real-time logs
5. Products automatically created on Printify

### Via API

```bash
# Start pipeline
curl -X POST https://your-pod-url/api/pipeline/start \
  -H "Content-Type: application/json" \
  -d '{
    "dropName": "UrbanVibes",
    "designCount": 5,
    "theme": "Streetwear",
    "style": "Bold graphics",
    "productTypes": ["tshirt", "hoodie"]
  }'

# Response: {"pipelineId": "pipeline-xxx", "status": "started"}

# Check status
curl https://your-pod-url/api/pipeline/<pipelineId>

# Get logs (real-time)
curl https://your-pod-url/api/pipeline/<pipelineId>/logs
```

---

## 📊 Monitoring & Logs

### View Logs in Container

SSH into your RunPod pod:

```bash
# ComfyUI logs
tail -f /var/log/comfyui.log

# API Server logs
tail -f /var/log/api.log

# Nginx logs
tail -f /var/log/nginx.log
```

### Check Service Status

```bash
# Inside container
ps aux | grep -E 'comfyui|node|nginx'
```

---

## 💰 Cost Breakdown

### Per Design Generated (1 T-shirt + 1 Hoodie)

| Service | Cost |
|---------|------|
| Claude API (prompts) | ~$0.01 |
| ComfyUI/RunPod (GPU time) | ~$0.05 |
| **Total per design** | **~$0.06** |

### RunPod Hosting

| GPU | VRAM | $/Hour | Best For |
|-----|------|--------|----------|
| RTX A4000 | 16GB | ~$0.50 | Recommended |
| RTX 3090 | 24GB | ~$0.70 | High volume |
| A100 40GB | 40GB | ~$1.50 | Maximum speed |

**Example:** Generate 100 designs in 1 hour = $6 (AI costs) + $0.50 (GPU) = **$6.50 total**

---

## 🔒 Security Best Practices

1. **Never commit `.env` file**
   ```bash
   # Already in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables on RunPod**
   - Don't hardcode API keys in Docker image
   - Use RunPod's environment variable feature

3. **Rotate API keys regularly**
   - Printify: Settings → API
   - Claude: Console → API Keys
   - Shopify: Apps → Manage private apps

4. **Monitor API usage**
   - Anthropic Console: Usage dashboard
   - Printify: API limits (100 req/min)

---

## 🐛 Troubleshooting

### ComfyUI Not Starting

**Symptom:** "Waiting for ComfyUI..." timeout

**Fix:**
```bash
# Check logs
tail -f /var/log/comfyui.log

# Common issues:
# - Missing SDXL model (re-download)
# - Insufficient VRAM (upgrade GPU)
# - Python dependencies (rebuild container)
```

### API Server Offline

**Symptom:** Web UI shows "API Server Offline"

**Fix:**
```bash
# Check if server is running
ps aux | grep tsx

# Restart server
cd /workspace/app
npx tsx server.ts

# Check logs
tail -f /var/log/api.log
```

### Printify API Errors

**Symptom:** "Failed to create product" in logs

**Common causes:**
1. Invalid API key → Check .env
2. Wrong Shop ID → Verify in Printify dashboard
3. Rate limit (100/min) → Add delays
4. Missing blueprint/provider → Use valid IDs

**Test credentials:**
```bash
curl https://api.printify.com/v1/shops/<SHOP_ID>/products.json \
  -H "Authorization: Bearer <API_KEY>"
```

### Out of GPU Memory

**Symptom:** CUDA OOM errors

**Fix:**
- Use smaller batch sizes (designCount: 1-5)
- Upgrade to GPU with more VRAM
- Reduce image size (1024→768)

---

## 📈 Scaling Tips

### Generate More Designs Faster

1. **Increase batch size**
   ```env
   BATCH_SIZE=10  # Generate 10 at once
   ```

2. **Use multiple pods**
   - Deploy 2-3 RunPod instances
   - Distribute drops across them
   - Parallel processing

3. **Optimize prompts**
   - Shorter prompts = faster generation
   - Cache common themes

### Cost Optimization

1. **Use spot instances**
   - RunPod's "Spot" pricing (50% off)
   - May get interrupted

2. **Auto-pause when idle**
   - Stop pod after generation
   - Restart when needed
   - Pay only for active time

3. **Batch processing**
   - Generate 100+ designs at once
   - Amortize startup costs

---

## 🔄 Updates & Maintenance

### Update Application Code

```bash
# Rebuild image
docker build -f Dockerfile.runpod -t $DOCKER_USERNAME/staticwaves-pod-studio:latest .
docker push $DOCKER_USERNAME/staticwaves-pod-studio:latest

# On RunPod: Recreate pod with new image
# (Pods auto-pull latest image on restart)
```

### Update Environment Variables

1. Go to RunPod pod settings
2. Edit environment variables
3. Restart pod

---

## 📚 Additional Resources

- **Printify API Docs:** https://developers.printify.com/
- **Claude API Docs:** https://docs.anthropic.com/
- **ComfyUI Guide:** https://github.com/comfyanonymous/ComfyUI
- **RunPod Docs:** https://docs.runpod.io/

---

## 🆘 Support

**Issues?** Open a GitHub issue with:
- Error logs from `/var/log/`
- Environment config (redact secrets!)
- Steps to reproduce

---

**🎉 You're ready to automate your POD business!**

Generate designs, create products, and publish to multiple platforms—all from one dashboard.

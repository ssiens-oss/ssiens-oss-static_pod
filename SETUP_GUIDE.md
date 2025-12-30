# POD Automation Pipeline - Complete Setup Guide

## Overview

This guide will walk you through setting up the complete POD automation pipeline that:
1. Generates AI images using Claude + ComfyUI
2. Auto-saves generated designs
3. Creates products on Printify (T-shirts & Hoodies)
4. Publishes to Shopify
5. Distributes to TikTok, Etsy, Instagram, and Facebook

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [RunPod Deployment](#runpod-deployment)
4. [Platform Integration Setup](#platform-integration-setup)
5. [Running the Pipeline](#running-the-pipeline)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **Node.js 20+** - [Download](https://nodejs.org/)
- **Python 3.10+** - [Download](https://www.python.org/)
- **Git** - [Download](https://git-scm.com/)
- **Docker** (for deployment) - [Download](https://www.docker.com/)

### API Keys & Accounts

You'll need accounts and API keys for the platforms you want to use:

#### Essential
- **Anthropic Claude API** - [Get API Key](https://console.anthropic.com/)
- **Printify Account** - [Sign Up](https://printify.com/)

#### Optional (based on your platforms)
- **Shopify Store** - [Start Free Trial](https://www.shopify.com/)
- **TikTok Shop** - [Apply](https://seller.tiktokshop.com/)
- **Etsy Shop** - [Open Shop](https://www.etsy.com/sell)
- **Instagram Business Account** - [Setup](https://business.instagram.com/)
- **Facebook Page** - [Create Page](https://www.facebook.com/pages/create)

---

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd ssiens-oss-static_pod
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Set Up ComfyUI

```bash
# Make script executable
chmod +x scripts/setup-comfyui.sh

# Run setup script
./scripts/setup-comfyui.sh
```

This will:
- Clone ComfyUI
- Install Python dependencies
- Download SDXL model (~7GB)

**Note:** The SDXL download can take 30-60 minutes depending on your connection.

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

**Minimum required configuration:**

```bash
# ComfyUI (if running locally)
COMFYUI_API_URL=http://localhost:8188

# Claude API
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Storage
STORAGE_TYPE=local
STORAGE_PATH=/data/designs

# Printify
PRINTIFY_API_KEY=your-printify-key
PRINTIFY_SHOP_ID=your-shop-id

# At least one sales channel (Shopify recommended)
SHOPIFY_STORE_URL=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-token
```

### Step 5: Start Services

**Terminal 1 - Start ComfyUI:**
```bash
cd ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188
```

**Terminal 2 - Start Web UI:**
```bash
npm run dev
```

**Terminal 3 - (Optional) Test Pipeline:**
```bash
# Create a test directory for designs
mkdir -p /data/designs

# The pipeline will now be accessible from the web UI
```

### Step 6: Access Web UI

Open your browser to: **http://localhost:5173**

You should see the POD Studio interface with the new pipeline controls.

---

## RunPod Deployment

### Why RunPod?

RunPod provides:
- **GPU instances** for fast AI image generation
- **Pre-configured environments** with CUDA support
- **Pay-per-use pricing** - only pay when generating
- **Public URLs** - access your pipeline from anywhere

### Prerequisites

1. **RunPod Account** - [Sign Up](https://www.runpod.io/)
2. **Docker Hub Account** - [Sign Up](https://hub.docker.com/)
3. **RunPod API Key** - Get from RunPod dashboard

### Deployment Steps

#### Option 1: Automated Deployment (Recommended)

```bash
# Make script executable
chmod +x scripts/deploy-runpod.sh

# Set environment variables
export DOCKER_USERNAME=your-dockerhub-username
export RUNPOD_API_KEY=your-runpod-api-key

# Run deployment
./scripts/deploy-runpod.sh
```

#### Option 2: Manual Deployment

**Step 1: Build Docker Image**

```bash
docker build -f Dockerfile.runpod -t pod-pipeline:latest .
```

**Step 2: Tag and Push to Registry**

```bash
# Tag for Docker Hub
docker tag pod-pipeline:latest your-username/pod-pipeline:latest

# Login to Docker Hub
docker login

# Push image
docker push your-username/pod-pipeline:latest
```

**Step 3: Deploy on RunPod**

1. Go to [RunPod Console](https://www.runpod.io/console/pods)
2. Click **"Deploy"** → **"Custom Container"**
3. Configure:
   - **Container Image**: `your-username/pod-pipeline:latest`
   - **GPU Type**: NVIDIA RTX A4000 (or higher)
   - **CPU**: 4 vCPUs
   - **Memory**: 16GB
   - **Storage**: 50GB
   - **Exposed Ports**: `80/http, 8188/http`
4. Click **"Deploy"**

**Step 4: Configure Environment Variables**

In RunPod pod settings, add environment variables:
```
ANTHROPIC_API_KEY=sk-ant-...
PRINTIFY_API_KEY=...
SHOPIFY_ACCESS_TOKEN=...
# etc.
```

**Step 5: Access Your Pipeline**

RunPod will provide a URL like:
```
https://xxxxx-80.proxy.runpod.net
```

Visit this URL to access your POD pipeline!

---

## Platform Integration Setup

### Printify Setup

1. **Create Shop**
   - Go to [Printify Dashboard](https://printify.com/app/dashboard)
   - Create a new shop or select existing

2. **Get API Key**
   - Settings → API → Generate new token
   - Copy token to `.env` as `PRINTIFY_API_KEY`

3. **Get Shop ID**
   - In URL bar: `https://printify.com/app/stores/{SHOP_ID}/products`
   - Copy shop ID to `.env` as `PRINTIFY_SHOP_ID`

### Shopify Setup

1. **Create Custom App**
   - Shopify Admin → Settings → Apps and sales channels
   - Develop apps → Create an app

2. **Configure Scopes**
   Required scopes:
   - `write_products`
   - `read_products`
   - `write_inventory`
   - `read_inventory`

3. **Install App & Get Token**
   - Install app → Reveal token once
   - Copy to `.env` as `SHOPIFY_ACCESS_TOKEN`

### TikTok Shop Setup

1. **Register as Seller**
   - [TikTok Seller Center](https://seller.tiktokshop.com/)

2. **Create App**
   - Developer Tools → Create App
   - Get App Key and App Secret

3. **Generate Access Token**
   - Follow OAuth flow or use test token
   - Copy credentials to `.env`

### Etsy Setup

1. **Register as Developer**
   - [Etsy Developer Portal](https://www.etsy.com/developers/)

2. **Create App**
   - Create app → Get API key
   - Set up OAuth for access token

3. **Get Shop ID**
   - Your shop URL: `etsy.com/shop/{SHOP_NAME}`
   - Use API to get shop ID

### Instagram Shopping Setup

1. **Convert to Business Account**
   - Instagram → Settings → Account → Switch to Professional

2. **Connect Facebook Page**
   - Link Instagram to Facebook Page

3. **Set Up Shopping**
   - Instagram → Settings → Business → Shopping
   - Connect product catalog

4. **Get Access Token**
   - [Facebook Developer Portal](https://developers.facebook.com/)
   - Create app → Get access token with `instagram_shopping_tag_product` permission

### Facebook Shop Setup

1. **Create Commerce Manager**
   - [Facebook Commerce Manager](https://business.facebook.com/commerce/)

2. **Set Up Catalog**
   - Create product catalog
   - Note catalog ID

3. **Get Access Token**
   - Facebook Developer Portal
   - Generate token with `catalog_management` permission

---

## Running the Pipeline

### Web UI (Recommended)

1. Start the application (local or RunPod)
2. Access web UI
3. Fill in pipeline form:
   - **Prompt Theme**: "Vintage sunset mountains"
   - **Product Types**: Select T-shirt and/or Hoodie
   - **Platforms**: Check platforms to publish to
   - **Quantity**: Number of designs to generate
4. Click **"Run Pipeline"**
5. Watch real-time logs in terminal panel

### Command Line

**Single Design:**
```bash
npm run pipeline:single -- \
  --prompt "Minimalist geometric patterns" \
  --products "tshirt,hoodie" \
  --platforms "printify,shopify,etsy"
```

**Batch Processing:**
```bash
npm run pipeline:batch -- \
  --theme "Nature" \
  --style "Vintage" \
  --count 10 \
  --products "tshirt,hoodie" \
  --platforms "all"
```

### Pipeline Flow

```
1. Claude generates creative prompts (30s)
   ↓
2. ComfyUI generates AI images (2-5min per image)
   ↓
3. Images saved to storage (5s)
   ↓
4. Products created on Printify (30s per product)
   ↓
5. Published to Shopify (10s per product)
   ↓
6. Distributed to other platforms (1-2min total)
   ↓
7. Complete! Products live on all platforms
```

**Estimated time for 1 design:**
- 5-7 minutes total
- Parallel processing where possible

**Estimated time for 10 designs:**
- 40-60 minutes total

---

## Troubleshooting

### ComfyUI Issues

**Error: "ComfyUI not responding"**
```bash
# Check if ComfyUI is running
curl http://localhost:8188/system_stats

# If not, start ComfyUI
cd ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188
```

**Error: "Model not found"**
```bash
# Re-download SDXL model
cd ComfyUI/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
```

### API Errors

**Printify: "Invalid API key"**
- Regenerate API key in Printify dashboard
- Update `.env` file
- Restart application

**Shopify: "401 Unauthorized"**
- Check access token hasn't expired
- Verify app scopes include required permissions
- Reinstall app if needed

**Claude: "Rate limit exceeded"**
- Wait 60 seconds
- Reduce batch size
- Check Anthropic account usage limits

### Storage Issues

**Error: "Permission denied"**
```bash
# Create storage directory with proper permissions
sudo mkdir -p /data/designs
sudo chown -R $USER:$USER /data/designs
chmod 755 /data/designs
```

### RunPod Issues

**Pod not starting**
- Check pod logs in RunPod dashboard
- Verify Docker image was pushed successfully
- Try smaller GPU type if out of capacity

**Can't access web UI**
- Wait 2-3 minutes for pod to fully start
- Check exposed ports are configured (80, 8188)
- Verify health check is passing

---

## Advanced Configuration

### Custom ComfyUI Workflows

Edit `services/comfyui.ts` to modify the workflow JSON for different models or styles.

### Custom Pricing Rules

Edit `.env`:
```bash
DEFAULT_TSHIRT_PRICE=24.99
DEFAULT_HOODIE_PRICE=39.99
```

### Platform Selection

Edit `.env` to enable only specific platforms:
```bash
ENABLE_PLATFORMS=printify,shopify,etsy
```

### Batch Size Optimization

For faster processing on RunPod with multiple GPUs:
```bash
BATCH_SIZE=10  # Process 10 images in parallel
```

---

## Next Steps

1. **Test with 1-2 designs** before running large batches
2. **Monitor costs** on each platform
3. **Set up webhooks** for completion notifications
4. **Create collections** to organize products
5. **Run A/B tests** with different designs
6. **Scale up** once everything works smoothly

---

## Support

- **Documentation**: See `PIPELINE_ARCHITECTURE.md`
- **Issues**: Report bugs on GitHub
- **Community**: Join Discord for POD automation discussions

---

## Cost Estimates

**Per design (1 T-shirt + 1 Hoodie):**

- Claude API: ~$0.01
- ComfyUI (RunPod A4000): ~$0.40/hour → ~$0.05 per design
- Storage: Negligible
- API calls: Free (Printify/Shopify)

**Total: ~$0.06 per design**

**For 100 designs: ~$6.00**

---

**Ready to automate your POD business? Start with the local setup, test with a few designs, then deploy to RunPod for production!** 🚀

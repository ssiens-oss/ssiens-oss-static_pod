# ⚡ Quick Start - Local to RunPod in 10 Minutes

Get your POD automation pipeline running on RunPod with GPU acceleration.

## 🎯 What You'll Build

A complete AI-powered POD pipeline that:
- Generates designs with Claude + ComfyUI (SDXL)
- Creates products on Printify automatically
- Publishes to Shopify, TikTok, Etsy, etc.
- Runs on GPU cloud (RunPod) for $0.50/hour

---

## 📝 Before You Start

Get these ready (5 minutes):

1. **Claude API Key** - https://console.anthropic.com/
2. **Printify API Key + Shop ID** - https://printify.com/app/account/api
3. **RunPod API Key** - https://www.runpod.io/console/user/settings
4. **DockerHub Account** - https://hub.docker.com/ (free)

---

## 🚀 Deployment Steps

### 1. Clone & Setup (2 minutes)

```bash
# Clone repo
git clone <your-repo-url>
cd ssiens-oss-static_pod

# Install dependencies
npm install

# Configure environment
./scripts/setup-env.sh
```

The setup script will ask for:
- ✅ Claude API key
- ✅ Printify API key & shop ID
- ⚙️ Product pricing (default: $19.99 T-shirt, $34.99 Hoodie)
- 🚀 Auto-publish settings

### 2. Build Docker Image (15-20 minutes)

```bash
# Set your DockerHub username
export DOCKER_USERNAME=your-dockerhub-username

# Build and push (one command)
docker build -f Dockerfile.runpod -t staticwaves-pod-studio:latest . && \
docker tag staticwaves-pod-studio:latest $DOCKER_USERNAME/staticwaves-pod-studio:latest && \
docker login && \
docker push $DOCKER_USERNAME/staticwaves-pod-studio:latest
```

**What's being installed:**
- CUDA + GPU drivers
- ComfyUI + SDXL model (6.5GB)
- Node.js backend + React frontend
- Nginx server
- All dependencies

☕ Grab coffee while this builds.

### 3. Deploy to RunPod (3 minutes)

#### Option A: Automated (Recommended)

```bash
export RUNPOD_API_KEY=your-runpod-api-key
./scripts/deploy-runpod.sh
```

#### Option B: Manual via Web UI

1. Go to https://www.runpod.io/console/pods
2. Click **"Deploy"**
3. Select GPU: **RTX A4000** (16GB, ~$0.50/hr)
4. Configure:
   - **Image:** `your-username/staticwaves-pod-studio:latest`
   - **Disk:** 50GB
   - **Volume:** `/data` (persistent storage)
5. Expose Ports:
   - `80/http` - Web UI
6. Add Environment Variables:
   ```
   ANTHROPIC_API_KEY=sk-ant-xxx
   PRINTIFY_API_KEY=xxx
   PRINTIFY_SHOP_ID=xxx
   AUTO_PUBLISH=true
   DEFAULT_TSHIRT_PRICE=19.99
   DEFAULT_HOODIE_PRICE=34.99
   ENABLE_PLATFORMS=printify
   ```
7. Click **"Deploy"**

### 4. Access Your Pipeline (1 minute)

After ~2 minutes, you'll get a URL like:

```
https://abc123def456-80.proxy.runpod.net
```

**Test it:**

```bash
# Check health
curl https://your-pod-url/health

# Should return:
# {"status":"ok","config":{"comfyui":true,"claude":true,"printify":true}}
```

**Open in browser:**

```
https://your-pod-url
```

You'll see the POD Studio interface!

---

## 🎨 Run Your First Drop

### Via Web UI

1. Open your RunPod URL
2. Enter:
   - **Drop Name:** `UrbanTest`
   - **Design Count:** `3`
   - **Blueprint ID:** `6` (T-shirt)
   - **Provider ID:** `1` (SwiftPOD)
3. Click **"Run Pipeline"**

Watch the logs in real-time:
- ✅ Generating 3 prompts with Claude...
- ✅ Creating images with ComfyUI...
- ✅ Uploading to Printify...
- ✅ Products created!

### Via API

```bash
curl -X POST https://your-pod-url/api/pipeline/start \
  -H "Content-Type: application/json" \
  -d '{
    "dropName": "UrbanTest",
    "designCount": 3,
    "theme": "Streetwear",
    "style": "Bold graphics",
    "productTypes": ["tshirt", "hoodie"]
  }'
```

---

## 💰 Cost Per Drop

**Example: 10 designs (10 T-shirts + 10 Hoodies)**

| Item | Cost |
|------|------|
| Claude API (prompts) | $0.10 |
| ComfyUI (GPU time, ~10 min) | $0.08 |
| **Total** | **$0.18** |

Plus $0.50/hour for RunPod GPU while active.

**Tip:** Generate 50-100 designs at once to maximize efficiency.

---

## 🔧 Common First-Time Issues

### "API Server Offline"

**Fix:** Wait 2-3 minutes after pod starts. Services need time to initialize.

```bash
# Check if services are running
docker exec -it <pod-id> ps aux | grep -E 'comfyui|node|nginx'
```

### "Failed to create product"

**Fix:** Verify Printify credentials

```bash
# Test Printify API
curl https://api.printify.com/v1/shops/<YOUR_SHOP_ID>/products.json \
  -H "Authorization: Bearer <YOUR_API_KEY>"

# Should return your products or empty array []
```

### "ComfyUI timeout"

**Fix:** GPU might need more VRAM. Upgrade to RTX A4000 or higher.

---

## 📊 View Results

### Check Printify Dashboard

1. Go to https://printify.com/app/products
2. You should see new products created!
3. Review and publish to your store

### Check Logs

```bash
# SSH into pod
docker exec -it <pod-id> bash

# View logs
tail -f /var/log/api.log        # API server
tail -f /var/log/comfyui.log    # Image generation
tail -f /var/log/nginx.log      # Web server
```

---

## 🎉 Next Steps

### Connect More Platforms

Edit `.env` and add:

```env
# Shopify
SHOPIFY_STORE_URL=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=xxx

# TikTok Shop
TIKTOK_APP_KEY=xxx
TIKTOK_SHOP_ID=xxx

# Enable platforms
ENABLE_PLATFORMS=printify,shopify,tiktok
```

Then rebuild and redeploy.

### Automate Drops

Create a cron job to run daily:

```bash
# generate-daily.sh
curl -X POST https://your-pod-url/api/pipeline/start \
  -H "Content-Type: application/json" \
  -d '{
    "dropName": "Daily'$(date +%Y%m%d)'",
    "designCount": 20,
    "theme": "Trending",
    "productTypes": ["tshirt", "hoodie"]
  }'
```

### Scale Up

- Use multiple RunPod instances
- Run 24/7 with auto-pause
- Generate 1000+ designs/day

---

## 📚 Learn More

- **Full Deployment Guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Architecture Details:** [PIPELINE_ARCHITECTURE.md](PIPELINE_ARCHITECTURE.md)
- **API Reference:** [README.md](README.md)

---

## 🆘 Need Help?

**Common Resources:**
- Printify API: https://developers.printify.com/
- Claude API: https://docs.anthropic.com/
- RunPod Docs: https://docs.runpod.io/

**Issues?** Open a GitHub issue with:
- Error logs
- Environment config (no secrets!)
- Steps to reproduce

---

**🚀 You're ready to automate!**

Generate hundreds of designs, create products on Printify, and scale your POD business with AI.

**Total setup time:** ~25 minutes
**Cost per 100 designs:** ~$1.80 + $0.50/hour GPU

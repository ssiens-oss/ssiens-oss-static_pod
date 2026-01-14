# Local Pipeline with RunPod ComfyUI

This guide shows you how to run the **entire POD pipeline locally** while using **RunPod for ComfyUI** (GPU-accelerated image generation).

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  LOCAL MACHINE                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Web UI (localhost:3000)                                   │  │
│  │  - Control panel                                           │  │
│  │  - Design management                                       │  │
│  │  - Product publishing                                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  POD Gateway (localhost:8099)                             │  │
│  │  - Image approval                                          │  │
│  │  - Printify integration                                    │  │
│  │  - Product creation                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         │ HTTPS
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  RUNPOD (GPU Cloud)                                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ComfyUI (https://xxxxx.proxy.runpod.net)                │  │
│  │  - SDXL image generation                                   │  │
│  │  - GPU acceleration (RTX 4090, A100, etc.)                │  │
│  │  - Automatic model downloading                             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Step 1: Deploy ComfyUI on RunPod

1. **Go to RunPod:** https://runpod.io
2. **Select Template:** Choose "ComfyUI" or "Stable Diffusion"
3. **Choose GPU:** RTX 4090 ($0.44/hr) or RTX 3090 ($0.34/hr)
4. **Deploy Pod**
5. **Get Public URL:** Copy the ComfyUI URL (e.g., `https://abc123-8188.proxy.runpod.net`)

### Step 2: Configure Local Environment

```bash
cd /home/user/ssiens-oss-static_pod

# Copy environment template
cp .env.example .env

# Edit .env with your RunPod ComfyUI URL
nano .env
```

**Update these values in `.env`:**

```bash
# ComfyUI (RunPod URL)
COMFYUI_API_URL=https://your-runpod-id-8188.proxy.runpod.net

# Printify Credentials
PRINTIFY_API_KEY=your_printify_api_key_here
PRINTIFY_SHOP_ID=26016759

# Blueprint Configuration
PRINTIFY_BLUEPRINT_ID=77    # Gildan 18500 Hoodie
PRINTIFY_PROVIDER_ID=39     # SwiftPOD
PRINTIFY_DEFAULT_PRICE_CENTS=3499  # $34.99
```

### Step 3: Start Local Services

#### Terminal 1: Web UI
```bash
npm run dev
# Access at: http://localhost:3000
```

#### Terminal 2: POD Gateway
```bash
cd gateway
source .venv/bin/activate
./start.sh
# Access at: http://localhost:8099
```

---

## 🎮 How to Use

### 1. Generate Images on RunPod

**Option A: ComfyUI Web Interface**
1. Open your RunPod ComfyUI URL in browser
2. Load a workflow (or create one)
3. Enter your prompt
4. Click "Queue Prompt"
5. Images are saved to ComfyUI's output directory

**Option B: API (from local machine)**
```bash
curl -X POST "https://your-runpod-id-8188.proxy.runpod.net/prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": {
      "3": {
        "inputs": {
          "text": "minimalist mountain landscape, flat colors"
        },
        "class_type": "CLIPTextEncode"
      }
    }
  }'
```

### 2. Sync Images to Local

**Option A: Manual Download**
```bash
# Download from RunPod ComfyUI output
wget https://your-runpod-id-8188.proxy.runpod.net/view?filename=ComfyUI_00001.png \
  -O ~/Downloads/design.png
```

**Option B: Auto-Sync Script**
```bash
# Create sync script
cat > sync-comfyui-images.sh << 'EOF'
#!/bin/bash
RUNPOD_URL="https://your-runpod-id-8188.proxy.runpod.net"
LOCAL_DIR="./gateway/images"

mkdir -p "$LOCAL_DIR"

# List and download new images
curl -s "$RUNPOD_URL/history" | jq -r '.[] | .outputs[]?.images[]?.filename' | while read img; do
  if [ ! -f "$LOCAL_DIR/$img" ]; then
    echo "Downloading $img..."
    wget -q "$RUNPOD_URL/view?filename=$img" -O "$LOCAL_DIR/$img"
  fi
done
EOF

chmod +x sync-comfyui-images.sh
./sync-comfyui-images.sh
```

### 3. Approve & Publish

1. **Open POD Gateway:** http://localhost:8099
2. **View Generated Images:** All synced images appear in gallery
3. **Approve Good Designs:** Click ✓ on designs you like
4. **Publish to Printify:**
   - Click "→ Publish"
   - Enter product title
   - Gateway uploads to Printify
   - Product created on Gildan 18500 Hoodie
   - Published to your shop

---

## 📊 Cost Breakdown

### RunPod ComfyUI
- **RTX 3090:** $0.34/hour (~$8/day if running 24/7)
- **RTX 4090:** $0.44/hour (~$11/day)
- **Recommended:** Stop pod when not generating (pay only when active)

### Image Generation Cost
- **Per image:** ~30 seconds on RTX 4090
- **Cost per image:** ~$0.004 (less than half a cent)
- **100 images/day:** ~$0.40

### Local Services
- **Web UI:** Free (your machine)
- **POD Gateway:** Free (your machine)
- **Printify API:** Free (pay only for fulfilled orders)

### Total Cost Estimate
- **Active use (8 hrs/day):** ~$3.50/day
- **Heavy use (24/7):** ~$11/day
- **Alternative:** Use RunPod's serverless (pay per second, no idle costs)

---

## ⚙️ Configuration Options

### ComfyUI Output Watching

**Enable auto-sync in `.env`:**
```bash
# Watch RunPod output directory
COMFYUI_WATCH_ENABLED=true
COMFYUI_WATCH_INTERVAL=30  # Check every 30 seconds
```

**Or use webhook (recommended):**
```bash
# In ComfyUI custom node, add webhook:
curl -X POST http://your-local-ip:8099/api/webhook/comfyui \
  -H "Content-Type: application/json" \
  -d '{"filename": "ComfyUI_00001.png"}'
```

### Printify Configuration

```bash
# Blueprint Options
PRINTIFY_BLUEPRINT_ID=77   # Hoodie (Gildan 18500)
# OR
PRINTIFY_BLUEPRINT_ID=3    # T-Shirt (Gildan 5000)

# Provider Options
PRINTIFY_PROVIDER_ID=39    # SwiftPOD (US, fast)
# OR
PRINTIFY_PROVIDER_ID=1     # Printify Choice (global)
```

---

## 🔧 Troubleshooting

### Can't Connect to RunPod ComfyUI

**Check URL:**
```bash
curl -I https://your-runpod-id-8188.proxy.runpod.net/
# Should return 200 OK
```

**Common Issues:**
- Pod is stopped (check RunPod dashboard)
- Wrong port (should be 8188)
- Firewall blocking (check RunPod network settings)

### Images Not Showing in Gateway

**Check sync script:**
```bash
./sync-comfyui-images.sh
ls -la gateway/images/
```

**Manual verification:**
```bash
# Test Printify connection
curl -X GET "https://api.printify.com/v1/shops.json" \
  -H "Authorization: Bearer $PRINTIFY_API_KEY"
```

### Gateway Not Starting

**Check dependencies:**
```bash
cd gateway
source .venv/bin/activate
pip list | grep -E "(Flask|requests|Pillow)"
```

**Check logs:**
```bash
tail -f gateway/logs/app.log
```

---

## 🎯 Next Steps

1. **Create your first design:**
   - Generate image on RunPod
   - Sync to local
   - Approve in gateway
   - Publish to Printify

2. **Explore workflows:**
   - Try different ComfyUI workflows
   - Experiment with prompts
   - Test different blueprints (hoodies, t-shirts)

3. **Scale up:**
   - Add more products (see `scripts/set_product_template.sh`)
   - Connect Shopify (see `POD_GATEWAY_INTEGRATION.md`)
   - Automate publishing (see `PIPELINE_ARCHITECTURE.md`)

---

## 📚 Related Docs

- **[POD_GATEWAY_INTEGRATION.md](./POD_GATEWAY_INTEGRATION.md)** - Gateway architecture
- **[PIPELINE_ARCHITECTURE.md](./PIPELINE_ARCHITECTURE.md)** - Full pipeline overview
- **[docs/PRINTIFY_BLUEPRINTS.md](./docs/PRINTIFY_BLUEPRINTS.md)** - Blueprint reference
- **[FREE_DEPLOYMENT.md](./FREE_DEPLOYMENT.md)** - 100% local setup (no cloud)

---

## 💡 Pro Tips

1. **Use RunPod Serverless:** Pay only when generating (no idle costs)
2. **Batch generate:** Queue 50+ images at once to maximize GPU time
3. **Stop pod overnight:** Save $5-8/day when not actively working
4. **Use webhook sync:** Instant image availability (no polling delay)
5. **Cache models:** Keep pod running during design sessions to avoid re-downloads

---

**Need help?** Check [README.md](./README.md) or open an issue.

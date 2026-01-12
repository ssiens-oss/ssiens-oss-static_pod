# ⚡ POD Engine - Quick Start Guide

Get your POD automation pipeline running in under 10 minutes.

## Prerequisites Checklist

- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Git installed
- [ ] 8GB+ RAM available
- [ ] Anthropic API key ([Get one](https://console.anthropic.com/))
- [ ] Printify account ([Sign up](https://printify.com/))

## Installation (5 minutes)

### Step 1: Get API Keys

**Anthropic Claude API:**
1. Go to https://console.anthropic.com/
2. Create account or login
3. Navigate to API Keys
4. Create new key → Copy it

**Printify API:**
1. Go to https://printify.com/app/account/api
2. Create new token → Copy it
3. Note your Shop ID from dashboard

### Step 2: Configure

```bash
# Copy environment template
cp .env.example .env

# Edit with your keys
nano .env
```

**Minimum required:**
```bash
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE
PRINTIFY_API_KEY=YOUR-PRINTIFY-KEY-HERE
PRINTIFY_SHOP_ID=YOUR-SHOP-ID
```

Save and exit (`Ctrl+X`, `Y`, `Enter`)

### Step 3: Deploy

```bash
# One-command deployment
./deploy-pod-engine.sh local
```

This installs everything automatically (~3-5 minutes).

### Step 4: Start

```bash
# Start all services
./start-pod-engine.sh
```

Wait ~30 seconds for services to initialize.

## Usage (2 minutes)

### Generate Your First Design

**Method 1: ComfyUI Interface (Recommended)**

1. Open http://localhost:8188
2. Load default workflow (or upload your own)
3. Enter a prompt in the text box
4. Click "Queue Prompt"
5. Wait for generation (~30-60 seconds)

**Method 2: Command Line**

```bash
npm run pipeline:single -- --prompt "cyberpunk city neon lights"
```

### Approve & Publish

1. Open **POD Gateway**: http://localhost:5000
2. See your generated design in the gallery
3. Click **"Approve"** button
4. Gateway automatically:
   - Uploads to Printify
   - Creates T-shirt product
   - Creates Hoodie product
   - Publishes to your shop

Done! Check your Printify shop for the new products.

## Workflow Summary

```
Generate → Review → Approve → Auto-Publish → Live on Store
(ComfyUI) (Gateway) (1-click)  (Automatic)    (2 minutes)
```

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| POD Gateway | http://localhost:5000 | Approve/reject designs |
| ComfyUI | http://localhost:8188 | AI generation |
| Web UI | http://localhost:5173 | Pipeline management |

## Common Commands

```bash
# Start engine
./start-pod-engine.sh

# Stop engine
./stop-pod-engine.sh

# View logs
tail -f logs/gateway.log

# Check health
curl http://localhost:5000/health

# Generate design (CLI)
npm run pipeline:single -- --prompt "your prompt here"
```

## Troubleshooting

### "Connection refused" on port 5000 or 8188

Services still starting. Wait 30 seconds and try again.

### ComfyUI shows "Queue empty"

Your design is generating. Refresh the page or check the output folder:
```bash
ls -la /workspace/ComfyUI/output/
```

### No designs in Gateway

1. Generate at least one design first
2. Check ComfyUI output directory exists:
   ```bash
   ls -la $POD_IMAGE_DIR
   ```

### Printify API errors

Verify your credentials:
```bash
curl -H "Authorization: Bearer $PRINTIFY_API_KEY" \
  https://api.printify.com/v1/shops.json
```

## Next Steps

### Enable More Platforms

Edit `.env`:
```bash
ENABLE_PLATFORMS=printify,shopify,etsy,tiktok

# Add platform credentials
SHOPIFY_STORE_URL=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=...
```

### Batch Processing

Generate multiple designs at once:
```bash
npm run pipeline:batch -- --count 10
```

### Custom Workflows

1. Create workflow in ComfyUI
2. Save as JSON
3. Place in `./ComfyUI/workflows/`
4. Use: `npm run pipeline:single -- --workflow my-workflow`

### Deploy to Cloud

For GPU acceleration and 24/7 operation:
```bash
./deploy-pod-engine.sh runpod
```

See [POD_ENGINE_DEPLOYMENT.md](POD_ENGINE_DEPLOYMENT.md) for full cloud deployment guide.

## Performance Tips

**Faster generation:**
- Use GPU instead of CPU
- Use SDXL Turbo models
- Lower image resolution (512x512 vs 1024x1024)

**Batch optimization:**
- Process 5-10 designs at once
- Schedule generation during off-hours
- Use RunPod spot instances (70% cheaper)

## Cost Breakdown

**Per Design:**
- Claude API: $0.01
- ComfyUI (local): Free
- Printify: Free (pay only when you sell)
- **Total: $0.01 per design**

**100 Designs:**
- Local: $1.00
- RunPod GPU: $6.00

## Help & Support

**Can't figure something out?**

1. Check [Full Deployment Guide](POD_ENGINE_DEPLOYMENT.md)
2. Search [GitHub Issues](https://github.com/ssiens-oss/ssiens-oss-static_pod/issues)
3. Read [Pipeline Architecture](PIPELINE_ARCHITECTURE.md)
4. Open new issue with logs

**Pro tip:** Include logs when asking for help:
```bash
# Copy recent logs
tail -n 100 logs/gateway.log > debug.log
tail -n 100 logs/comfyui.log >> debug.log
```

## What's Next?

Now that your POD engine is running:

1. **Generate 10 designs** - Get familiar with the workflow
2. **Review approval process** - Understand the gateway
3. **Set up webhooks** - Get notifications
4. **Configure platforms** - Connect Shopify, Etsy, etc.
5. **Scale up** - Move to RunPod for production

**Ready to scale?** See the [Complete Deployment Guide](POD_ENGINE_DEPLOYMENT.md) for advanced features, monitoring, and production deployment.

---

**Got it working?** ⭐ Star the repo and share your results!

**Having issues?** 🐛 Open an issue with your logs and we'll help you out.

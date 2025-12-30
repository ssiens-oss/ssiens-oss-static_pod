# POD Studio - Quick Start Guide

## 🚀 Running the Auto-Publish Pipeline

The POD pipeline automatically generates AI designs and publishes them to your print-on-demand platforms.

### Prerequisites

1. **RunPod is running** with ComfyUI
2. **Environment variables configured** (copy `.env.example` to `.env` and fill in your API keys)
3. **Auto-download running** (optional, to get images to your local machine)

### Basic Usage

#### Generate a Single Design

```bash
# SSH into your RunPod
ssh nfre49elqpt6su-64411157@ssh.runpod.io -i ~/.ssh/id_ed25519

# Navigate to the app directory
cd /workspace/app

# Run the pipeline
npm run pipeline:single
```

This will:
1. ✅ Generate a creative prompt with Claude AI
2. ✅ Create an AI image in ComfyUI
3. ✅ Auto-save the image to `/data/designs`
4. ✅ Create T-shirt and Hoodie products on Printify
5. ✅ Publish to Shopify
6. ✅ Distribute to TikTok/Etsy/Instagram/Facebook (if configured)

#### Generate a Batch of Designs

```bash
# Generate 10 designs with different themes
npm run pipeline:batch

# Custom batch size
node scripts/run-batch.js 20
```

#### Custom Options

```bash
# Specific theme
node scripts/run-pipeline.js --theme="cyberpunk aesthetic"

# Generate multiple variations
node scripts/run-pipeline.js --count=5

# Only T-shirts
node scripts/run-pipeline.js --products=tshirt

# Don't auto-publish (just generate and save)
node scripts/run-pipeline.js --no-publish

# Combine options
node scripts/run-pipeline.js --theme="retro gaming" --count=3 --products=tshirt,hoodie
```

### Environment Configuration

Your `.env` file controls what platforms are used:

```bash
# Required (Claude AI for prompts)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# ComfyUI (usually automatic on RunPod)
COMFYUI_API_URL=http://localhost:8188

# Storage (where images are saved)
STORAGE_TYPE=local
STORAGE_PATH=/data/designs

# Printify (create products)
PRINTIFY_API_KEY=your-key
PRINTIFY_SHOP_ID=your-shop-id

# Shopify (publish products)
SHOPIFY_STORE_URL=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-token

# Optional: Other platforms
TIKTOK_ACCESS_TOKEN=...
ETSY_ACCESS_TOKEN=...
INSTAGRAM_ACCESS_TOKEN=...
FACEBOOK_ACCESS_TOKEN=...
```

### Workflow Examples

#### Example 1: Quick Test Run

```bash
# Generate one design, don't publish
node scripts/run-pipeline.js --theme="cute cats" --no-publish
```

Check the output in `/data/designs/` to verify it works.

#### Example 2: Full Auto-Publish

```bash
# Generate and publish 5 retro gaming designs
node scripts/run-pipeline.js --theme="retro gaming" --count=5
```

Products will appear on your Shopify store automatically!

#### Example 3: Daily Batch Job

Set up a cron job on RunPod to generate designs daily:

```bash
# Edit crontab
crontab -e

# Add this line (runs at 3 AM daily)
0 3 * * * cd /workspace/app && npm run pipeline:batch >> /var/log/pod-pipeline.log 2>&1
```

This generates 10 new designs every day automatically!

### Monitoring Progress

The pipeline shows real-time progress:

```
╔════════════════════════════════════════════════════╗
║  POD Studio - Auto Pipeline                       ║
╚════════════════════════════════════════════════════╝

🚀 Starting POD automation pipeline...

📝 Generating creative prompts...
✓ Generated 1 prompt(s)

🎨 Generating images with ComfyUI...
✓ Generated 1 images

💾 Saving images to storage...
✓ Saved 1 image(s)

🛍️  Creating products on Printify...
✓ Created 2 product(s) (T-shirt, Hoodie)

📢 Publishing to platforms...
✓ Published to Shopify: 2 products
✓ Published to TikTok: 2 products

╔════════════════════════════════════════════════════╗
║  Pipeline Complete!                               ║
╚════════════════════════════════════════════════════╝

✨ All done! Your designs are live!
```

### Auto-Download to Local Machine

While the pipeline runs on RunPod, you can auto-download images to your local machine:

```bash
# On your LOCAL machine (not RunPod)
cd ~/ssiens-oss-static_pod

export RUNPOD_SSH_HOST="nfre49elqpt6su-64411157@ssh.runpod.io"
export REMOTE_PATH="/workspace/ComfyUI/output"

# Start auto-sync (runs continuously)
./scripts/auto-download-images.sh
```

New images appear in `~/POD-Designs/` automatically!

### Troubleshooting

#### "Module not found" errors

```bash
# Make sure you're in the app directory
cd /workspace/app

# Reinstall dependencies
npm install
```

#### "ComfyUI not responding"

```bash
# Check if ComfyUI is running
curl http://localhost:8188/system_stats

# If not, start it
cd /workspace/ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188 &
```

#### "API key invalid"

Make sure your `.env` file has valid API keys:

```bash
# Check your .env file
cat /workspace/app/.env

# Test Claude API
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":100,"messages":[{"role":"user","content":"test"}]}'
```

### Next Steps

1. **Run your first design**: `npm run pipeline:single`
2. **Configure platforms**: Add API keys to `.env`
3. **Set up auto-download**: Run the sync script on your local machine
4. **Schedule batch jobs**: Set up cron for daily automation
5. **Monitor results**: Check Shopify/Printify dashboards

Need help? Check:
- SETUP_GUIDE.md - Full setup instructions
- PIPELINE_ARCHITECTURE.md - Technical details
- AUTO_DOWNLOAD_GUIDE.md - Local sync setup

Happy automating! 🎨🚀

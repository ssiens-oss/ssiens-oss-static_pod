# POD Pipeline - Quick Command Reference

## 🚀 On RunPod

### Setup (First Time Only)
```bash
cd /workspace/app
npm install
cp .env.example .env
nano .env  # Add your API keys
```

### Start ComfyUI
```bash
cd /workspace/ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188 &
```

### Generate Designs

#### Single Design
```bash
cd /workspace/app

# Basic
npm run pipeline:single

# With theme
npm run pipeline:single -- --theme="cyberpunk cats"

# Multiple variations
npm run pipeline:single -- --theme="retro gaming" --count=5

# Test mode (no publishing)
npm run pipeline:single -- --theme="space art" --no-publish

# Only T-shirts
npm run pipeline:single -- --products=tshirt
```

#### Batch Mode
```bash
# Default (10 designs)
npm run pipeline:batch

# Custom count
npm run pipeline:batch -- 5
npm run pipeline:batch -- 50
npm run pipeline:batch -- 301  # All existing images

# Test mode
npm run pipeline:batch -- 10 --no-publish
```

### Monitor
```bash
# View logs
tail -f /var/log/pod-pipeline.log

# Check images
ls -la /data/designs/

# ComfyUI status
curl http://localhost:8188/system_stats

# ComfyUI queue
curl http://localhost:8188/queue
```

## 💻 On Local Machine

### Auto-Download Images
```bash
# Set RunPod connection
export RUNPOD_SSH_HOST="<pod-id>@ssh.runpod.io"
export REMOTE_PATH="/data/designs"

# Start auto-sync (runs continuously)
./scripts/auto-download-images.sh

# One-time download
./scripts/download-images.sh
```

Images download to `~/POD-Designs/`

## 🔧 Troubleshooting

### Module Errors
```bash
cd /workspace/app
rm -rf node_modules package-lock.json
npm install
```

### ComfyUI Down
```bash
cd /workspace/ComfyUI
pkill -f main.py
python3 main.py --listen 0.0.0.0 --port 8188 &
```

### Check Configuration
```bash
cat .env | grep ANTHROPIC_API_KEY
cat .env | grep PRINTIFY_API_KEY
```

### Test Printify Connection
```bash
curl -H "Authorization: Bearer $PRINTIFY_API_KEY" \
  https://api.printify.com/v1/shops.json
```

## ⏰ Cron Job (Daily Automation)

```bash
# Edit crontab
crontab -e

# Add this line (3 AM daily, 10 designs)
0 3 * * * cd /workspace/app && npm run pipeline:batch -- 10 >> /var/log/pod-pipeline.log 2>&1
```

## 📊 Quick Stats

```bash
# Total images
ls /data/designs/*.png | wc -l

# Recent images
ls -lt /data/designs/ | head -20

# Disk usage
du -sh /data/designs/
```

## 🌐 Platform URLs

- Printify Dashboard: https://printify.com/app/products
- Shopify Admin: https://yourstore.myshopify.com/admin
- RunPod Dashboard: https://runpod.io/console/pods

## 📝 Environment Variables

**Required:**
- `ANTHROPIC_API_KEY` - Claude AI
- `COMFYUI_API_URL` - Usually http://localhost:8188

**Optional (enable platforms):**
- `PRINTIFY_API_KEY` + `PRINTIFY_SHOP_ID`
- `SHOPIFY_STORE_URL` + `SHOPIFY_ACCESS_TOKEN`
- `TIKTOK_*` - TikTok Shop
- `ETSY_*` - Etsy
- `INSTAGRAM_*` - Instagram Shopping
- `FACEBOOK_*` - Facebook Shop

## 🎯 Common Workflows

### Morning: Start Everything
```bash
# 1. SSH to RunPod
ssh <pod-id>@ssh.runpod.io -i ~/.ssh/id_ed25519

# 2. Start ComfyUI
cd /workspace/ComfyUI && python3 main.py --listen 0.0.0.0 --port 8188 &

# 3. Generate designs
cd /workspace/app && npm run pipeline:batch -- 10

# 4. On local machine: Start auto-download
./scripts/auto-download-images.sh
```

### Test New Theme
```bash
npm run pipeline:single -- --theme="YOUR THEME" --no-publish
# Check /data/designs/ for output
# If good, remove --no-publish to go live
```

### Full Auto Run
```bash
npm run pipeline:batch -- 20
# Sits back and watches the magic happen
```

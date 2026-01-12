# 🚀 POD Engine - Complete Deployment Guide

## Overview

Complete end-to-end Print-on-Demand automation pipeline with AI generation, human approval, and multi-platform publishing.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    POD ENGINE PIPELINE                        │
└──────────────────────────────────────────────────────────────┘

1. AI GENERATION
   ┌─────────────────┐
   │   ComfyUI       │  AI Image Generation
   │   Port: 8188    │  GPU-accelerated
   └────────┬────────┘
            │
            ↓
   /workspace/ComfyUI/output/*.png

2. HUMAN APPROVAL
   ┌─────────────────┐
   │  POD Gateway    │  Review & Approve
   │  Port: 5000     │  Quality Control
   └────────┬────────┘
            │
            ↓ (Approved Only)

3. PRODUCT CREATION
   ┌─────────────────┐
   │  Printify API   │  Create Products
   │                 │  T-shirts, Hoodies
   └────────┬────────┘
            │
            ↓

4. MULTI-PLATFORM PUBLISHING
   ┌──────────────────────────────────┐
   │ Shopify │ TikTok │ Etsy │ More  │
   └──────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- 8GB+ RAM
- GPU (optional, for faster generation)
- API Keys:
  - Anthropic Claude API
  - Printify API
  - Platform APIs (Shopify, etc. - optional)

### 1. Clone & Configure

```bash
# Navigate to project
cd ssiens-oss-static_pod

# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

**Required environment variables:**
- `ANTHROPIC_API_KEY` - Your Claude API key
- `PRINTIFY_API_KEY` - Your Printify API key
- `PRINTIFY_SHOP_ID` - Your Printify shop ID

### 2. Deploy

Choose your deployment mode:

```bash
# Local deployment (recommended for development)
./deploy-pod-engine.sh local

# RunPod deployment (cloud GPU)
./deploy-pod-engine.sh runpod

# Docker deployment
./deploy-pod-engine.sh docker
```

The script will:
- ✅ Validate configuration
- ✅ Install dependencies
- ✅ Set up ComfyUI
- ✅ Configure POD Gateway
- ✅ Create startup scripts
- ✅ Set up health monitoring

### 3. Start Services

```bash
./start-pod-engine.sh
```

### 4. Access Services

- **POD Gateway**: http://localhost:5000 - Approve/reject designs
- **ComfyUI**: http://localhost:8188 - AI generation interface
- **Web UI**: http://localhost:5173 - Pipeline management

---

## Deployment Modes

### Local Deployment

Best for development and testing.

```bash
./deploy-pod-engine.sh local
```

**Characteristics:**
- Runs on localhost
- All services local
- Easy debugging
- No cloud costs

**Requirements:**
- Sufficient local resources
- GPU recommended for ComfyUI

### RunPod Deployment

Best for production with GPU acceleration.

```bash
./deploy-pod-engine.sh runpod
```

**Characteristics:**
- Cloud GPU (NVIDIA RTX A4000+)
- Persistent storage at `/workspace`
- Public URLs for access
- Pay-per-use pricing

**Additional Steps:**
1. Expose ports in RunPod:
   - 5000 (POD Gateway)
   - 8188 (ComfyUI)
2. Configure webhooks with public URL
3. Set up persistent volume for designs

### Docker Deployment

Best for containerized environments.

```bash
./deploy-pod-engine.sh docker
```

**Run the container:**
```bash
docker run -d \
  --name pod-engine \
  -p 5000:5000 \
  -p 8188:8188 \
  --gpus all \
  -v /data/designs:/data/designs \
  staticwaves-pod-engine:latest
```

---

## Complete Workflow

### Step 1: Generate Designs

**Option A: Use ComfyUI Interface**
1. Open http://localhost:8188
2. Load a workflow
3. Queue generation
4. Images saved to `/workspace/ComfyUI/output`

**Option B: Use Claude Automation**
```bash
npm run pipeline:single -- \
  --prompt "cyberpunk neon cityscape" \
  --style "digital-art"
```

### Step 2: Review in POD Gateway

1. Open http://localhost:5000
2. View generated designs in gallery
3. Click "Approve" or "Reject"
4. Add tags/metadata (optional)

**Features:**
- Real-time gallery updates
- Filter by status
- Batch operations
- Auto-refresh every 10s

### Step 3: Auto-Publish Approved Designs

Once approved, the gateway automatically:
1. Uploads image to Printify
2. Creates products (T-shirt + Hoodie)
3. Sets pricing and variants
4. Publishes to your shop

**Monitor progress:**
```bash
tail -f logs/gateway.log
```

### Step 4: Multi-Platform Distribution

Enable platforms in `.env`:
```bash
ENABLE_PLATFORMS=shopify,tiktok,etsy,instagram,facebook
```

Products will sync to all enabled platforms automatically.

---

## Service Management

### Start All Services

```bash
./start-pod-engine.sh
```

Starts:
- ComfyUI (port 8188)
- POD Gateway (port 5000)
- Web UI (port 5173)

### Stop All Services

```bash
./stop-pod-engine.sh
```

Gracefully stops all services.

### Restart Individual Services

```bash
# Restart ComfyUI
kill $(cat logs/comfyui.pid)
cd ComfyUI && python3 main.py --listen 0.0.0.0 --port 8188 &

# Restart POD Gateway
kill $(cat logs/gateway.pid)
cd gateway && source .venv/bin/activate && python app/main.py &

# Restart Web UI
kill $(cat logs/webui.pid)
npm run dev &
```

---

## Health Monitoring

### Check System Health

```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "comfyui": "operational",
    "printify": "connected",
    "storage": "available"
  },
  "timestamp": "2026-01-12T07:00:00Z"
}
```

### View Logs

```bash
# All logs
tail -f logs/*.log

# Specific services
tail -f logs/comfyui.log
tail -f logs/gateway.log
tail -f logs/webui.log
```

### Service Status

```bash
# Check running processes
ps aux | grep -E "(comfyui|gateway|vite)"

# Check ports
netstat -tulpn | grep -E "(5000|8188|5173)"
```

---

## Configuration

### Environment Variables

Edit `.env` to configure:

#### Core Services
```bash
COMFYUI_API_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=/workspace/ComfyUI/output
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

#### POD Gateway
```bash
POD_IMAGE_DIR=/workspace/comfyui/output
POD_STATE_FILE=/workspace/gateway/state.json
POD_ARCHIVE_DIR=/workspace/gateway/archive
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

#### Printify
```bash
PRINTIFY_API_KEY=your-api-key
PRINTIFY_SHOP_ID=your-shop-id
AUTO_PUBLISH=true
DEFAULT_TSHIRT_PRICE=19.99
DEFAULT_HOODIE_PRICE=34.99
```

#### Multi-Platform
```bash
ENABLE_PLATFORMS=printify,shopify,etsy

# Shopify
SHOPIFY_STORE_URL=mystore.myshopify.com
SHOPIFY_ACCESS_TOKEN=...

# TikTok Shop
TIKTOK_APP_KEY=...
TIKTOK_SHOP_ID=...

# Etsy
ETSY_API_KEY=...
ETSY_SHOP_ID=...
```

### Gateway Configuration

Edit `gateway/.env` for gateway-specific settings:

```bash
# Gateway Port
FLASK_PORT=5000

# Auto-approval settings
AUTO_APPROVE_THRESHOLD=0.9  # Quality score threshold

# Retention
ARCHIVE_AFTER_DAYS=30
```

---

## Troubleshooting

### ComfyUI Won't Start

**Check:**
```bash
tail -f logs/comfyui.log
```

**Common issues:**
- Port 8188 already in use: `lsof -i :8188`
- Missing models: Run `./scripts/setup-comfyui.sh`
- GPU not found: Check CUDA installation

### POD Gateway Connection Issues

**Check:**
```bash
curl http://localhost:5000/health
```

**Common issues:**
- Port 5000 in use: `lsof -i :5000`
- Python environment: `cd gateway && source .venv/bin/activate`
- Missing dependencies: `cd gateway && pip install -r requirements.txt`

### Printify API Errors

**Verify credentials:**
```bash
curl -H "Authorization: Bearer $PRINTIFY_API_KEY" \
  https://api.printify.com/v1/shops.json
```

**Common issues:**
- Invalid API key
- Shop ID mismatch
- Rate limiting (wait 1 minute)

### Images Not Appearing in Gateway

**Check:**
1. ComfyUI output directory exists
2. Permissions: `chmod 755 /workspace/ComfyUI/output`
3. Gateway can read directory:
   ```bash
   ls -la $POD_IMAGE_DIR
   ```

---

## Scaling & Performance

### Increase Generation Speed

**Local:**
- Use GPU instead of CPU
- Increase ComfyUI workers
- Use faster models (SDXL Turbo)

**RunPod:**
- Upgrade to better GPU (RTX 4090, A100)
- Use multiple pods with load balancer

### Batch Processing

```bash
# Generate multiple designs
npm run pipeline:batch -- \
  --prompts prompts.json \
  --count 50 \
  --parallel 5
```

### Database for Large Scale

For 1000+ designs, switch to PostgreSQL:

```bash
# In gateway/app/state.py
DATABASE_URL=postgresql://user:pass@localhost/pod_gateway
```

---

## Security Best Practices

### API Keys

- Never commit `.env` to git
- Use environment variables in production
- Rotate keys regularly

### Network Security

```bash
# Firewall rules (production)
ufw allow 5000/tcp  # Gateway (restrict to your IP)
ufw allow 8188/tcp  # ComfyUI (internal only)
```

### Authentication

Add authentication to gateway:

```python
# gateway/app/main.py
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == os.getenv('GATEWAY_USER') and \
           password == os.getenv('GATEWAY_PASS')

@app.route('/')
@auth.login_required
def index():
    # ...
```

---

## Cost Estimates

### Per Design

| Service | Cost |
|---------|------|
| Claude API | $0.01 |
| ComfyUI (RunPod GPU) | $0.05 |
| Printify (free) | $0.00 |
| **Total** | **$0.06** |

### Monthly (100 designs)

- Generation: $6.00
- RunPod Storage: $5.00
- **Total: ~$11/month**

### Production (1000 designs/month)

- Generation: $60.00
- RunPod GPU: $50.00
- Storage: $10.00
- **Total: ~$120/month**

---

## Advanced Features

### Webhook Notifications

Get notified when designs are approved:

```bash
# In .env
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
WEBHOOK_ON_APPROVAL=true
```

### Custom Workflows

Add custom ComfyUI workflows:

```bash
# Place workflow in
./ComfyUI/workflows/my-custom-workflow.json

# Use in automation
npm run pipeline:single -- --workflow my-custom-workflow
```

### A/B Testing

Test different designs automatically:

```bash
npm run pipeline:ab-test -- \
  --variants 5 \
  --theme "minimalist-tech"
```

---

## Support & Resources

### Documentation

- [POD Gateway Integration](POD_GATEWAY_INTEGRATION.md)
- [Pipeline Architecture](PIPELINE_ARCHITECTURE.md)
- [Setup Guide](SETUP_GUIDE.md)
- [Music Engine Guide](MUSIC_GUIDE.md)

### Community

- GitHub Issues: Report bugs
- Discussions: Share workflows
- Discord: Real-time support

### Professional Support

For enterprise deployments, custom integrations, or priority support, contact the development team.

---

## Changelog

### Version 2.0 (2026-01-12)
- ✅ Complete unified deployment script
- ✅ Health check system
- ✅ Integrated POD Gateway
- ✅ Multi-mode deployment (local/RunPod/Docker)
- ✅ Automated service management

### Version 1.0 (2026-01-09)
- Initial POD Gateway release
- ComfyUI integration
- Printify automation
- Multi-platform support

---

## License

MIT License - See LICENSE file for details

---

**Questions?** Check the [troubleshooting](#troubleshooting) section or open an issue on GitHub.

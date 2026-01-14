# RunPod Production Setup Guide

Complete guide for deploying the StaticWaves POD Pipeline to RunPod with the POD Gateway approval system.

## 🎯 What You Get

After following this guide, you'll have:

- ✅ **ComfyUI** running on GPU for AI image generation
- ✅ **POD Gateway** with web UI for approving designs
- ✅ **Printify integration** for automatic product publishing
- ✅ **Auto-restart** for all services
- ✅ **Production-ready** configuration

## 📋 Prerequisites

### Required

1. **RunPod Account** - [Sign up](https://runpod.io/)
2. **Printify API Key** - [Get from Printify](https://printify.com/app/account/api)
3. **Printify Shop ID** - Found in your Printify dashboard

### Optional

- **Anthropic API Key** - For AI prompt generation (optional)
- **SSH Key** - For direct deployment via SSH

## 🚀 Quick Start (Recommended)

### Option 1: Automated Setup Script

The easiest way to set up everything on RunPod:

#### Step 1: Create RunPod Instance

1. Go to [RunPod Console](https://www.runpod.io/console/pods)
2. Click **Deploy** → **GPU Pod**
3. Select a GPU:
   - **Recommended**: NVIDIA RTX A4000 (16GB VRAM)
   - **Budget**: NVIDIA RTX 3090 (24GB VRAM)
   - **Performance**: NVIDIA RTX A5000/A6000
4. Configure:
   - **Template**: RunPod PyTorch 2.1
   - **Container Disk**: 50GB minimum
   - **Volume**: 50GB (for persistent storage)
5. Click **Deploy**

#### Step 2: Connect via SSH

```bash
# Get SSH command from RunPod dashboard
ssh root@your-pod-id.ssh.runpod.io -i ~/.ssh/your-key
```

#### Step 3: Clone Repository

```bash
cd /workspace
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
cd ssiens-oss-static_pod
```

#### Step 4: Run Setup Script

```bash
chmod +x scripts/setup-runpod.sh
./scripts/setup-runpod.sh
```

The script will:
1. ✅ Install system dependencies
2. ✅ Clone and install ComfyUI
3. ✅ Install POD Gateway
4. ✅ Prompt for API keys
5. ✅ Create startup scripts

#### Step 5: Start Services

```bash
/workspace/start-pod.sh
```

#### Step 6: Expose Ports

1. Go to RunPod dashboard
2. Click **HTTP Service [Port]**
3. Expose these ports:
   - **8188** → ComfyUI API
   - **5000** → POD Gateway

#### Step 7: Access Gateway

Click the port 5000 URL to open the POD Gateway web interface.

---

## 🐳 Docker Deployment (Alternative)

### Step 1: Build and Push Image

```bash
# On your local machine
docker build -f Dockerfile.runpod -t your-username/pod-pipeline:latest .
docker push your-username/pod-pipeline:latest
```

### Step 2: Deploy to RunPod

1. Go to [RunPod Console](https://www.runpod.io/console/pods)
2. Click **Deploy** → **Custom Container**
3. Configure:
   - **Image**: `your-username/pod-pipeline:latest`
   - **GPU**: NVIDIA RTX A4000+
   - **Ports**: `80/http,8188/http,5000/http`
   - **Volume**: 50GB mounted at `/data`
4. Add environment variables:
   ```
   PRINTIFY_API_KEY=your-api-key
   PRINTIFY_SHOP_ID=your-shop-id
   ANTHROPIC_API_KEY=your-anthropic-key (optional)
   ```
5. Click **Deploy**

---

## 📁 Directory Structure

After setup, your RunPod instance will have:

```
/workspace/
├── ComfyUI/                    # AI image generation
│   ├── main.py
│   ├── models/
│   └── output/                 # Generated images appear here
├── gateway/                    # POD Gateway
│   ├── app/
│   │   ├── main.py             # Flask server
│   │   ├── config.py
│   │   ├── state.py
│   │   └── printify_client.py
│   ├── templates/
│   │   └── gallery.html        # Web UI
│   ├── .venv/
│   └── .env                    # Your configuration
├── gateway-state/
│   └── state.json              # Approval status tracking
├── start-pod.sh                # Start all services
├── stop-pod.sh                 # Stop all services
└── status-pod.sh               # Check service status
```

---

## ⚙️ Configuration

### Environment Variables

Edit `/workspace/gateway/.env`:

```bash
# ComfyUI
COMFYUI_API_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=/workspace/ComfyUI/output

# Gateway
POD_IMAGE_DIR=/workspace/ComfyUI/output
POD_STATE_FILE=/workspace/gateway-state/state.json
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Printify (REQUIRED)
PRINTIFY_API_KEY=your-printify-api-key
PRINTIFY_SHOP_ID=your-shop-id
PRINTIFY_BLUEPRINT_ID=3        # 3 = T-shirt
PRINTIFY_PROVIDER_ID=99        # 99 = SwiftPOD

# Claude (Optional)
ANTHROPIC_API_KEY=your-key-here
```

### Printify Configuration

To find your credentials:

1. **API Key**:
   - Go to [Printify Account → API](https://printify.com/app/account/api)
   - Click **Create Token**
   - Copy the token

2. **Shop ID**:
   ```bash
   curl https://api.printify.com/v1/shops.json \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```
   Look for the `id` field in the response

---

## 🎨 Usage Workflow

### 1. Generate Images with ComfyUI

```bash
# Access ComfyUI at http://your-pod:8188
# Upload a workflow or use the default
# Click "Queue Prompt" to generate
```

Images will be saved to `/workspace/ComfyUI/output/`

### 2. Review in Gateway

1. Open POD Gateway at `http://your-pod:5000`
2. See all generated images in the gallery
3. Images start with status **Pending**

### 3. Approve Designs

1. Click on an image to view full size
2. Click **Approve** if you like it
3. Status changes to **Approved**

### 4. Publish to Printify

1. Click **Publish** on an approved image
2. Enter product title (optional)
3. Gateway will:
   - Upload image to Printify
   - Create T-shirt product
   - Publish to your shop
4. Status changes to **Published**

### 5. Check Printify

Visit your Printify dashboard to see the new product!

---

## 🔧 Management

### Start Services

```bash
/workspace/start-pod.sh
```

Starts:
- ComfyUI on port 8188
- POD Gateway on port 5000

### Stop Services

```bash
/workspace/stop-pod.sh
```

### Check Status

```bash
/workspace/status-pod.sh
```

Example output:
```
📊 POD Pipeline Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ComfyUI:  Running (PID: 1234)
   API:      Responding
✅ Gateway:  Running (PID: 5678)
   API:      Responding
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### View Logs

```bash
# ComfyUI logs
tail -f /var/log/comfyui.log

# Gateway logs
tail -f /var/log/gateway.log
```

### Restart Services

```bash
/workspace/stop-pod.sh
/workspace/start-pod.sh
```

---

## 🐛 Troubleshooting

### ComfyUI Won't Start

**Check GPU:**
```bash
nvidia-smi
```

**Check logs:**
```bash
tail -100 /var/log/comfyui.log
```

**Common issues:**
- Out of VRAM → Use smaller model or reduce batch size
- Port 8188 in use → Kill existing process: `pkill -f "python3 main.py --listen"`

### Gateway Won't Start

**Check Python environment:**
```bash
cd /workspace/gateway
source .venv/bin/activate
python3 app/main.py
```

**Check configuration:**
```bash
cat /workspace/gateway/.env
```

**Common issues:**
- Missing API keys → Edit `.env` file
- Permission errors → `chmod -R 755 /workspace/gateway`
- Port 5000 in use → Change `FLASK_PORT` in `.env`

### Images Not Appearing

**Check ComfyUI output directory:**
```bash
ls -la /workspace/ComfyUI/output/
```

**Verify gateway configuration:**
```bash
grep POD_IMAGE_DIR /workspace/gateway/.env
```

Should point to: `/workspace/ComfyUI/output`

### Printify Publish Fails

**Test API connection:**
```bash
curl https://api.printify.com/v1/shops.json \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Check gateway logs:**
```bash
tail -50 /var/log/gateway.log | grep -i printify
```

**Common issues:**
- Invalid API key → Regenerate in Printify dashboard
- Wrong shop ID → Verify with API call above
- Image too large → Max 20MB, resize if needed

### Services Die After Restart

**Enable auto-start:**

1. SSH into RunPod
2. Add to `~/.bashrc`:
   ```bash
   echo "/workspace/start-pod.sh" >> ~/.bashrc
   ```
3. Or use `screen`:
   ```bash
   screen -dmS pod /workspace/start-pod.sh
   ```

---

## 💰 Cost Optimization

### Recommended GPU Tiers

| GPU | VRAM | Speed | Cost/hr | Best For |
|-----|------|-------|---------|----------|
| RTX 3090 | 24GB | Good | $0.34 | Budget |
| RTX A4000 | 16GB | Fast | $0.44 | Recommended |
| RTX A5000 | 24GB | Faster | $0.76 | High volume |

### Tips to Save Money

1. **Use Spot Instances** (50-70% cheaper)
   - Risk: Can be terminated anytime
   - Good for: Non-critical work

2. **Stop When Not Using**
   - Stop pod via dashboard
   - Volume persists your data
   - Only pay for storage (~$0.10/GB/month)

3. **Batch Processing**
   - Generate 100 designs in one session
   - Approve/publish later
   - Minimize active hours

### Example Monthly Costs

**Light use** (1 hour/day):
- GPU: $13/month (1hr × $0.44 × 30 days)
- Storage: $5/month (50GB volume)
- **Total: ~$18/month**

**Medium use** (4 hours/day):
- GPU: $53/month
- Storage: $5/month
- **Total: ~$58/month**

**Heavy use** (24/7):
- GPU: $316/month
- Storage: $5/month
- **Total: ~$321/month**

---

## 🔒 Security Best Practices

### 1. Protect API Keys

✅ **DO:**
- Store in `.env` file (not committed to git)
- Use RunPod environment variables for Docker deployments
- Rotate keys regularly

❌ **DON'T:**
- Hardcode in scripts
- Share in screenshots
- Commit to public repos

### 2. Network Security

- ✅ RunPod provides HTTPS by default
- ✅ Use firewall rules if deploying elsewhere
- ✅ Add authentication to gateway (future feature)

### 3. Data Privacy

- Images stored in `/workspace/ComfyUI/output/`
- State stored in `/workspace/gateway-state/state.json`
- Both persist on RunPod volume
- Delete sensitive images after publishing

---

## 🚀 Advanced Configuration

### Custom Printify Product Types

Edit `.env`:
```bash
# T-shirt (default)
PRINTIFY_BLUEPRINT_ID=3
PRINTIFY_PROVIDER_ID=99

# Hoodie
PRINTIFY_BLUEPRINT_ID=6
PRINTIFY_PROVIDER_ID=99

# Mug
PRINTIFY_BLUEPRINT_ID=19
PRINTIFY_PROVIDER_ID=99
```

Find more IDs: [Printify Blueprints API](https://developers.printify.com/#blueprints)

### Auto-Publish on Approval

Edit `.env`:
```bash
AUTO_PUBLISH=true
```

Gateway will auto-publish approved images (use with caution!)

### Change Gateway Port

Edit `.env`:
```bash
FLASK_PORT=8080
```

Then expose port 8080 in RunPod UI.

---

## 📚 Additional Resources

- **POD Gateway Documentation**: [gateway/README.md](gateway/README.md)
- **Printify API Docs**: https://developers.printify.com/
- **ComfyUI Docs**: https://github.com/comfyanonymous/ComfyUI
- **RunPod Docs**: https://docs.runpod.io/

---

## 🆘 Getting Help

### Check Logs First

```bash
# Service status
/workspace/status-pod.sh

# Recent errors
tail -100 /var/log/gateway.log | grep -i error
tail -100 /var/log/comfyui.log | grep -i error
```

### Common Commands

```bash
# Restart everything
/workspace/stop-pod.sh && /workspace/start-pod.sh

# Test gateway API
curl http://localhost:5000/health

# Test ComfyUI API
curl http://localhost:8188/system_stats

# Check processes
ps aux | grep python
```

### Still Stuck?

1. Check existing issues: [GitHub Issues](https://github.com/ssiens-oss/ssiens-oss-static_pod/issues)
2. Open new issue with:
   - RunPod GPU type
   - Error logs
   - Steps to reproduce

---

## ✅ Post-Setup Checklist

After completing setup, verify:

- [ ] ComfyUI accessible at port 8188
- [ ] POD Gateway accessible at port 5000
- [ ] Can generate test image in ComfyUI
- [ ] Image appears in gateway gallery
- [ ] Can approve image in gateway
- [ ] Can publish to Printify (test with one image)
- [ ] Product appears in Printify dashboard
- [ ] Services auto-restart after pod reboot

---

**Happy designing! 🎨**

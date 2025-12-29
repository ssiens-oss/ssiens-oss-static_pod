# StaticWaves POD Engine - RunPod Deployment Guide

Complete guide for deploying to RunPod GPU cloud infrastructure.

## 🚀 Quick Deploy (3 Minutes)

### Step 1: Create RunPod Pod

1. Go to https://www.runpod.io/console/pods
2. Click **+ Deploy**
3. Choose GPU:
   - **Budget**: RTX 4090 (~$0.44/hr = $317/month)
   - **Balanced**: RTX A5000 (~$0.64/hr = $460/month)
   - **Enterprise**: A100 (~$1.89/hr = $1,361/month)

4. Pod Configuration:
   ```
   Template: RunPod Pytorch 2.1
   Disk: 100 GB (minimum)
   Expose TCP Ports: 8000, 8188
   Persistent Volume: ENABLED (critical!)
   ```

5. Click **Deploy On-Demand**

### Step 2: One-Command Install

Once your pod is running, click **Connect** → **Start Web Terminal**, then run:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ssiens-oss/ssiens-oss-static_pod/main/pod-engine/runpod_install.sh)
```

⏱️ Install time: 5-8 minutes (depending on GPU/network)

### Step 3: Configure API Keys

```bash
nano /workspace/pod-engine/.env
```

Add your keys:
```env
PRINTIFY_API_KEY=your_key_here
PRINTIFY_SHOP_ID=your_shop_id
SHOPIFY_STORE=yourstore
SHOPIFY_TOKEN=shpat_xxxxx
```

Save (Ctrl+O) and exit (Ctrl+X).

### Step 4: Restart Services

```bash
supervisorctl restart staticwaves:*
```

### Step 5: Access Your Pod

Get your POD ID from the RunPod dashboard (top of the screen), then access:

- **ComfyUI**: `https://{POD_ID}-8188.proxy.runpod.net`
- **API**: `https://{POD_ID}-8000.proxy.runpod.net`
- **Health**: `https://{POD_ID}-8000.proxy.runpod.net/health`

✅ **You're live!**

---

## 📊 RunPod Architecture

```
RunPod GPU Pod
├── /workspace (persistent storage)
│   ├── ComfyUI/ (port 8188)
│   ├── pod-engine/ (port 8000)
│   │   ├── workers/ (background)
│   │   ├── queues/
│   │   └── .env
│   ├── queues/
│   │   ├── incoming/
│   │   ├── done/
│   │   ├── failed/
│   │   └── published/
│   └── logs/
```

### Port Mapping

| Service | Internal | RunPod Proxy |
|---------|----------|--------------|
| ComfyUI | 8188 | `{POD_ID}-8188.proxy.runpod.net` |
| POD API | 8000 | `{POD_ID}-8000.proxy.runpod.net` |

---

## 🔧 Management Commands

### Check Service Status

```bash
supervisorctl status
```

Expected output:
```
comfyui                          RUNNING   pid 1234
pod-api                          RUNNING   pid 1235
printify-worker                  RUNNING   pid 1236
shopify-worker                   RUNNING   pid 1237
```

### Restart Services

```bash
# Restart all
supervisorctl restart staticwaves:*

# Restart specific service
supervisorctl restart comfyui
supervisorctl restart printify-worker
```

### View Logs

```bash
# Real-time logs
tail -f /workspace/logs/comfyui.log
tail -f /workspace/logs/printify.log

# All logs
ls -lh /workspace/logs/
```

### Check Queue Status

```bash
# Via API
curl https://{POD_ID}-8000.proxy.runpod.net/queues

# Via filesystem
ls -la /workspace/queues/incoming/
ls -la /workspace/queues/published/
```

---

## 💰 Cost Optimization

### Single Pod Strategy (Best for Starting)

**Setup**: 1x RTX 4090
- **Cost**: ~$317/month (24/7)
- **Capacity**: 10-30 clients
- **Revenue Target**: $15k-$50k/month
- **Profit**: $14k-$49k/month

### Multi-Pod Strategy (Agency Scale)

**Setup**: 3x RTX 4090 pods
- **Cost**: ~$950/month
- **Capacity**: 50-100 clients
- **Revenue Target**: $75k-$150k/month
- **Profit**: $74k-$149k/month

### GPU Cluster Strategy (Enterprise)

**Setup**:
- 1x Control Pod (CPU) - $40/month
- 5x GPU Pods (A100) - $6,800/month
- **Total**: ~$6,840/month
- **Capacity**: 200+ clients
- **Revenue Target**: $300k+/month

### Cost Saving Tips

1. **Auto-Pause**: Use RunPod's auto-pause when idle (saves 80%+)
2. **Spot Instances**: Use spot pricing (saves 50%+, less reliable)
3. **Right-Size**: Start small, scale as revenue grows
4. **GPU Selection**: RTX 4090 = best price/performance for POD work

---

## 🔒 Persistent Storage

**CRITICAL**: Always enable persistent volume!

Your `/workspace` directory survives pod restarts and contains:
- ComfyUI models (large!)
- Queue data
- Client workspaces
- Generated products
- Logs

### Backup Strategy

```bash
# Backup to S3
apt-get install rclone
rclone config  # Configure S3
rclone sync /workspace/pod-engine s3:backup/pod-engine
rclone sync /workspace/queues s3:backup/queues
```

### Data Recovery

If pod crashes:
1. Spin new pod with **same persistent volume**
2. Run installer again
3. Data is preserved automatically

---

## 🎨 ComfyUI Setup

### Add Models

```bash
cd /workspace/ComfyUI/models/checkpoints

# Download from Hugging Face
wget https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors

# Or upload via RunPod file manager
```

### Test ComfyUI

1. Open: `https://{POD_ID}-8188.proxy.runpod.net`
2. Load default workflow
3. Queue prompt
4. Check output in `/workspace/ComfyUI/output/`

---

## 📈 Monitoring

### Health Check

```bash
curl https://{POD_ID}-8000.proxy.runpod.net/health
```

Response:
```json
{
  "status": "healthy",
  "comfyui": "running",
  "cpu_percent": 15.2,
  "memory_percent": 42.1,
  "disk_usage": 23.4
}
```

### GPU Usage

```bash
nvidia-smi

# Watch in real-time
watch -n 1 nvidia-smi
```

### Disk Space

```bash
df -h /workspace
```

---

## 🔥 Troubleshooting

### ComfyUI Won't Start

```bash
# Check logs
tail -100 /workspace/logs/comfyui.err.log

# Check if port is in use
netstat -tlnp | grep 8188

# Restart manually
cd /workspace/ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188
```

### Workers Not Processing

```bash
# Check worker logs
tail -f /workspace/logs/printify.log

# Verify API keys
cat /workspace/pod-engine/.env | grep API_KEY

# Restart workers
supervisorctl restart printify-worker
supervisorctl restart shopify-worker
```

### Out of Disk Space

```bash
# Clear old queues
rm -rf /workspace/queues/failed/*
rm -rf /workspace/queues/done/*

# Clear ComfyUI outputs
rm -rf /workspace/ComfyUI/output/*

# Check what's using space
du -sh /workspace/*
```

### Out of Memory

```bash
# Check memory
free -h

# Restart all services
supervisorctl restart staticwaves:*

# Reduce concurrent jobs
nano /workspace/pod-engine/.env
# Set lower limits
```

---

## 🚀 Advanced: Multi-Client Setup

### Create Client Workspace

```bash
cd /workspace/pod-engine
python3 << 'EOF'
import json
from pathlib import Path

client = "client_acme"
Path(f"clients/{client}/queues/incoming").mkdir(parents=True, exist_ok=True)
Path(f"clients/{client}/queues/done").mkdir(parents=True, exist_ok=True)

limits = {
    "products_per_month": 50,
    "gpu_minutes": 500
}

Path(f"clients/{client}/limits.json").write_text(json.dumps(limits, indent=2))
print(f"✅ Created client: {client}")
EOF
```

### Client-Specific Queues

```bash
# Client uploads images to:
/workspace/clients/client_acme/queues/incoming/

# Outputs go to:
/workspace/clients/client_acme/queues/published/
```

---

## 🌍 Multiple Regions

### Primary Region (US)

```bash
# Deploy main pod in US-East
# Lowest latency for US clients
```

### Secondary Region (EU)

```bash
# Deploy backup pod in EU-West
# Failover + EU client support
```

### Sync Strategy

```bash
# On primary pod
rclone sync /workspace s3:primary-backup

# On secondary pod (disaster recovery)
rclone sync s3:primary-backup /workspace
```

---

## 📱 Connect to Dashboard

Update your frontend `.env`:

```env
VITE_API_URL=https://{POD_ID}-8000.proxy.runpod.net
VITE_COMFY_URL=https://{POD_ID}-8188.proxy.runpod.net
```

Deploy frontend (Vercel/Netlify/etc.) with these URLs.

---

## 💡 Pro Tips

1. **Enable Auto-Start**: Use supervisor to auto-start on pod boot
2. **Monitor Costs**: Set RunPod budget alerts
3. **Use Templates**: Save your configured pod as a template
4. **Backup Weekly**: Automate S3 backups with cron
5. **Log Rotation**: Set up logrotate to prevent disk fill

---

## 🎯 Production Checklist

Before going live with clients:

- [ ] Persistent volume enabled
- [ ] API keys configured
- [ ] ComfyUI models loaded
- [ ] All workers running
- [ ] Health endpoint responding
- [ ] Queues processing correctly
- [ ] Logs writing properly
- [ ] Backup system configured
- [ ] Monitoring alerts set
- [ ] Client workspaces created

---

## 📞 Support

**RunPod Issues**: https://www.runpod.io/support
**POD Engine Issues**: GitHub Issues
**Emergency**: Check logs first, then restart services

---

## 🎓 Next Steps

1. ✅ Deploy to RunPod
2. ✅ Configure API keys
3. ✅ Test with sample images
4. ✅ Add first client workspace
5. 🚀 Start generating revenue!

Your RunPod-powered POD automation platform is ready to print money! 💰

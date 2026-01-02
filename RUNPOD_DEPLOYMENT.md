# RunPod Deployment Guide - POD Pipeline GUI

Complete guide to deploying the POD Pipeline GUI with ComfyUI on RunPod cloud infrastructure.

## Overview

This deployment provides:
- **POD Pipeline GUI** (Port 80) - Multi-platform automation interface
- **Original POD Studio** (Port 8080) - Legacy interface
- **Music Studio** (Port 8081) - AI music generation
- **ComfyUI API** (Port 8188) - AI image generation backend
- **GPU Acceleration** - NVIDIA RTX A4000 or better
- **50GB Volume** - Persistent storage for designs and models

## Prerequisites

### 1. Docker Hub Account
Create account at: https://hub.docker.com

### 2. RunPod Account
Sign up at: https://www.runpod.io

### 3. RunPod API Key
1. Login to RunPod
2. Go to: https://www.runpod.io/console/user/settings
3. Create new API key
4. Save it securely

### 4. Docker Installed Locally
- **Mac**: Docker Desktop
- **Linux**: `sudo apt install docker.io`
- **Windows**: Docker Desktop with WSL2

## Quick Deployment

### Option 1: Automated Script (Recommended)

```bash
# Set your credentials
export DOCKER_USERNAME=your-dockerhub-username
export RUNPOD_API_KEY=your-runpod-api-key

# Deploy
./deploy-to-runpod.sh
```

**What this does:**
1. Builds Docker image with POD Pipeline GUI + ComfyUI
2. Pushes to Docker Hub
3. Deploys to RunPod with GPU
4. Returns pod ID and access URL

### Option 2: Manual Deployment

#### Step 1: Build Docker Image

```bash
docker build -f Dockerfile.runpod -t staticwaves-pod-pipeline:latest .
```

#### Step 2: Tag for Docker Hub

```bash
# Replace 'yourusername' with your Docker Hub username
docker tag staticwaves-pod-pipeline:latest yourusername/staticwaves-pod-pipeline:latest
```

#### Step 3: Push to Docker Hub

```bash
docker login
docker push yourusername/staticwaves-pod-pipeline:latest
```

#### Step 4: Deploy on RunPod

1. Login to RunPod: https://www.runpod.io/console/pods
2. Click **"Deploy"** or **"+ GPU Pod"**
3. Select **"Deploy Custom Container"**
4. Configure:
   - **Container Image**: `yourusername/staticwaves-pod-pipeline:latest`
   - **Container Disk**: 50 GB
   - **Volume**: 50 GB
   - **GPU Type**: NVIDIA RTX A4000 (or better)
   - **Expose Ports**: `80/http,8080/http,8081/http,8188/http`
5. Click **"Deploy"**

## Accessing Your Deployment

### Get Your Pod URL

1. Go to: https://www.runpod.io/console/pods
2. Find your pod: `pod-pipeline-gui`
3. Click **"Connect"**
4. Copy the **"Connect to HTTP Service [Port 80]"** URL

### Application URLs

Replace `[your-pod-id]` with your actual RunPod pod ID:

- **POD Pipeline GUI**: `https://[your-pod-id]-80.proxy.runpod.net`
- **Original POD Studio**: `https://[your-pod-id]-8080.proxy.runpod.net`
- **Music Studio**: `https://[your-pod-id]-8081.proxy.runpod.net`
- **ComfyUI API**: `https://[your-pod-id]-8188.proxy.runpod.net`

## Configuration

### Environment Variables

To set environment variables for API keys, edit the deployment script or set them in RunPod UI:

```bash
ANTHROPIC_API_KEY=sk-ant-...
PRINTIFY_API_KEY=...
SHOPIFY_ACCESS_TOKEN=...
TIKTOK_APP_KEY=...
# etc.
```

### Persistent Storage

The deployment includes a 50GB volume mounted at `/data`:
- Generated designs: `/data/designs`
- Chrome profile: `/data/chrome-profile`
- ComfyUI models: `/workspace/ComfyUI/models`

## Monitoring

### Check Pod Status

```bash
# Using RunPod API
curl -X POST https://api.runpod.io/graphql?api_key=YOUR_API_KEY \
  -H "Content-Type: application/json" \
  -d '{"query": "{ myself { pods { id name runtime { uptimeInSeconds } } } }"}'
```

### View Logs

SSH into your pod:
1. Click **"Connect"** in RunPod console
2. Use **"Start Web Terminal"** or SSH

```bash
# ComfyUI logs
tail -f /var/log/comfyui.log

# Nginx logs
tail -f /var/log/nginx.log

# Check running processes
ps aux | grep -E "comfyui|nginx"
```

### Health Check

```bash
# Check if services are running
curl https://[your-pod-id]-80.proxy.runpod.net/health
curl https://[your-pod-id]-8188.proxy.runpod.net/system_stats
```

## Cost Optimization

### GPU Options

| GPU | VRAM | Performance | Cost/hr |
|-----|------|-------------|---------|
| RTX A4000 | 16GB | Good | ~$0.34 |
| RTX A5000 | 24GB | Better | ~$0.44 |
| RTX A6000 | 48GB | Best | ~$0.79 |

**Recommendation**: RTX A4000 is sufficient for most use cases.

### Auto-Stop

Set up auto-stop to save costs:
1. Go to pod settings
2. Set **"Idle Timeout"**: 30 minutes
3. Pod will stop when idle (no API requests)

### Volume Storage

- Volume costs: ~$0.10/GB/month
- Container disk is ephemeral (free)
- Only store important data on volumes

## Troubleshooting

### Issue: Pod fails to start

**Check:**
- Docker image was pushed successfully
- Sufficient GPU availability
- Correct port configuration

**Solution:**
```bash
# View pod logs in RunPod console
# Look for startup errors
```

### Issue: ComfyUI not responding

**Check:**
```bash
# SSH into pod
tail -f /var/log/comfyui.log

# Restart ComfyUI
pkill -f "main.py"
cd /workspace/ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188 &
```

### Issue: "Out of memory" errors

**Solutions:**
- Upgrade to GPU with more VRAM (RTX A5000 or A6000)
- Reduce batch size in generation settings
- Lower image resolution (1024→768)

### Issue: Cannot access web UI

**Check:**
- Pod is running (not stopped)
- Ports are correctly exposed
- Using HTTPS (not HTTP) for proxy URLs

**Solution:**
```bash
# Check nginx status
curl http://localhost/health

# Restart nginx
pkill nginx
nginx -g "daemon off;" &
```

### Issue: Slow image generation

**Solutions:**
- Ensure GPU is being used (check ComfyUI logs)
- Download models to local storage
- Upgrade to faster GPU

## Advanced Configuration

### Custom Models

SSH into pod and download models:

```bash
cd /workspace/ComfyUI/models/checkpoints

# Download SDXL base model
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

# Download custom LoRA
cd ../loras
wget [your-lora-url]
```

### Update Application

To update to latest version:

```bash
# Rebuild and push image locally
docker build -f Dockerfile.runpod -t yourusername/staticwaves-pod-pipeline:latest .
docker push yourusername/staticwaves-pod-pipeline:latest

# In RunPod, stop and delete old pod
# Create new pod with same image name
# RunPod will pull latest version
```

### Backup Data

```bash
# SSH into pod
cd /data
tar -czf backup-$(date +%Y%m%d).tar.gz designs/

# Download via RunPod file browser or SCP
```

## Security

### Best Practices

1. **Don't expose sensitive ports publicly**
   - Keep ComfyUI API internal if possible
   - Use RunPod proxy URLs with authentication

2. **Rotate API keys regularly**
   - Update environment variables
   - Restart pod after changes

3. **Monitor usage**
   - Check RunPod billing dashboard
   - Set spending limits

4. **Secure credentials**
   - Never commit API keys to git
   - Use environment variables
   - Consider RunPod secrets management

## API Integration

### Connecting to ComfyUI from External Apps

```javascript
// Use RunPod proxy URL
const COMFYUI_URL = 'https://[your-pod-id]-8188.proxy.runpod.net'

const response = await fetch(`${COMFYUI_URL}/prompt`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: { /* your workflow */ }
  })
})
```

### WebSocket Connection

```javascript
const ws = new WebSocket('wss://[your-pod-id]-8188.proxy.runpod.net/ws')

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log('Progress:', data)
}
```

## Performance Benchmarks

| Operation | RTX A4000 | RTX A5000 | RTX A6000 |
|-----------|-----------|-----------|-----------|
| 1024x1024 SDXL (20 steps) | ~8s | ~6s | ~4s |
| Batch 10 designs | ~80s | ~60s | ~40s |
| Model loading | ~5s | ~4s | ~3s |

## Support

### Resources

- **RunPod Documentation**: https://docs.runpod.io
- **ComfyUI Documentation**: https://github.com/comfyanonymous/ComfyUI
- **POD Pipeline GUI Docs**: [POD_PIPELINE_GUI.md](POD_PIPELINE_GUI.md)

### Common Issues

1. **Pod won't start**: Check GPU availability in your region
2. **High costs**: Enable auto-stop and monitor usage
3. **Slow performance**: Upgrade GPU or optimize workflow
4. **Connection errors**: Verify ports are exposed correctly

## Cleanup

### Stop Pod

```bash
# Via RunPod console
# Click pod → "Stop Pod"

# Via API
curl -X POST https://api.runpod.io/graphql?api_key=YOUR_API_KEY \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { podStop(input: {podId: \"YOUR_POD_ID\"}) { id } }"}'
```

### Delete Pod

```bash
# Via RunPod console
# Click pod → "Terminate Pod"

# This will delete the pod and container disk
# Volume will be preserved (can be deleted separately)
```

### Delete Volume

```bash
# Via RunPod console
# Go to "Storage" → Select volume → "Delete"
```

---

## Next Steps

1. Deploy your pod using the script
2. Access the POD Pipeline GUI
3. Configure your platforms (Shopify, TikTok, etc.)
4. Start generating and publishing designs!

For detailed usage instructions, see [POD_PIPELINE_GUI.md](POD_PIPELINE_GUI.md).

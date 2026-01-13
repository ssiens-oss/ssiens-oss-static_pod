# Production Deployment Guide

Complete guide for deploying the StaticWaves POD Pipeline to production environments.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Deployment Options](#deployment-options)
- [RunPod Deployment](#runpod-deployment)
- [Docker Deployment](#docker-deployment)
- [Post-Deployment](#post-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- **Docker** (v20.10+) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Hub Account** (or GHCR) - For container registry
- **RunPod Account** - For cloud deployment (optional)

### Required API Keys

1. **Anthropic Claude API** - [Get API Key](https://console.anthropic.com/)
2. **Printify Account** - [Sign Up](https://printify.com/)
3. **RunPod API Key** - For automated deployment (optional)

### Optional Platform Credentials

- Shopify store and access token
- TikTok Shop credentials
- Etsy API key
- Instagram Business account
- Facebook Page credentials

## Environment Configuration

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Configure Required Variables

Edit `.env` and set these **required** variables:

```bash
# ComfyUI
COMFYUI_API_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=/data/comfyui/output

# Claude AI
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Storage
STORAGE_TYPE=local
STORAGE_PATH=/data/designs

# Printify
PRINTIFY_API_KEY=your-printify-api-key
PRINTIFY_SHOP_ID=your-shop-id
```

### 3. Validate Configuration

Run the validation script to ensure all required variables are set:

```bash
./scripts/validate-env.sh
```

This will check your configuration and report any missing required variables.

## Deployment Options

### Quick Comparison

| Option | Best For | GPU Required | Cost | Setup Time |
|--------|----------|--------------|------|------------|
| **RunPod** | Production, AI generation | Yes | Pay-per-use | 10 min |
| **Docker Local** | Development, testing | Optional | Free | 5 min |
| **VPS/Cloud** | Custom infrastructure | Optional | Monthly | 30 min |

## RunPod Deployment

### Automated Deployment (Recommended)

The easiest way to deploy to RunPod:

```bash
export DOCKER_USERNAME=your-dockerhub-username
export RUNPOD_API_KEY=your-runpod-api-key
export DEPLOY_TARGET=both

./scripts/deploy-production.sh
```

**What this does:**
1. ✅ Builds production Docker image
2. ✅ Pushes to Docker Hub
3. ✅ Creates RunPod pod with GPU
4. ✅ Configures networking and ports
5. ✅ Sets up health checks

### Manual RunPod Deployment

If you prefer manual control:

#### Step 1: Build and Push Image

```bash
# Build
docker build -f Dockerfile.runpod -t pod-pipeline:latest .

# Tag for your registry
docker tag pod-pipeline:latest yourusername/pod-pipeline:latest

# Push
docker push yourusername/pod-pipeline:latest
```

#### Step 2: Create Pod via RunPod UI

1. Go to [RunPod Dashboard](https://www.runpod.io/)
2. Click **Deploy** → **Deploy a Custom Container**
3. Configure:
   - **Image**: `yourusername/pod-pipeline:latest`
   - **GPU**: NVIDIA RTX A4000 (or better)
   - **vCPU**: 4+
   - **Memory**: 16GB+
   - **Container Disk**: 50GB
   - **Volume**: 50GB (persistent storage)
   - **Ports**: `80/http, 8188/http, 5000/http`

4. Add environment variables from your `.env` file

5. Click **Deploy**

#### Step 3: Access Your Deployment

Once deployed, RunPod will provide:
- **HTTP Endpoint**: `https://your-pod-id-80.proxy.runpod.net`
- **ComfyUI API**: `https://your-pod-id-8188.proxy.runpod.net`

### RunPod Configuration Details

#### Recommended GPU Settings

```json
{
  "cloudType": "ALL",
  "gpuCount": 1,
  "gpuTypeId": "NVIDIA RTX A4000",
  "minVcpuCount": 4,
  "minMemoryInGb": 16,
  "volumeInGb": 50,
  "containerDiskInGb": 50
}
```

#### Cost Estimate

- **GPU Pod**: ~$0.40/hour (RTX A4000)
- **Storage**: ~$0.10/GB/month
- **Monthly (24/7)**: ~$300/month
- **Cost per design**: ~$0.05

💡 **Cost Saving Tip**: Use **Spot Instances** for 50-70% savings

## Docker Deployment

### Local Development

```bash
# Build
docker build -f Dockerfile.runpod -t pod-pipeline:latest .

# Run
docker run -d \
  --name pod-pipeline \
  -p 80:80 \
  -p 8188:8188 \
  -v $(pwd)/data:/data \
  --env-file .env \
  pod-pipeline:latest
```

Access at: `http://localhost`

### VPS/Cloud Server Deployment

For deploying to a VPS (DigitalOcean, AWS EC2, etc.):

#### Requirements

- Ubuntu 22.04 LTS
- 4+ CPU cores
- 16GB+ RAM
- 100GB+ storage
- NVIDIA GPU (for ComfyUI)

#### Setup Steps

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Install NVIDIA Container Toolkit (if using GPU)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# 3. Clone repository
git clone https://github.com/yourusername/pod-pipeline.git
cd pod-pipeline

# 4. Configure environment
cp .env.example .env
nano .env

# 5. Deploy
./scripts/deploy-production.sh
```

## Post-Deployment

### 1. Verify Services

Check all services are running:

```bash
# Health check
curl https://your-pod-url/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-13T10:30:00Z",
  "service": "pod-pipeline"
}

# ComfyUI check
curl https://your-pod-url:8188/system_stats
```

### 2. Test Pipeline

Run a test design generation:

1. Access the web UI
2. Configure a simple design (1 count)
3. Click **Run Single Drop**
4. Monitor the progress

### 3. Configure Platforms

Set up your sales platforms:

```bash
# In your .env file
ENABLE_PLATFORMS=printify,shopify,etsy
```

### 4. Set Up Monitoring

#### Basic Monitoring

Monitor container health:

```bash
# For Docker
docker ps
docker logs pod-pipeline

# For RunPod
# Use RunPod dashboard logs viewer
```

#### Advanced Monitoring (Optional)

Set up webhook notifications:

```bash
# In .env
WEBHOOK_URL=https://your-webhook-url.com
WEBHOOK_ON_SUCCESS=true
WEBHOOK_ON_ERROR=true
```

## Monitoring & Maintenance

### Health Checks

The deployment includes automatic health checks:

- **Nginx**: Every 30s via `/health` endpoint
- **ComfyUI**: Every 30s via `/system_stats`
- **Auto-restart**: Failed services restart automatically

### Log Access

#### Docker Logs

```bash
docker logs -f pod-pipeline
```

#### RunPod Logs

Access via RunPod dashboard → Pod → Logs tab

### Backups

#### Automatic Backups

Designs are automatically saved to your configured storage:
- **Local**: `/data/designs`
- **S3**: Your configured bucket
- **GCS**: Your configured bucket

#### Manual Backup

```bash
# Backup designs
docker cp pod-pipeline:/data/designs ./backup-$(date +%Y%m%d)

# Backup configuration
cp .env .env.backup-$(date +%Y%m%d)
```

### Updates

To update your deployment:

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild
docker build -f Dockerfile.runpod -t pod-pipeline:v2 .

# 3. Stop old container
docker stop pod-pipeline && docker rm pod-pipeline

# 4. Start new version
docker run -d \
  --name pod-pipeline \
  -p 80:80 -p 8188:8188 \
  --env-file .env \
  pod-pipeline:v2
```

## Troubleshooting

### Services Not Starting

**Check logs:**
```bash
docker logs pod-pipeline
# Look for startup errors
```

**Common issues:**
- Missing API keys → Check `.env` file
- Port conflicts → Change ports in `docker run`
- Insufficient memory → Increase container limits

### ComfyUI Connection Failed

**Verify ComfyUI is running:**
```bash
curl http://localhost:8188/system_stats
```

**If not responding:**
```bash
# Check ComfyUI logs
docker exec pod-pipeline cat /var/log/comfyui.log
```

### Image Generation Fails

**Check:**
1. SDXL model is downloaded
2. GPU is accessible (for RunPod)
3. ComfyUI has sufficient VRAM
4. Prompt is valid

**Debug:**
```bash
# Access container
docker exec -it pod-pipeline bash

# Check GPU
nvidia-smi

# Test ComfyUI directly
curl -X POST http://localhost:8188/prompt \
  -H "Content-Type: application/json" \
  -d @test-workflow.json
```

### Platform Integration Issues

**Printify:**
```bash
# Test API access
curl https://api.printify.com/v1/shops.json \
  -H "Authorization: Bearer $PRINTIFY_API_KEY"
```

**Shopify:**
```bash
# Test store access
curl https://$SHOPIFY_STORE_URL/admin/api/2024-01/products.json \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

### Performance Optimization

**Slow generation:**
1. Use GPU-enabled instance
2. Upgrade to faster GPU (RTX A5000/A6000)
3. Increase batch size
4. Optimize ComfyUI workflow

**High costs:**
1. Use Spot Instances (50-70% savings)
2. Auto-stop when not in use
3. Use CPU for non-generation tasks
4. Optimize image sizes

## Security Best Practices

### 1. Environment Variables

- ✅ Never commit `.env` to git
- ✅ Use strong, unique API keys
- ✅ Rotate keys regularly
- ✅ Use secrets management in production

### 2. Network Security

- ✅ Use HTTPS in production (RunPod provides this)
- ✅ Restrict API access to trusted IPs
- ✅ Enable firewall rules
- ✅ Use VPC for sensitive data

### 3. Access Control

- ✅ Add authentication to web UI
- ✅ Use separate API keys per environment
- ✅ Implement rate limiting
- ✅ Monitor API usage

## Cost Optimization

### RunPod Strategies

1. **Use Spot Instances**: 50-70% cheaper
2. **Auto-stop**: Stop pods when not in use
3. **Right-size**: Use smallest GPU that works
4. **Batch processing**: Generate multiple designs per session

### Storage Optimization

1. **Compress images**: Reduce storage costs
2. **Clean old designs**: Remove unused files
3. **Use lifecycle policies**: Auto-delete old files (S3/GCS)

### Example Monthly Costs

**Light usage** (10 designs/day):
- RunPod GPU: ~$30/month (1 hour/day)
- Storage: ~$5/month
- APIs: ~$20/month
- **Total: ~$55/month**

**Medium usage** (50 designs/day):
- RunPod GPU: ~$120/month (4 hours/day)
- Storage: ~$10/month
- APIs: ~$50/month
- **Total: ~$180/month**

**Heavy usage** (200 designs/day):
- RunPod GPU: ~$300/month (24/7 with auto-scaling)
- Storage: ~$30/month
- APIs: ~$120/month
- **Total: ~$450/month**

## Support & Resources

- 📚 **Documentation**: README.md, SETUP_GUIDE.md
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/pod-pipeline/issues)
- 💬 **Community**: [Discord Server](https://discord.gg/yourserver)
- 📧 **Support**: support@yourproject.com

## Next Steps

After deployment:

1. ✅ Verify all services are healthy
2. ✅ Test the complete pipeline
3. ✅ Configure your sales platforms
4. ✅ Set up monitoring and alerts
5. ✅ Create your first product batch!

---

**Happy deploying! 🚀**

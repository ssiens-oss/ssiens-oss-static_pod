# RunPod Serverless Production Deployment Instructions

## Quick Start (5 Minutes)

Your deployment script is ready! Follow these steps to deploy to RunPod:

### Prerequisites

1. **Docker Desktop** must be installed and running on your local machine:
   - **macOS/Windows**: Download from https://www.docker.com/products/docker-desktop
   - **Linux**: Run `curl -fsSL https://get.docker.com | sh`

2. **Docker Hub Account** - You're using: `staticwaves`
   - Make sure you can log in at https://hub.docker.com

3. **RunPod Account** with API access
   - Your API key is already configured in the deployment script

### Deployment Steps

#### Option 1: Automated Deployment (Recommended)

```bash
# Run the automated deployment script
./deploy-to-runpod.sh
```

This script will:
1. ✅ Check that Docker is installed and running
2. 📦 Build the production Docker image (5-10 minutes)
3. 🚀 Push to Docker Hub registry
4. ☁️ Deploy to RunPod serverless
5. 🎉 Provide your access URLs

#### Option 2: Manual Deployment

If you prefer to run the steps manually:

```bash
# 1. Build the Docker image
docker build -f Dockerfile.runpod -t staticwaves-pod-pipeline:latest .

# 2. Tag for Docker Hub
docker tag staticwaves-pod-pipeline:latest staticwaves/staticwaves-pod-pipeline:latest

# 3. Login to Docker Hub
docker login -u staticwaves

# 4. Push to Docker Hub
docker push staticwaves/staticwaves-pod-pipeline:latest

# 5. Deploy to RunPod (use the existing script)
DOCKER_USERNAME=staticwaves \
RUNPOD_API_KEY=rpa_ZLK5MWU94JE5RJLBF7J0GFTKXY6LHPPPJJGRTI0X1q8bte \
DEPLOY_TARGET=runpod \
./scripts/deploy-production.sh
```

### After Deployment

1. **Wait for Pod to Start** (2-5 minutes)
   - Go to https://runpod.io/console/pods
   - Find your pod: `staticwaves-pod-pipeline-prod`
   - Wait for status: `RUNNING`

2. **Get Your URLs**
   - Click "Connect" on your pod
   - You'll see URLs like:
     - Web UI: `https://{pod-id}-80.proxy.runpod.net`
     - ComfyUI: `https://{pod-id}-8188.proxy.runpod.net`
     - POD Gateway: `https://{pod-id}-5000.proxy.runpod.net`

3. **Configure Environment Variables**
   - Click "Edit Pod" or connect via SSH
   - Upload your `.env` file with API keys:
     - `ANTHROPIC_API_KEY` - For Claude AI image generation
     - `PRINTIFY_API_KEY` - For print-on-demand
     - `SHOPIFY_ACCESS_TOKEN` - For store integration
     - Other platform credentials as needed

4. **Test Your Deployment**
   - Open the Web UI URL
   - Try generating a test design
   - Check the POD Gateway for approval workflow

## Deployment Configuration

### RunPod Specifications

Your deployment uses these specifications:
- **GPU**: NVIDIA RTX A4000 (or equivalent)
- **vCPU**: 4+ cores
- **Memory**: 16GB+
- **Container Disk**: 50GB
- **Persistent Volume**: 50GB (mounted at `/data`)
- **Ports**:
  - `80/http` - Web UI (Nginx)
  - `8188/http` - ComfyUI API
  - `5000/http` - POD Gateway
- **Cost**: ~$0.40/hour (or use Spot Instances for 50-70% savings)

### Environment Variables

Key environment variables to configure in your pod:

```bash
# Required for AI image generation
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# ComfyUI (pre-configured)
COMFYUI_API_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=/data/comfyui/output

# Printify Integration (Required)
PRINTIFY_API_KEY=your-key
PRINTIFY_SHOP_ID=your-shop-id
PRINTIFY_BLUEPRINT_ID=77  # 77=Hoodie, 3=T-Shirt
PRINTIFY_PROVIDER_ID=39   # 39=SwiftPOD

# Platform Integrations (Optional)
SHOPIFY_STORE_URL=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-token
ENABLE_PLATFORMS=shopify,printify,etsy

# Pipeline Settings
AUTO_PUBLISH=true
BATCH_SIZE=5
```

See `.env.example` for the complete list.

## Troubleshooting

### Build Errors

**Problem**: "Cannot connect to Docker daemon"
```bash
# Start Docker Desktop (macOS/Windows)
# Or on Linux:
sudo systemctl start docker
```

**Problem**: "No space left on device"
```bash
# Clean up Docker
docker system prune -a
```

### Deployment Errors

**Problem**: "Authentication required"
```bash
# Re-login to Docker Hub
docker login -u staticwaves
```

**Problem**: "RunPod API error"
- Check your API key at https://runpod.io/console/user/settings
- Ensure you have sufficient credits/balance
- Try a different GPU type if A4000 is unavailable

### Pod Not Starting

1. Check RunPod console for error messages
2. Verify the Docker image pushed successfully
3. Check pod logs in RunPod console
4. Try restarting the pod

## Cost Optimization

### Spot Instances (Recommended)
- 50-70% cheaper than on-demand
- Good for batch processing
- Configure in pod settings: "Cloud Type" → "Secure Cloud (Spot)"

### Auto-Pause
- Set idle timeout to pause pod when not in use
- Configure in pod settings: "Idle Timeout" → 5-15 minutes

### Volume Management
- Use persistent volumes only for essential data
- Clean up `/data/comfyui/output` regularly
- Archive completed designs to S3/GCS

## Monitoring

### Health Checks

```bash
# Check Web UI health
curl https://{pod-id}-80.proxy.runpod.net/health

# Check ComfyUI
curl https://{pod-id}-8188.proxy.runpod.net/system_stats

# Check POD Gateway
curl https://{pod-id}-5000.proxy.runpod.net/health
```

### Logs

Access logs through RunPod console:
1. Go to your pod
2. Click "Logs" tab
3. View real-time logs

Or via CLI:
```bash
# Install RunPod CLI
pip install runpod

# View logs
runpod logs {pod-id}
```

## Updating Your Deployment

To update your deployed pod with new code:

```bash
# 1. Make your code changes locally
# 2. Re-run the deployment script
./deploy-to-runpod.sh

# 3. In RunPod console, recreate the pod with the new image
# Or update the existing pod's image in settings
```

## Support & Documentation

- **General Guide**: `README.md`
- **Production Deployment**: `PRODUCTION_DEPLOYMENT.md`
- **Free Local Setup**: `FREE_DEPLOYMENT.md`
- **POD Gateway**: `POD_GATEWAY_INTEGRATION.md`
- **API Documentation**: `docs/API.md`

## Next Steps

After successful deployment:

1. ✅ Configure all required API keys
2. ✅ Test image generation with ComfyUI
3. ✅ Set up Printify products and templates
4. ✅ Connect your Shopify/Etsy stores
5. ✅ Run a full end-to-end test
6. ✅ Set up monitoring and alerts
7. ✅ Configure auto-pause for cost savings

## Security Notes

⚠️ **Important Security Reminders**:

1. **Never commit API keys** to version control
2. **Rotate your RunPod API key** periodically
3. **Use environment variables** for all secrets
4. **Enable HTTPS** for all external connections
5. **Restrict API access** to known IPs if possible
6. **Monitor pod access logs** regularly

---

**Deployment Script**: `./deploy-to-runpod.sh`
**Docker Hub**: https://hub.docker.com/r/staticwaves/staticwaves-pod-pipeline
**RunPod Console**: https://runpod.io/console/pods

Happy deploying! 🚀

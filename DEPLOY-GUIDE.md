# Full Stack Deployment Guide
## Local → Docker → RunPod → Printify Integration

This guide covers the complete deployment pipeline for StaticWaves POD Studio.

## Quick Start

```bash
# 1. Copy environment template
cp .env.deploy.example .env.deploy

# 2. Edit with your credentials
nano .env.deploy

# 3. Load environment variables
source .env.deploy

# 4. Run full deployment
./deploy-full-stack.sh
```

## Prerequisites

### Required
- Docker installed and running
- Docker Hub account
- RunPod account with credits

### Optional (for automation)
- RunPod API key
- Printify API key

## Step-by-Step Manual Deployment

### Step 1: Local Development

Ensure your project files are ready:

**For HTML version:**
```bash
cd ~/pod-studio-v6
ls *.html  # Verify HTML files exist
```

**For React version:**
```bash
cd ~/project-directory
npm install
npm run build
```

### Step 2: Build Docker Image

```bash
# Build the image
docker build -t staticwaves/staticwaves-pod-studio:latest .

# Test locally (optional)
docker run -p 8080:80 staticwaves/staticwaves-pod-studio:latest
# Visit: http://localhost:8080
```

### Step 3: Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Push image
docker push staticwaves/staticwaves-pod-studio:latest
```

### Step 4: Deploy to RunPod

#### Option A: Manual Deployment (Recommended for first time)

1. Go to https://www.runpod.io/console/pods
2. Click **"Deploy"** → **"Custom Container"**
3. Configure:
   - **Container Image**: `staticwaves/staticwaves-pod-studio:latest`
   - **Container Disk**: `10 GB`
   - **Expose HTTP Ports**: `80`
   - **GPU**: Select CPU (no GPU needed)
   - **vCPUs**: 2
   - **Memory**: 4 GB
4. Click **"Deploy"**
5. Wait for pod to start
6. Access via the provided HTTP URL

#### Option B: Automated Deployment (API)

```bash
# Set your RunPod API key
export RUNPOD_API_KEY="your_api_key_here"

# Run deployment script
./deploy-full-stack.sh
```

### Step 5: Auto-Kill Configuration (Cost Saving)

To automatically stop pods after a certain time:

**Option 1: RunPod Built-in (Recommended)**
1. Go to pod settings in RunPod dashboard
2. Set "Stop After" duration (e.g., 24 hours)
3. Pod will auto-stop to save costs

**Option 2: Custom Script**
```bash
# Schedule pod termination
export AUTO_KILL_HOURS=24
./deploy-full-stack.sh
```

### Step 6: Printify Integration

#### Get Printify API Key
1. Go to https://printify.com/app/account/api
2. Click "Create Token"
3. Copy the API token

#### Configure Webhook
1. In Printify dashboard, go to Settings → Webhooks
2. Add webhook URL: `https://YOUR-POD-URL/webhook/printify`
3. Select events:
   - `order:created`
   - `order:updated`
   - `order:sent-to-production`

#### Set Environment Variables in RunPod
1. Go to your pod in RunPod dashboard
2. Click "Edit"
3. Add environment variables:
   ```
   PRINTIFY_API_KEY=your_printify_api_key
   PRINTIFY_SHOP_ID=your_shop_id
   ```
4. Restart pod

## Automated Deployment Script

The `deploy-full-stack.sh` script automates the entire pipeline:

### Features
- ✅ Local environment validation
- ✅ Docker image build
- ✅ Local testing (optional)
- ✅ Push to Docker Hub
- ✅ RunPod deployment (manual or API)
- ✅ Health checks
- ✅ Printify API validation
- ✅ Webhook configuration

### Usage

**Basic usage:**
```bash
./deploy-full-stack.sh
```

**With environment variables:**
```bash
# Load from .env.deploy
source .env.deploy
./deploy-full-stack.sh

# Or inline
DOCKER_USERNAME=myusername \
RUNPOD_API_KEY=your_key \
PRINTIFY_API_KEY=your_key \
./deploy-full-stack.sh
```

**Custom version:**
```bash
VERSION=v1.2.3 ./deploy-full-stack.sh
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DOCKER_USERNAME` | Yes | Your Docker Hub username (default: staticwaves) |
| `VERSION` | No | Image version tag (default: latest) |
| `RUNPOD_API_KEY` | No | RunPod API key for automated deployment |
| `PRINTIFY_API_KEY` | No | Printify API key for integration |
| `AUTO_KILL_HOURS` | No | Hours before auto-termination (default: 24) |

## Troubleshooting

### Docker Build Fails

**Issue**: "COPY failed: no source files were specified"

**Solution**: Make sure you're in the correct directory with source files
```bash
cd ~/pod-studio-v6
ls *.html  # Should show your HTML files
```

### Docker Push Permission Denied

**Issue**: "denied: requested access to the resource is denied"

**Solution**:
1. Create repository on Docker Hub first
2. Make sure you're logged in: `docker login`
3. Check username matches: `docker info | grep Username`

### RunPod Pod Not Starting

**Issue**: Pod stuck in "Starting" status

**Solution**:
1. Check logs in RunPod dashboard
2. Verify image exists: `docker pull staticwaves/staticwaves-pod-studio:latest`
3. Check port configuration (should be 80)

### Application Shows Nginx Welcome Page

**Issue**: Default nginx page instead of your app

**Solution**: HTML files weren't copied during build
```bash
# Rebuild image
docker build -t staticwaves/staticwaves-pod-studio:latest .

# Verify files in image
docker run --rm staticwaves/staticwaves-pod-studio:latest ls -la /usr/share/nginx/html/

# Push updated image
docker push staticwaves/staticwaves-pod-studio:latest

# Terminate and redeploy pod in RunPod
```

### SSH Permission Denied

**Issue**: Can't SSH into RunPod pod

**Solution**:
1. Add SSH public key to RunPod:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
2. Go to https://www.runpod.io/console/user/settings
3. Add Public Key
4. Redeploy pod

### Printify API Connection Failed

**Issue**: "Printify API connection failed"

**Solution**:
1. Verify API key is correct
2. Check key permissions in Printify dashboard
3. Test manually:
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        https://api.printify.com/v1/shops.json
   ```

## Cost Optimization

### Pod Management
- Use **Spot Pods** instead of On-Demand (60-80% cheaper)
- Set auto-stop timers to prevent forgotten pods
- Use CPU pods (no GPU needed for this app)
- Monitor usage via RunPod dashboard

### Resource Allocation
- **Minimum viable**: 1 vCPU, 2 GB RAM
- **Recommended**: 2 vCPU, 4 GB RAM
- **Container Disk**: 10 GB sufficient

### Auto-Kill Script
```bash
# Stop pod after 24 hours of inactivity
# This can be set in RunPod dashboard or via API
```

## Production Checklist

Before going to production:

- [ ] Environment variables configured
- [ ] Printify API key set and tested
- [ ] Webhook URL configured in Printify
- [ ] HTTPS enabled (RunPod provides this)
- [ ] Health check endpoint working (`/health`)
- [ ] Monitoring and logging configured
- [ ] Auto-stop policy set
- [ ] Backup strategy defined
- [ ] Cost alerts configured in RunPod

## Support

- **RunPod**: https://docs.runpod.io/
- **Printify API**: https://developers.printify.com/
- **Docker**: https://docs.docker.com/

## Next Steps

After successful deployment:

1. **Test your application** at the provided URLs
2. **Configure Printify** integration and webhooks
3. **Set up monitoring** via RunPod logs
4. **Configure auto-stop** to manage costs
5. **Create a custom domain** (optional, via RunPod settings)
6. **Set up CI/CD** for automated deployments (GitHub Actions, etc.)

## Example Deployment Output

```
╔════════════════════════════════════════════════════════════╗
║  StaticWaves POD Studio - Full Stack Deployment Pipeline  ║
╚════════════════════════════════════════════════════════════╝

[1/7] Checking Local Environment...
✓ Docker found
✓ Dockerfile found
✓ HTML files found

[2/7] Building Docker Image...
✓ Docker image built successfully

[3/7] Local Testing
Test locally on port 8080? (y/n) n

[4/7] Pushing to Docker Hub...
✓ Image pushed to Docker Hub

[5/7] Deploying to RunPod...
✓ Pod deployed: abc123xyz

[6/7] Health Check...
✓ Health check passed

[7/7] Printify Integration Setup...
✓ Printify API connected

╔════════════════════════════════════════════════════════════╗
║            DEPLOYMENT COMPLETE                             ║
╚════════════════════════════════════════════════════════════╝

Docker Image: staticwaves/staticwaves-pod-studio:latest
RunPod URL: https://abc123xyz-80.proxy.runpod.net

Application URLs:
  • https://abc123xyz-80.proxy.runpod.net/pod-studio-automation.html
  • https://abc123xyz-80.proxy.runpod.net/pod-studio-pro.html
```

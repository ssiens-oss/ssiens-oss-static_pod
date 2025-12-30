# RunPod Deployment Guide

Complete guide for deploying StaticWaves POD Studio to RunPod cloud platform.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Deployment](#detailed-deployment)
- [Configuration](#configuration)
- [Scaling](#scaling)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required
- RunPod account ([Sign up](https://runpod.io))
- Docker installed locally (for building)
- Docker Hub account or private registry

### Optional
- RunPod CLI for advanced deployment
- Custom domain for production

## Quick Start

### 1. Build and Push Docker Image

```bash
# Make script executable (first time only)
chmod +x scripts/deploy-runpod.sh

# Run deployment script
./scripts/deploy-runpod.sh
```

### 2. Deploy to RunPod

1. Go to [RunPod Dashboard](https://runpod.io/console/pods)
2. Click **"Deploy"** or **"New Pod"**
3. Select **"Deploy Custom Container"**
4. Configure:
   - **Container Image**: `your-registry/staticwaves-pod-studio:6.0.0`
   - **Container Port**: `80`
   - **Expose HTTP Port**: `Yes`
5. Click **"Deploy"**

### 3. Access Your Application

- Application URL: `https://your-pod-id-80.proxy.runpod.net`
- Health check: `https://your-pod-id-80.proxy.runpod.net/health`

---

## Detailed Deployment

### Step 1: Local Testing

Test the Docker build locally before deploying:

```bash
# Run local test
./scripts/test-local.sh

# Access at http://localhost:8080
# Health check at http://localhost:8080/health
```

**Expected Output:**
```
✅ Build successful
✅ Health check passed
✅ Main page accessible
🌐 Application running at: http://localhost:8080
```

### Step 2: Docker Registry Setup

#### Option A: Docker Hub (Public/Private)

```bash
# Login to Docker Hub
docker login

# Build and tag
docker build -t your-username/staticwaves-pod-studio:6.0.0 .

# Push to Docker Hub
docker push your-username/staticwaves-pod-studio:6.0.0
docker push your-username/staticwaves-pod-studio:latest
```

#### Option B: GitHub Container Registry

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Build and tag
docker build -t ghcr.io/your-username/staticwaves-pod-studio:6.0.0 .

# Push to GHCR
docker push ghcr.io/your-username/staticwaves-pod-studio:6.0.0
```

#### Option C: Private Registry

```bash
# Login to your registry
docker login your-registry.com

# Build and tag
docker build -t your-registry.com/staticwaves-pod-studio:6.0.0 .

# Push
docker push your-registry.com/staticwaves-pod-studio:6.0.0
```

### Step 3: RunPod Configuration

#### Basic Configuration

```json
{
  "image": "your-registry/staticwaves-pod-studio:6.0.0",
  "ports": [
    {
      "containerPort": 80,
      "expose": true
    }
  ]
}
```

#### Advanced Configuration

```json
{
  "image": "your-registry/staticwaves-pod-studio:6.0.0",
  "ports": [
    {
      "containerPort": 80,
      "protocol": "http",
      "expose": true
    }
  ],
  "env": [
    {
      "name": "NODE_ENV",
      "value": "production"
    }
  ],
  "resources": {
    "cpu": "2000m",
    "memory": "1Gi",
    "gpu": 0
  },
  "volumeMounts": [
    {
      "name": "pod-data",
      "mountPath": "/data"
    }
  ]
}
```

### Step 4: Deploy via RunPod Web UI

1. **Navigate to Pods**
   - Go to: https://runpod.io/console/pods
   - Click **"Deploy"**

2. **Select Template**
   - Choose **"Deploy Custom Container"**

3. **Configure Container**
   ```
   Container Image: your-registry/staticwaves-pod-studio:6.0.0
   Container Disk: 1 GB (minimum)
   Volume Disk: Not required (optional)
   ```

4. **Port Configuration**
   ```
   Container Port: 80
   Expose HTTP Ports: ✓ Enabled
   ```

5. **Resource Allocation**
   ```
   CPU: 2 vCPU (recommended)
   RAM: 1 GB (minimum)
   GPU: Not required
   ```

6. **Deploy**
   - Click **"Deploy On-Demand"** or **"Deploy Spot"**
   - Wait for pod to start (~30-60 seconds)

### Step 5: Verify Deployment

```bash
# Get your pod URL from RunPod dashboard
POD_URL="https://your-pod-id-80.proxy.runpod.net"

# Test health endpoint
curl ${POD_URL}/health

# Expected output: "healthy"

# Test application
curl -I ${POD_URL}/

# Expected: HTTP 200 OK
```

---

## Configuration

### Environment Variables

Currently, POD Studio doesn't require environment variables for the simulation. For real API integration:

```bash
# Add to RunPod environment configuration
VITE_PRINTIFY_API_KEY=your_api_key
VITE_PRINTIFY_SHOP_ID=your_shop_id
```

### Custom Domain

1. **Add Domain in RunPod**
   - Go to Pod settings
   - Click **"Add Custom Domain"**
   - Enter your domain (e.g., `pod.yourdomain.com`)

2. **Configure DNS**
   ```
   Type: CNAME
   Name: pod
   Value: your-pod-id-80.proxy.runpod.net
   TTL: 300
   ```

3. **Enable SSL**
   - RunPod provides automatic SSL for custom domains
   - Wait 5-10 minutes for SSL certificate

### Resource Recommendations

| Workload | CPU | RAM | Storage |
|----------|-----|-----|---------|
| **Development** | 1 vCPU | 512 MB | 1 GB |
| **Production (Light)** | 2 vCPU | 1 GB | 2 GB |
| **Production (Heavy)** | 4 vCPU | 2 GB | 5 GB |

---

## Scaling

### Manual Scaling

1. Go to Pod details
2. Click **"Scale"**
3. Select number of replicas
4. Click **"Apply"**

### Auto-Scaling (Enterprise)

Create `runpod-autoscale.json`:

```json
{
  "scaling": {
    "min": 1,
    "max": 10,
    "targetCPU": 80,
    "targetMemory": 80
  }
}
```

### Load Balancing

RunPod automatically load balances between replicas when scaled.

---

## Monitoring

### Health Checks

POD Studio includes a health check endpoint:

```bash
# Check pod health
curl https://your-pod-url/health

# Response: "healthy"
```

### Logs

**Via RunPod Dashboard:**
1. Go to Pod details
2. Click **"Logs"** tab
3. View real-time logs

**Via RunPod CLI:**
```bash
runpod logs <pod-id>
```

### Metrics

Monitor in RunPod dashboard:
- CPU usage
- Memory usage
- Network traffic
- Request count
- Response times

---

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
runpod logs <pod-id>
```

**Common issues:**
- Image not found → Verify registry access
- Port conflict → Ensure port 80 is exposed
- Resource limits → Increase CPU/RAM

### 502 Bad Gateway

**Causes:**
- Container not ready yet (wait 30-60s)
- Application crashed (check logs)
- Port misconfiguration (verify port 80)

**Solution:**
```bash
# Restart pod
runpod restart <pod-id>

# Or redeploy
runpod deploy --image your-image:latest
```

### Health Check Failing

**Test locally:**
```bash
./scripts/test-local.sh
```

**Check nginx:**
```bash
# Access pod shell
runpod exec <pod-id> /bin/sh

# Test nginx
wget -qO- localhost/health
```

### Slow Performance

**Optimize:**
1. Increase CPU/RAM allocation
2. Use faster storage (SSD)
3. Enable caching in nginx
4. Use CDN for static assets

### Image Pull Errors

**Private registry:**
```bash
# Add registry credentials in RunPod
# Settings → Registry Credentials
Username: your-username
Password: your-token
Registry: docker.io
```

---

## Cost Optimization

### On-Demand vs Spot Instances

| Type | Price | Availability | Use Case |
|------|-------|--------------|----------|
| **On-Demand** | Standard | 99.9% | Production |
| **Spot** | ~70% cheaper | Variable | Development/Testing |

### Recommendations

1. **Development**: Use Spot instances
2. **Production**: Use On-Demand with auto-scaling
3. **Hybrid**: On-Demand base + Spot for overflow

### Cost Calculation

```
Estimated monthly cost (On-Demand):
- 2 vCPU + 1GB RAM = ~$10-15/month
- 4 vCPU + 2GB RAM = ~$20-30/month

Estimated monthly cost (Spot):
- 2 vCPU + 1GB RAM = ~$3-5/month
- 4 vCPU + 2GB RAM = ~$6-10/month
```

---

## Advanced Topics

### Multi-Region Deployment

Deploy to multiple regions for redundancy:

```bash
# Deploy to US-East
runpod deploy --region us-east --image your-image:latest

# Deploy to EU-West
runpod deploy --region eu-west --image your-image:latest
```

### Custom SSL Certificate

1. Upload certificate in RunPod settings
2. Attach to custom domain
3. Force HTTPS redirect

### Continuous Deployment

**GitHub Actions Integration:**

```yaml
# .github/workflows/deploy-runpod.yml
name: Deploy to RunPod

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build and push
        run: |
          docker build -t ${{ secrets.REGISTRY }}/pod-studio:latest .
          docker push ${{ secrets.REGISTRY }}/pod-studio:latest

      - name: Deploy to RunPod
        run: |
          runpod deploy --image ${{ secrets.REGISTRY }}/pod-studio:latest
```

---

## Migration from Other Platforms

### From Netlify/Vercel

1. Build Docker image with this guide
2. Push to registry
3. Deploy to RunPod
4. Update DNS to point to RunPod URL

### From Heroku

1. Use existing Dockerfile or create new one
2. Build and push to registry
3. Deploy to RunPod with same environment variables

---

## Security Best Practices

1. **Use Private Registry** for production images
2. **Enable HTTPS** with custom domain
3. **Rotate API Keys** regularly
4. **Monitor Access Logs** for suspicious activity
5. **Update Base Image** regularly for security patches

---

## Support & Resources

- **RunPod Documentation**: https://docs.runpod.io
- **RunPod Discord**: https://discord.gg/runpod
- **POD Studio Issues**: https://github.com/ssiens-oss/ssiens-oss-static_pod/issues
- **Email Support**: support@staticwaves.io

---

## Quick Reference

### Common Commands

```bash
# Local testing
./scripts/test-local.sh

# Build image
docker build -t pod-studio:latest .

# Run locally
docker run -p 8080:80 pod-studio:latest

# Push to registry
docker push your-registry/pod-studio:latest

# Check health
curl https://your-pod-url/health
```

### Important URLs

- RunPod Dashboard: https://runpod.io/console/pods
- Your App: https://your-pod-id-80.proxy.runpod.net
- Health Check: https://your-pod-id-80.proxy.runpod.net/health

---

**Deployment Checklist:**

- [ ] Docker image built and tested locally
- [ ] Image pushed to registry
- [ ] RunPod account set up
- [ ] Pod deployed with correct configuration
- [ ] Health check passing
- [ ] Application accessible
- [ ] Custom domain configured (optional)
- [ ] SSL enabled (optional)
- [ ] Monitoring set up
- [ ] Auto-scaling configured (optional)

**Your POD Studio is ready for RunPod deployment!** 🚀

# 🚀 RunPod Unified Deployment Guide

**Deploy POD + Forge services on a single RunPod GPU instance**

---

## 📋 Overview

This deployment runs **two complete platforms** on one RunPod instance:

1. **StaticWaves POD** - Print-on-demand merch platform
2. **StaticWaves Forge** - AI 3D asset generation platform

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   RunPod GPU Instance                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Nginx Reverse Proxy (:80)                      │   │
│  │  • / → POD Web UI                              │   │
│  │  • /forge/ → Forge Web UI                      │   │
│  │  • /api/pod/ → POD API                         │   │
│  │  • /api/forge/ → Forge API                     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────┐  ┌─────────────────┐                 │
│  │ POD Service  │  │ Forge Service   │                 │
│  ├──────────────┤  ├─────────────────┤                 │
│  │ Web  :3000   │  │ API    :8000    │                 │
│  │ API  :8001   │  │ Web    :3001    │                 │
│  │              │  │ Worker (GPU)    │                 │
│  └──────────────┘  └─────────────────┘                 │
│                                                          │
│  ┌───────────────────────────────────┐                  │
│  │ Redis :6379 (Job Queue)           │                  │
│  └───────────────────────────────────┘                  │
│                                                          │
│  ┌───────────────────────────────────┐                  │
│  │ Shared Volume (/app/assets)       │                  │
│  │ Forge generates → POD uses         │                  │
│  └───────────────────────────────────┘                  │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 Prerequisites

### Required
- RunPod account
- GPU instance (RTX 4090 or A5000 recommended)
- AWS S3 or Cloudflare R2 account
- Environment variables configured

### Recommended Specs
- **GPU**: RTX 4090 (24GB VRAM)
- **CPU**: 8+ cores
- **RAM**: 32GB+
- **Storage**: 100GB+

---

## 🔧 Setup Steps

### 1. Clone Repository on RunPod

```bash
# SSH into your RunPod instance
ssh root@YOUR_RUNPOD_URL

# Clone the repository
cd /workspace
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod
cd ssiens-oss-static_pod
```

### 2. Configure Environment

```bash
cd staticwaves-forge/infra/runpod

# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Required Variables:**
```bash
# Storage
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=staticwaves-assets

# POD Service
STRIPE_KEY=sk_live_...
PRINTFUL_API_KEY=your_key

# Database (if using)
DATABASE_URL=postgresql://...
```

### 3. Build and Start Services

```bash
# Make startup script executable
chmod +x start_unified.sh

# Start all services
./start_unified.sh
```

This will:
- ✅ Build all Docker images
- ✅ Start POD service (web + API)
- ✅ Start Forge service (API + web + worker)
- ✅ Start Redis queue
- ✅ Start Nginx proxy
- ✅ Run health checks

---

## 🌐 Accessing Services

### Public URLs

Once deployed, your services are available at:

```
Base URL: https://YOUR_RUNPOD_ID-80.proxy.runpod.net/
```

#### POD Service
- **Web UI**: `https://YOUR_RUNPOD_ID-80.proxy.runpod.net/`
- **API**: `https://YOUR_RUNPOD_ID-80.proxy.runpod.net/api/pod/`

#### Forge Service
- **Web UI**: `https://YOUR_RUNPOD_ID-80.proxy.runpod.net/forge/`
- **API**: `https://YOUR_RUNPOD_ID-80.proxy.runpod.net/api/forge/`
- **API Docs**: `https://YOUR_RUNPOD_ID-80.proxy.runpod.net/forge/docs`

### Internal Services

Within the Docker network:
- POD Web: `http://pod-service:3000`
- POD API: `http://pod-service:8001`
- Forge API: `http://forge-api:8000`
- Forge Web: `http://forge-web:3000`
- Redis: `redis://redis:6379`

---

## 🔗 Service Integration

### POD ↔ Forge Integration

The services can communicate via shared volume and HTTP:

#### Forge → POD (Asset to Merch)

```python
# In Forge: Generate 3D asset
job_id = forge_api.generate_asset(prompt="dragon figurine")

# Get asset path
asset_path = f"/output/{job_id}/asset.glb"

# In POD: Use asset for merch
pod_api.create_product(
    name="Dragon Figurine",
    model_path=asset_path,  # Shared volume
    render_views=["front", "side"]
)
```

#### POD → Forge (Request Custom Asset)

```python
# In POD: Customer requests custom design
order_id = "ORD-12345"

# Call Forge API
response = requests.post(
    "http://forge-api:8000/api/generate/",
    json={
        "prompt": customer_design_prompt,
        "asset_type": "prop",
        "poly_budget": 10000
    }
)

# Track job
job_id = response.json()["job_id"]
```

---

## 📊 Monitoring

### View Logs

```bash
cd /workspace/staticwaves-forge/infra/runpod

# All services
docker-compose -f docker-compose.unified.yml logs -f

# Specific service
docker-compose -f docker-compose.unified.yml logs -f forge-worker
docker-compose -f docker-compose.unified.yml logs -f pod-service
```

### Check Status

```bash
# Service status
docker-compose -f docker-compose.unified.yml ps

# Health checks
curl http://localhost/health
curl http://localhost/api/pod/health
curl http://localhost/api/forge/health
```

### GPU Usage

```bash
# Real-time GPU monitoring
watch -n 1 nvidia-smi

# Check which container is using GPU
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## 🔄 Management Commands

### Start/Stop Services

```bash
cd /workspace/staticwaves-forge/infra/runpod

# Start all
docker-compose -f docker-compose.unified.yml up -d

# Stop all
docker-compose -f docker-compose.unified.yml down

# Restart specific service
docker-compose -f docker-compose.unified.yml restart forge-worker
```

### Update Services

```bash
# Pull latest code
git pull origin main

# Rebuild specific service
docker-compose -f docker-compose.unified.yml build forge-api
docker-compose -f docker-compose.unified.yml up -d forge-api

# Rebuild all
docker-compose -f docker-compose.unified.yml build
docker-compose -f docker-compose.unified.yml up -d
```

### Clear Data

```bash
# Remove all containers and volumes
docker-compose -f docker-compose.unified.yml down -v

# Clean Docker system
docker system prune -af
```

---

## 💾 Resource Management

### Disk Space

Monitor disk usage:
```bash
# Check usage
df -h

# Clean Docker
docker system df
docker system prune -a

# Clean build cache
docker builder prune
```

### Memory

```bash
# Check memory
free -h

# Container memory usage
docker stats --no-stream
```

---

## 🔒 Security

### Environment Variables

**Never commit `.env` file!**

Store sensitive data:
- RunPod environment variables
- Or encrypted secrets manager

### Network

Default configuration:
- All services internal except Nginx
- Nginx exposes only port 80
- HTTPS via RunPod proxy

For custom domain:
1. Add SSL certificates to `/infra/runpod/ssl/`
2. Update `nginx.conf` with SSL config

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose -f docker-compose.unified.yml logs

# Check ports
netstat -tulpn | grep LISTEN

# Restart services
docker-compose -f docker-compose.unified.yml restart
```

### GPU Not Detected

```bash
# Verify GPU
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Restart forge-worker
docker-compose -f docker-compose.unified.yml restart forge-worker
```

### Out of Memory

```bash
# Check memory
docker stats

# Reduce concurrent workers
# Edit docker-compose.unified.yml
# Reduce WORKER_CONCURRENCY

# Restart with new config
docker-compose -f docker-compose.unified.yml up -d
```

### Network Issues

```bash
# Check network
docker network ls
docker network inspect runpod_staticwaves

# Recreate network
docker-compose -f docker-compose.unified.yml down
docker network prune
docker-compose -f docker-compose.unified.yml up -d
```

---

## 📈 Performance Tuning

### Optimize for Cost

**Single GPU, Multiple Services:**
- Forge worker uses GPU only during generation
- POD service runs CPU tasks
- Resource sharing = 50% cost savings

**Auto-scaling:**
```yaml
# In docker-compose.unified.yml
forge-worker:
  deploy:
    replicas: 1  # Start with 1
    # Scale up during high demand:
    # docker-compose up -d --scale forge-worker=3
```

### Optimize for Speed

**Redis Caching:**
- Job queue in memory
- Fast job distribution

**Shared Volume:**
- No network transfer between services
- Direct file access

**GPU Optimization:**
- Blender GPU rendering
- Batch processing

---

## 💰 Cost Estimation

### RunPod Pricing (RTX 4090)

| Component | Cost/hr | Monthly (24/7) |
|-----------|---------|----------------|
| GPU Instance | $0.34 | ~$245 |

**Running Both Services:**
- Single instance = $245/mo
- Separate instances = $490/mo
- **Savings: $245/mo (50%)**

### Usage-Based Costs

- Storage (S3/R2): ~$0.02/GB
- Bandwidth: ~$0.08/GB
- API calls: Varies by volume

---

## 🔄 CI/CD Integration

### Auto-Deploy on Git Push

```bash
# Add webhook to RunPod
# POST https://YOUR_RUNPOD_URL/webhook/deploy

# Webhook handler script
cat > /workspace/deploy_webhook.sh << 'EOF'
#!/bin/bash
cd /workspace/ssiens-oss-static_pod
git pull
cd staticwaves-forge/infra/runpod
docker-compose -f docker-compose.unified.yml build
docker-compose -f docker-compose.unified.yml up -d
EOF

chmod +x /workspace/deploy_webhook.sh
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Nginx responding on port 80
- [ ] POD web UI accessible at `/`
- [ ] Forge web UI accessible at `/forge/`
- [ ] POD API healthy at `/api/pod/health`
- [ ] Forge API healthy at `/api/forge/health`
- [ ] Redis accepting connections
- [ ] GPU visible to forge-worker
- [ ] Logs showing no errors
- [ ] Test asset generation works
- [ ] Test POD product creation works
- [ ] Services can communicate
- [ ] Shared volume accessible

---

## 📞 Support

**Issues:**
- GitHub: https://github.com/ssiens-oss/ssiens-oss-static_pod/issues
- Logs: Check `docker-compose logs`

**Resources:**
- RunPod Docs: https://docs.runpod.io
- Docker Docs: https://docs.docker.com

---

**Your unified StaticWaves platform is ready for production deployment!** 🚀

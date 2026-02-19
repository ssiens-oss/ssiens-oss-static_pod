# StaticWaves Forge - Complete Deployment Guide

## Table of Contents

1. [Quick Start (Local Development)](#quick-start-local-development)
2. [Production Deployment](#production-deployment)
3. [RunPod Deployment](#runpod-deployment)
4. [Architecture Overview](#architecture-overview)
5. [Configuration](#configuration)
6. [Scaling](#scaling)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start (Local Development)

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Redis** (or use Docker)
- **Blender 3.6+** (for workers)

### 1. Start Redis

```bash
# Option A: Using Docker
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Option B: System Redis
redis-server
```

### 2. Start API Server

```bash
cd apps/api

# Install dependencies
pip install -r requirements.txt
pip install redis

# Start API
export USE_REDIS=true
export REDIS_URL=redis://localhost:6379
python main.py

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 3. Start Worker

```bash
cd apps/worker

# Install dependencies
pip install -r requirements.txt

# Install Blender (if not already installed)
# Download from https://www.blender.org/download/

# Start worker
export REDIS_URL=redis://localhost:6379
export BLENDER_PATH=/usr/local/bin/blender  # Adjust path
export OUTPUT_DIR=./generated_assets
python worker.py
```

### 4. Start Web GUI

```bash
cd apps/web

# Install dependencies
npm install

# Start dev server
export NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev

# Web GUI will be available at http://localhost:3000
```

### 5. Test Generation

```bash
# Via API
curl -X POST http://localhost:8000/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a low-poly medieval sword",
    "asset_type": "weapon",
    "style": "low-poly",
    "export_formats": ["glb", "fbx"],
    "poly_budget": 5000
  }'

# Response: {"job_id": "xxx-xxx-xxx", "status": "queued"}

# Check status
curl http://localhost:8000/api/jobs/xxx-xxx-xxx

# Via Web GUI
# Open http://localhost:3000/generate and create an asset
```

---

## Production Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale worker=3

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop all services
docker-compose -f docker-compose.prod.yml down
```

### Production Docker Compose Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  api:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - USE_REDIS=true
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped

  worker:
    build:
      context: ./apps/worker
      dockerfile: Dockerfile
    environment:
      - REDIS_URL=redis://redis:6379
      - BLENDER_PATH=/usr/local/blender/blender
      - OUTPUT_DIR=/workspace/generated_assets
      - WORKER_TYPE=docker
    volumes:
      - generated_assets:/workspace/generated_assets
    depends_on:
      - redis
    restart: unless-stopped
    deploy:
      replicas: 2  # Run 2 workers

  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
      - NODE_ENV=production
    depends_on:
      - api
    restart: unless-stopped

volumes:
  redis_data:
  generated_assets:
```

---

## RunPod Deployment

### Option 1: One-Click Boot (Recommended)

Use the existing unified boot system:

```bash
# SSH into RunPod pod
cd /workspace

# Clone repository
git clone -b claude/ai-3d-asset-engine-Q6XOw \
    https://github.com/ssiens-oss/ssiens-oss-static_pod.git \
    staticwaves-forge

cd staticwaves-forge/staticwaves-forge

# Start all services
./start-unified.sh start

# Services will be available at:
# - Web GUI: https://YOUR-POD-ID-3000.proxy.runpod.net
# - API: https://YOUR-POD-ID-8000.proxy.runpod.net
```

### Option 2: Worker-Only RunPod Pod

Deploy a dedicated worker pod for processing:

```bash
# Create RunPod template with:
# - Base Image: nvidia/cuda:11.8.0-devel-ubuntu22.04
# - Exposed Ports: None (worker only)
# - Volume: /workspace

# Start script:
#!/bin/bash
apt-get update && apt-get install -y git python3 python3-pip wget

# Install Blender
wget https://download.blender.org/release/Blender3.6/blender-3.6.5-linux-x64.tar.xz
tar -xf blender-3.6.5-linux-x64.tar.xz
mv blender-3.6.5-linux-x64 /usr/local/blender

# Clone repository
cd /workspace
git clone -b claude/ai-3d-asset-engine-Q6XOw \
    https://github.com/ssiens-oss/ssiens-oss-static_pod.git

cd ssiens-oss-static_pod/staticwaves-forge/apps/worker

# Install dependencies
pip3 install -r requirements.txt

# Start worker (connect to your Redis instance)
export REDIS_URL=redis://YOUR-REDIS-HOST:6379
export BLENDER_PATH=/usr/local/blender/blender
export OUTPUT_DIR=/workspace/generated_assets
python3 worker.py
```

---

## Architecture Overview

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Web GUI    │────────▶│  API Server  │────────▶│    Redis     │
│  (Next.js)   │         │  (FastAPI)   │         │    Queue     │
└──────────────┘         └──────────────┘         └──────────────┘
                                                          │
                                                          │
                         ┌────────────────────────────────┤
                         │                                │
                         ▼                                ▼
                  ┌──────────────┐              ┌──────────────┐
                  │   Worker 1   │              │   Worker N   │
                  │  (Blender)   │      ...     │  (Blender)   │
                  └──────────────┘              └──────────────┘
                         │                                │
                         └────────────┬───────────────────┘
                                      ▼
                              ┌──────────────┐
                              │   Storage    │
                              │  (S3/Local)  │
                              └──────────────┘
```

### Components

1. **Web GUI** - User interface for creating assets
2. **API Server** - REST API + WebSocket for real-time updates
3. **Redis Queue** - Distributed job queue with priority support
4. **Workers** - Blender instances that generate 3D assets
5. **Storage** - File storage for generated assets (S3 or local)

---

## Configuration

### Environment Variables

#### API Server

```bash
# Redis
USE_REDIS=true                    # Enable Redis queue
REDIS_URL=redis://localhost:6379  # Redis connection

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=*  # In production: specify allowed origins
```

#### Worker

```bash
# Worker Identity
WORKER_ID=worker-gpu-1            # Unique worker ID (auto-generated if not set)
WORKER_TYPE=runpod                # runpod, local, docker

# Redis
REDIS_URL=redis://localhost:6379  # Redis connection
QUEUE_NAME=generation:normal      # Queue to poll (normal, high, low)

# Blender
BLENDER_PATH=/usr/local/bin/blender  # Path to Blender executable

# Output
OUTPUT_DIR=/workspace/generated_assets  # Where to save generated files
STORAGE_TYPE=local                      # local or s3

# S3 (if using cloud storage)
S3_BUCKET=staticwaves-assets
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx

# Performance
MAX_CONCURRENT_JOBS=1       # Jobs per worker (keep at 1 for GPU)
JOB_TIMEOUT=600             # Timeout in seconds (10 minutes)
POLL_INTERVAL=5             # Queue polling interval
```

#### Web GUI

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # API endpoint
NODE_ENV=production                         # production or development
```

---

## Scaling

### Horizontal Scaling

Add more workers to process jobs faster:

```bash
# Docker Compose
docker-compose up -d --scale worker=5  # Run 5 workers

# Manually
# Start multiple worker instances with different WORKER_IDs
WORKER_ID=worker-1 python worker.py &
WORKER_ID=worker-2 python worker.py &
WORKER_ID=worker-3 python worker.py &
```

### Auto-Scaling Strategy

```python
# Monitor queue depth
queue_depth = redis_client.llen('generation:normal')

if queue_depth > 10:
    # Spawn additional RunPod workers
    spawn_runpod_worker()

elif queue_depth == 0 and worker_idle_time > 300:
    # Terminate idle workers
    terminate_worker()
```

### Priority Queues

Jobs are processed from three priority queues:

1. **High Priority** (`generation:high`) - Processed first
2. **Normal Priority** (`generation:normal`) - Standard queue
3. **Low Priority** (`generation:low`) - Batch jobs

```bash
# Create job with priority
curl -X POST http://localhost:8000/api/generate/?priority=high \
  -d '{"prompt": "urgent asset"}'
```

---

## Monitoring

### Queue Stats

```bash
# Check queue depth
curl http://localhost:8000/api/generate/queue/stats

# Response:
# {
#   "high_priority": 0,
#   "normal_priority": 5,
#   "low_priority": 12,
#   "total": 17
# }
```

### Worker Status

```bash
# List active workers
curl http://localhost:8000/api/jobs/workers/list

# Response:
# {
#   "workers": [
#     {
#       "worker_id": "worker-gpu-1",
#       "status": "processing",
#       "current_job": "xxx-xxx-xxx",
#       "jobs_completed": 45,
#       "jobs_failed": 2
#     }
#   ]
# }
```

### Job Stats

```bash
# Get overall stats
curl http://localhost:8000/api/jobs/stats/overview

# Response:
# {
#   "total_jobs": 150,
#   "queued": 5,
#   "processing": 2,
#   "completed": 140,
#   "failed": 3
# }
```

### Real-Time Progress

```javascript
// WebSocket connection for live updates
const ws = new WebSocket('ws://localhost:8000/api/jobs/xxx-xxx-xxx/stream');

ws.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  console.log(`Progress: ${progress.progress * 100}%`);
  console.log(`Status: ${progress.status}`);
};
```

---

## Troubleshooting

### Worker Not Processing Jobs

```bash
# Check if worker is connected to Redis
redis-cli ping

# Check queue depth
redis-cli llen generation:normal

# Check worker logs
# Look for connection errors or Blender issues

# Manually test Blender
blender --version
blender --background --python test_script.py
```

### Jobs Stuck in Queue

```bash
# Check if any workers are running
curl http://localhost:8000/api/jobs/workers/list

# Clear stuck jobs (caution!)
curl -X DELETE http://localhost:8000/api/generate/queue/clear?priority=normal

# Restart workers
pkill -f worker.py
python worker.py
```

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli ping

# Check Redis URL
echo $REDIS_URL

# Check if Redis is running
ps aux | grep redis

# Restart Redis
redis-server
```

### Blender Script Errors

```bash
# Test Blender script directly
blender --background --python apps/worker/blender_scripts/asset_generator.py -- /path/to/job_config.json

# Check Blender Python version
blender --background --python-expr "import sys; print(sys.version)"

# Install dependencies in Blender Python
blender --background --python-expr "import pip; pip.main(['install', 'numpy'])"
```

### Out of Memory

```bash
# Reduce poly budget
"poly_budget": 5000  # Instead of 50000

# Disable LOD generation
"generate_lods": false

# Use lower quality AI model
# Edit worker to use Shap-E instead of Point-E
```

---

## Performance Tips

### 1. Use GPU Workers

RunPod GPU instances dramatically speed up AI generation:
- **CPU**: 2-5 minutes per asset
- **GPU (T4)**: 30-60 seconds per asset
- **GPU (A100)**: 15-30 seconds per asset

### 2. Cache AI Models

Workers download models on first run. Keep them cached:

```bash
export MODEL_CACHE_DIR=/workspace/models
```

### 3. Optimize Poly Budget

Lower poly counts = faster generation:

- **Low-poly games**: 2,000-5,000 polys
- **Mobile games**: 5,000-10,000 polys
- **PC/Console**: 10,000-30,000 polys

### 4. Batch Processing

Use low-priority queue for large batches:

```bash
curl -X POST http://localhost:8000/api/generate/batch?priority=low \
  -d '[{"prompt": "asset1"}, {"prompt": "asset2"}, ...]'
```

### 5. Worker Pool

Maintain a pool of warm workers during peak hours:

```bash
# Keep 2 workers always running
for i in {1..2}; do
  WORKER_ID=worker-$i python worker.py &
done
```

---

## Next Steps

1. ✅ Set up local development environment
2. ✅ Test asset generation pipeline
3. ⬜ Deploy to RunPod production
4. ⬜ Set up monitoring and alerts
5. ⬜ Configure auto-scaling
6. ⬜ Integrate real AI models (Shap-E, Point-E)
7. ⬜ Add cloud storage (S3/R2)

---

**Questions or Issues?**

- GitHub: https://github.com/ssiens-oss/ssiens-oss-static_pod
- Documentation: See CODE_REFERENCE.md
- Architecture: See WORKER_ARCHITECTURE.md

**Version**: 1.0.0
**Last Updated**: 2026-01-03

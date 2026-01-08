# RunPod Deployment Guide

## Quick Deploy (Recommended)

### Option 1: Using Existing Docker Image

If someone has already built and pushed the image:

```bash
# On RunPod, create a new pod with:
# - Template: Custom
# - Container Image: your-username/pod-engine:latest
# - GPU: RTX A4000 or better
# - Container Disk: 50 GB
# - Volume: 50 GB
# - Ports: 80, 8188, 8000
```

### Option 2: Manual Setup on RunPod PyTorch Template

1. **Create Pod:**
   - Template: `runpod/pytorch:2.1.0-py3.10-cuda12.1.1-devel-ubuntu22.04`
   - GPU: RTX A4000+
   - Container Disk: 50 GB
   - Volume: 50 GB

2. **SSH into pod and run:**

```bash
cd /workspace
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
cd ssiens-oss-static_pod
git checkout claude/setup-local-pod-engine-pzLRK

# Install system dependencies
apt-get update
apt-get install -y redis-server nodejs npm lsof

# Run setup
./scripts/setup-pod-engine.sh

# Start Redis manually (workaround for config issue)
redis-server --daemonize yes

# Start other services
source .venv/bin/activate
cd ComfyUI && nohup python main.py --listen 0.0.0.0 --port 8188 > ../logs/comfyui.log 2>&1 & cd ..
export REDIS_HOST=localhost REDIS_PORT=6379 OUTPUT_DIR=./data/output
nohup python -m uvicorn music-engine.api.main:app --host 0.0.0.0 --port 8000 > logs/music-api.log 2>&1 &
nohup python music-engine/worker/worker.py > logs/music-worker.log 2>&1 &
```

3. **Verify services:**

```bash
curl http://localhost:8000/health
curl http://localhost:8188
```

## Build Your Own Docker Image

```bash
# On your local machine or build server
cd ssiens-oss-static_pod
git pull

# Build the image
docker build -f Dockerfile.runpod -t your-dockerhub-username/pod-engine:latest .

# Push to Docker Hub
docker login
docker push your-dockerhub-username/pod-engine:latest
```

## Services & Ports

| Service | Port | Description |
|---------|------|-------------|
| ComfyUI | 8188 | AI Image Generation Web UI |
| Music API | 8000 | Music Generation API |
| API Docs | 8000/docs | Interactive API Documentation |
| Web UI | 5173 | POD Pipeline Interface (optional) |
| Redis | 6379 | Internal queue system |

## Quick Start Commands

```bash
# Health check all services
curl http://localhost:8000/health
curl http://localhost:8188

# Generate music
curl -X POST http://localhost:8000/generate/auto

# View available genres
curl http://localhost:8000/genres

# Generate with specific genre
curl -X POST "http://localhost:8000/generate/auto?genre=edm&duration=120"

# Check logs
tail -f logs/music-worker.log
tail -f logs/comfyui.log
tail -f logs/music-api.log
```

## Persistent Storage

All data is stored in:
- `/workspace/data/output` - Generated music files
- `/workspace/data/designs` - POD designs
- `/workspace/ComfyUI/models` - AI models (SDXL, etc.)
- `/workspace/logs` - Service logs

## Environment Variables (Optional)

Create `.env` file:

```bash
ANTHROPIC_API_KEY=your-api-key-here
PRINTIFY_API_KEY=your-printify-key
SHOPIFY_ACCESS_TOKEN=your-shopify-token
```

## Troubleshooting

### Redis won't start with logfile
```bash
# Start without logfile
redis-server --daemonize yes
```

### ComfyUI models missing
```bash
cd ComfyUI/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
```

### Music Worker crashes
```bash
# Check logs
tail -100 logs/music-worker.log

# Ensure GPU is available
nvidia-smi

# Restart worker
pkill -f music-engine/worker
source .venv/bin/activate
export MUSICGEN_MODEL=facebook/musicgen-medium
python music-engine/worker/worker.py > logs/music-worker.log 2>&1 &
```

## Cost Estimate

**RunPod RTX A4000:**
- ~$0.40/hour
- ~$10/day for 24/7 operation
- Can pause when not in use

**Usage:**
- Image generation: ~8-10 seconds per image
- Music generation: ~25-30 seconds per 30s clip

## Next Steps

1. Access ComfyUI at `http://your-pod-ip:8188`
2. Generate music via API: `curl -X POST http://localhost:8000/generate/auto`
3. View API docs: `http://your-pod-ip:8000/docs`
4. (Optional) Start web UI: `npm run dev`

## Support

- GitHub Issues: https://github.com/ssiens-oss/ssiens-oss-static_pod/issues
- API Docs: http://localhost:8000/docs
- ComfyUI Docs: https://github.com/comfyanonymous/ComfyUI

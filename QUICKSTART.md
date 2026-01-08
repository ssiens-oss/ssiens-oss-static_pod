# Quick Start Guide

## Important: Run from Project Directory

All commands must be run from the project directory:

```bash
cd /home/user/ssiens-oss-static_pod
```

Or if you cloned to a different location:

```bash
cd /path/to/ssiens-oss-static_pod
```

## Step-by-Step Setup

### 1. Navigate to Project Directory

```bash
cd /home/user/ssiens-oss-static_pod
# Verify you're in the right place
ls scripts/setup-pod-engine.sh
```

### 2. Run Complete Setup

```bash
./scripts/setup-pod-engine.sh
```

This will:
- Install all Python dependencies
- Clone ComfyUI
- Download SDXL models (6.94 GB + 335 MB)
- Install npm packages
- Setup environment

**Note**: This will take 15-30 minutes depending on your internet speed.

### 3. Start All Services

```bash
./scripts/start-pod-engine.sh
```

This starts:
- ComfyUI (port 8188)
- Music API (port 8000)
- Music Worker (GPU)
- Redis (port 6379)

### 4. Start Web UI (Optional)

In a new terminal, from the project directory:

```bash
cd /home/user/ssiens-oss-static_pod
npm run dev          # POD Pipeline UI (port 5173)
```

Or for Music Studio:

```bash
npm run dev:music    # Music Studio UI (port 5174)
```

### 5. Test Music Generation

```bash
# Wait for services to be ready (~30 seconds)
sleep 30

# Generate music
curl http://localhost:8000/generate/auto
```

### 6. Access Services

- **ComfyUI**: http://localhost:8188
- **Music API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Web UI**: http://localhost:5173

### 7. Stop All Services

```bash
cd /home/user/ssiens-oss-static_pod
./scripts/stop-pod-engine.sh
```

## Troubleshooting

### "No such file or directory"

You're in the wrong directory. Run:

```bash
cd /home/user/ssiens-oss-static_pod
pwd  # Should show: /home/user/ssiens-oss-static_pod
```

### "Permission denied"

Make scripts executable:

```bash
chmod +x scripts/*.sh
```

### Check Service Status

```bash
# Check if services are running
ps aux | grep -E "comfyui|uvicorn|redis|music-engine"

# Check logs
tail -f logs/music-worker.log
tail -f logs/comfyui.log
tail -f logs/music-api.log
```

### Redis Not Found

Install Redis:

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y redis-server

# macOS
brew install redis
```

## One-Line Setup (After Installing Dependencies)

From project directory:

```bash
./scripts/setup-pod-engine.sh && ./scripts/start-pod-engine.sh
```

## For RunPod Deployment

```bash
cd /home/user/ssiens-oss-static_pod
export DOCKER_USERNAME=your-dockerhub-username
export RUNPOD_API_KEY=your-runpod-api-key
./scripts/deploy-runpod.sh
```

## Directory Structure Reference

```
ssiens-oss-static_pod/          ← YOU MUST BE HERE
├── scripts/
│   ├── setup-pod-engine.sh     ← Run these from project root
│   ├── start-pod-engine.sh
│   └── stop-pod-engine.sh
├── package.json                ← npm commands work here
├── POD_ENGINE.md
└── ...
```

## Common Commands Cheat Sheet

```bash
# Always start here
cd /home/user/ssiens-oss-static_pod

# Setup (first time only)
./scripts/setup-pod-engine.sh

# Start services
./scripts/start-pod-engine.sh

# Start web UI
npm run dev

# Generate music
curl http://localhost:8000/generate/auto

# Check status
curl http://localhost:8000/health

# View logs
tail -f logs/music-worker.log

# Stop everything
./scripts/stop-pod-engine.sh
```

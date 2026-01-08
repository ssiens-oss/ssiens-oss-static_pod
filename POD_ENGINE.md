# Pod Engine - Complete Setup Guide

## Overview

The **Pod Engine** is a complete, production-ready system that combines:

- **🎨 ComfyUI** - AI image generation with SDXL
- **🎵 Music Generation** - AI music creation with MusicGen + DDSP
- **🎤 MashDeck** - Advanced music production with vocals, battles, and live streaming
- **📦 POD Pipeline** - Print-on-Demand automation (Printify, Shopify, etc.)
- **☁️ RunPod Ready** - Deploy to GPU cloud with one command

## Features

### ComfyUI Integration
- SDXL 1.0 Base Model with VAE
- Automatic model downloads
- GPU-accelerated image generation
- Web UI on port 8188

### Music Engine
- **MusicGen** for base music generation
- **DDSP** for advanced synthesis
- **Redis** job queue system
- **FastAPI** backend with WebSocket support
- Automatic music generation with genre/mood presets
- Playlist generation
- Stem export (mix, bass, lead, pad, drums)

### MashDeck Features
- AI vocal generation with harmonies
- Live freestyle mode (chat-to-rap)
- AI rapper battles
- MIDI export
- Auto-release to streaming platforms

## Quick Start (Local Development)

### Prerequisites

```bash
# System Requirements
- Python 3.10+
- CUDA 12.1+ (for GPU acceleration)
- Redis
- Node.js 20+
- 16GB+ RAM
- 20GB+ disk space (for models)
```

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd ssiens-oss-static_pod

# 2. Run the complete setup (installs everything)
./scripts/setup-pod-engine.sh
```

This will:
- Install all Python dependencies
- Clone and setup ComfyUI
- Download SDXL models (6.94 GB + 335 MB)
- Install Node.js dependencies
- Pre-download MusicGen models
- Create necessary directories
- Setup .env file

### Start All Services

```bash
# Start ComfyUI, Music API, Music Worker, and Redis
./scripts/start-pod-engine.sh
```

Services will be available at:
- **ComfyUI**: http://localhost:8188
- **Music API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redis**: localhost:6379

### Start Web UI

```bash
# POD Pipeline UI
npm run dev

# Or Music Studio UI
npm run dev:music
```

### Stop All Services

```bash
./scripts/stop-pod-engine.sh
```

## RunPod Deployment

### Quick Deploy

```bash
# Set environment variables
export DOCKER_USERNAME=your-dockerhub-username
export RUNPOD_API_KEY=your-runpod-api-key

# Build and deploy
./scripts/deploy-runpod.sh
```

### What Gets Deployed

The Dockerfile.runpod creates a complete container with:

1. **Pre-installed Models**:
   - SDXL Base 1.0 (6.94 GB)
   - SDXL VAE (335 MB)
   - MusicGen Medium (auto-downloads on build)

2. **All Services**:
   - ComfyUI (port 8188)
   - Music API (port 8000)
   - Music Worker (GPU)
   - Redis (port 6379)
   - Nginx (port 80)

3. **Auto-start Script**:
   - All services start automatically
   - Health checks ensure everything is running
   - Logs available in /workspace/logs/

### RunPod Configuration

The deployment uses:
- **GPU**: NVIDIA RTX A4000 (or better)
- **Container Disk**: 50 GB
- **Persistent Volume**: 50 GB (for outputs/data)
- **Ports**: 80/http, 8188/http, 8000/http
- **Auto-scaling**: Supported

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Pod Engine                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ ComfyUI  │  │  Music   │  │  Redis   │             │
│  │  :8188   │  │  API     │  │  :6379   │             │
│  │          │  │  :8000   │  │          │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │             │             │                    │
│       │             │             │                    │
│  ┌────┴─────────────┴─────────────┴─────┐             │
│  │         Music Worker (GPU)            │             │
│  │    (MusicGen + DDSP + Mixer)          │             │
│  └───────────────────────────────────────┘             │
│                                                         │
│  ┌───────────────────────────────────────┐             │
│  │          Web UI (Nginx)               │             │
│  │            :80 / :5173                │             │
│  └───────────────────────────────────────┘             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## API Usage

### Music Generation

#### Automatic Generation (Zero Config)

```bash
# Generate a random song
curl http://localhost:8000/generate/auto

# Generate with specific genre
curl "http://localhost:8000/generate/auto?genre=edm&duration=120"

# Generate with lyrics
curl "http://localhost:8000/generate/auto?include_lyrics=true"
```

#### Smart Presets

```bash
# Available presets
curl http://localhost:8000/presets

# Generate from preset
curl -X POST http://localhost:8000/generate/preset/workout_energy
curl -X POST http://localhost:8000/generate/preset/deep_focus
curl -X POST http://localhost:8000/generate/preset/party_vibes
```

#### Generate Playlist

```bash
# Generate 5-song workout playlist
curl -X POST "http://localhost:8000/generate/playlist?mood=energetic&count=5"

# Chill study playlist
curl -X POST "http://localhost:8000/generate/playlist?mood=chill&count=10"
```

#### Check Status

```bash
# Get job status
curl http://localhost:8000/status/{job_id}

# Response:
{
  "job_id": "abc-123",
  "status": "completed",
  "progress": 100.0,
  "output_urls": {
    "mix": "/download/abc-123/mix",
    "bass": "/download/abc-123/bass",
    "lead": "/download/abc-123/lead",
    "pad": "/download/abc-123/pad",
    "drums": "/download/abc-123/drums"
  }
}
```

#### Download Generated Music

```bash
# Download full mix
wget http://localhost:8000/download/{job_id}/mix

# Download individual stems
wget http://localhost:8000/download/{job_id}/bass
wget http://localhost:8000/download/{job_id}/lead
wget http://localhost:8000/download/{job_id}/drums
```

### ComfyUI Integration

ComfyUI is accessible at http://localhost:8188 and can be used:

1. Via the web UI for manual workflow design
2. Via the API for automated image generation
3. Integrated with the POD pipeline for product design

## MashDeck CLI

MashDeck provides advanced music production features via CLI:

### Generate Full Song

```bash
python3 -m mashdeck.cli generate \
  --style edm \
  --bpm 128 \
  --key "Am" \
  --title "My Track" \
  --output ./output
```

### Live Freestyle Mode

```bash
# Chat-to-rap generation
python3 -m mashdeck.cli freestyle --bars 8
```

### AI Rapper Battle

```bash
# 3-round AI battle
python3 -m mashdeck.cli battle --rounds 3 --bars 4
```

### Auto-Release to Platforms

```bash
python3 -m mashdeck.cli release track.wav \
  --title "My Song" \
  --artist "AI Producer" \
  --platforms "spotify,youtube,tiktok"
```

## Directory Structure

```
.
├── scripts/
│   ├── setup-pod-engine.sh      # Complete installation
│   ├── start-pod-engine.sh      # Start all services
│   ├── stop-pod-engine.sh       # Stop all services
│   ├── setup-comfyui.sh         # ComfyUI-only setup
│   └── deploy-runpod.sh         # Deploy to RunPod
├── music-engine/
│   ├── api/                     # FastAPI backend
│   ├── worker/                  # GPU worker
│   └── shared/                  # Shared utilities
├── mashdeck/                    # Advanced music production
│   ├── song_engine/             # Song generation
│   ├── vocals/                  # Vocal synthesis
│   ├── live/                    # Live modes
│   └── release/                 # Platform publishing
├── ComfyUI/                     # ComfyUI installation
├── data/                        # Generated files
│   ├── output/                  # Music outputs
│   ├── designs/                 # POD designs
│   └── models/                  # Downloaded models
├── logs/                        # Service logs
├── pod-requirements.txt         # Python dependencies
├── Dockerfile.runpod            # RunPod container
└── POD_ENGINE.md               # This file
```

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
# ComfyUI
COMFYUI_API_URL=http://localhost:8188

# Claude AI
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Music Engine
REDIS_HOST=localhost
REDIS_PORT=6379
MUSICGEN_MODEL=facebook/musicgen-medium
OUTPUT_DIR=./data/output

# POD Pipeline (optional)
PRINTIFY_API_KEY=your-key
SHOPIFY_ACCESS_TOKEN=your-token
```

## Troubleshooting

### ComfyUI Won't Start

```bash
# Check logs
tail -f logs/comfyui.log

# Ensure models are downloaded
ls -lh ComfyUI/models/checkpoints/

# Manually start ComfyUI
cd ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188
```

### Music Worker Errors

```bash
# Check worker logs
tail -f logs/music-worker.log

# Verify Redis is running
redis-cli ping

# Check GPU availability
nvidia-smi

# Restart worker
pkill -f "music-engine/worker"
python3 music-engine/worker/worker.py
```

### Models Not Found

```bash
# Re-run setup to download models
./scripts/setup-pod-engine.sh

# Manually download SDXL
cd ComfyUI/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
```

### Out of Memory

```bash
# Use smaller MusicGen model
export MUSICGEN_MODEL=facebook/musicgen-small

# Or use CPU (slower)
export CUDA_VISIBLE_DEVICES=""
```

## Performance

### Local Development (NVIDIA RTX 3090)
- **Image Generation**: ~10s per image (SDXL)
- **Music Generation**: ~30s for 30s of audio
- **Concurrent Jobs**: 1-2 (GPU limited)

### RunPod (NVIDIA RTX A4000)
- **Image Generation**: ~8s per image
- **Music Generation**: ~25s for 30s of audio
- **Concurrent Jobs**: 2-3
- **Cost**: ~$0.40/hour

## Next Steps

1. **Generate your first song**:
   ```bash
   curl http://localhost:8000/generate/auto
   ```

2. **Create POD designs**:
   ```bash
   npm run dev
   # Open http://localhost:5173
   ```

3. **Deploy to RunPod**:
   ```bash
   ./scripts/deploy-runpod.sh
   ```

4. **Explore the API**:
   - Visit http://localhost:8000/docs
   - Try different genres, moods, and presets
   - Generate playlists and variations

## Support

- **Documentation**: See README.md, SETUP_GUIDE.md, MUSIC_GUIDE.md
- **Issues**: GitHub Issues
- **API Reference**: http://localhost:8000/docs

## License

See LICENSE file for details.

---

**Built with**: ComfyUI, MusicGen, DDSP, FastAPI, Redis, PyTorch, and ❤️

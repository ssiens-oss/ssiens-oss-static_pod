# StaticWaves AI Music Engine 🎵

User-generated AI music with synthesizers, mixing, and vibe controls.

## Features

- 🎹 **Neural Synthesis** - DDSP-based instrument modeling
- 🎚️ **Vibe Controls** - Energy, darkness, dreaminess, aggression
- 🎛️ **Genre Mixing** - Blend synthwave, lofi, techno, etc.
- 🎸 **Instrument Selection** - Choose presets for bass, lead, pad, drums
- 📊 **Stem Export** - Download individual instrument tracks
- ⚡ **Real-time Generation** - GPU-accelerated with MusicGen
- 💳 **Credits System** - Usage-based billing ready

## Architecture

```
Frontend (React)
  ↓
FastAPI Gateway
  ↓
Redis Queue
  ↓
GPU Worker
  ├─ MusicGen (base audio)
  ├─ DDSP Synth (stems)
  └─ Mixer (final output)
```

## Quick Start

### 1. Install Dependencies

```bash
# API dependencies
cd music-engine
pip install -r requirements-api.txt

# Worker dependencies (separate env recommended)
pip install -r requirements-worker.txt
```

### 2. Start Services with Docker

```bash
cd music-engine
docker-compose up -d
```

This starts:
- Redis (port 6379)
- Music API (port 8000)
- GPU Worker

### 3. Test API

```bash
curl http://localhost:8000/health
```

### 4. Generate Music

```python
import requests

spec = {
    "bpm": 120,
    "key": "C minor",
    "duration": 30,
    "vibe": {
        "energy": 0.8,
        "dark": 0.6,
        "dreamy": 0.4,
        "aggressive": 0.2
    },
    "genre_mix": {
        "synthwave": 0.6,
        "lofi": 0.3,
        "techno": 0.1
    },
    "instruments": {
        "bass": "analog_mono",
        "lead": "supersaw",
        "pad": "granular_pad",
        "drums": "808"
    },
    "stems": True
}

# Generate
response = requests.post("http://localhost:8000/generate", json=spec)
job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8000/status/{job_id}")
print(status.json())

# Download when complete
import time
while True:
    status = requests.get(f"http://localhost:8000/status/{job_id}").json()
    if status["status"] == "completed":
        print(f"Download: http://localhost:8000/download/{job_id}/mix")
        break
    time.sleep(2)
```

## MusicSpec JSON

The core of user-generated music:

```json
{
  "bpm": 120,
  "key": "C minor",
  "duration": 45,
  "vibe": {
    "energy": 0.8,
    "dark": 0.6,
    "dreamy": 0.4,
    "aggressive": 0.2
  },
  "genre_mix": {
    "synthwave": 0.6,
    "lofi": 0.3,
    "techno": 0.1
  },
  "instruments": {
    "bass": "analog_mono",
    "lead": "supersaw",
    "pad": "granular_pad",
    "drums": "808"
  },
  "stems": true,
  "seed": 483920
}
```

## API Endpoints

- `POST /generate` - Submit music generation job
- `GET /status/{job_id}` - Get job status
- `GET /download/{job_id}/{file_type}` - Download audio
- `WS /live` - Real-time streaming mode
- `GET /health` - Health check

## Environment Variables

```bash
# API
REDIS_HOST=localhost
REDIS_PORT=6379
OUTPUT_DIR=/data/output

# Worker
MUSICGEN_MODEL=facebook/musicgen-medium  # or -small, -large
```

## GPU Requirements

### Development (Mock Mode)
- No GPU needed
- Uses frequency-based stem separation
- Good for testing UX

### Production (Real AI)
- NVIDIA GPU with 8GB+ VRAM
- CUDA 12.1+
- Recommended: RTX 4090, A4000+

## Scaling

### Horizontal Scaling
- Add more workers: `docker-compose up --scale music-worker=4`
- Workers pull from shared Redis queue

### RunPod Deployment
See `../scripts/deploy-runpod-music.sh` for one-command GPU deployment.

## Pricing Model

```python
# Base: 1 credit per 10 seconds
base_cost = max(1, duration // 10)

# Stems: +2 credits
stem_cost = 2 if stems else 0

total = base_cost + stem_cost
```

Example:
- 30s preview: 3 credits
- 30s with stems: 5 credits
- 60s with stems: 8 credits

## Advanced: Real MusicGen

To use actual Meta MusicGen instead of mock generation:

```bash
# Install PyTorch + CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install audiocraft
pip install git+https://github.com/facebookresearch/audiocraft.git

# Install DDSP (optional, for true neural synthesis)
pip install ddsp tensorflow
```

Then restart the worker - it will auto-detect and use MusicGen.

## File Structure

```
music-engine/
├── api/
│   ├── main.py          # FastAPI server
│   └── credits.py       # Billing system
├── worker/
│   ├── worker.py        # Main worker loop
│   ├── musicgen_engine.py  # MusicGen wrapper
│   ├── ddsp_synth.py    # Stem synthesis
│   └── mixer.py         # Mixing & export
├── shared/
│   ├── music_spec.py    # Data models
│   └── utils.py         # Utilities
├── docker/
│   ├── api.Dockerfile
│   └── worker.Dockerfile
└── docker-compose.yml
```

## Integration with POD App

The music engine integrates with your POD app:

1. **Add music to designs** - Generate background music for product videos
2. **Social content** - Create TikTok/Instagram Reels with custom music
3. **Brand identity** - Unique sonic branding for your merch line

See `components/MusicControls.tsx` for React integration.

## License

MIT - Use freely in commercial products

---

**Need help?** Open an issue or check the docs.

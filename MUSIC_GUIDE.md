# StaticWaves AI Music Generation Guide 🎵

Complete guide to the AI music generation system integrated into your POD automation pipeline.

## Overview

The StaticWaves Music Engine enables **user-generated AI music** with full control over:
- 🎹 **Synthesizer instruments** (bass, lead, pad, drums)
- 🎚️ **Vibe controls** (energy, darkness, dreaminess, aggression)
- 🎛️ **Genre mixing** (synthwave, lofi, techno, etc.)
- 📊 **Stem export** (individual instrument tracks)

## Quick Start

### 1. Start Music Services

```bash
cd music-engine
./scripts/start-music-services.sh
```

This starts:
- **Redis** - Job queue (port 6379)
- **Music API** - FastAPI server (port 8000)
- **Music Worker** - GPU processing

### 2. Verify Services

```bash
# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

### 3. Generate Your First Track

**Option A: Using the Web UI**

1. Open http://localhost:5173
2. Navigate to Music tab
3. Adjust vibe sliders
4. Click "Generate Music"
5. Wait for completion
6. Download mix + stems

**Option B: Using the API**

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
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
    "stems": true
  }'
```

## Understanding MusicSpec

Every track is defined by a **MusicSpec JSON**. This is what makes music user-generated and reproducible.

### Basic Parameters

```json
{
  "bpm": 120,          // Beats per minute (60-180)
  "key": "C minor",    // Musical key
  "duration": 45       // Seconds (5-300)
}
```

### Vibe Controls (0.0 - 1.0)

```json
{
  "vibe": {
    "energy": 0.8,     // Low = calm, High = energetic
    "dark": 0.6,       // Low = bright, High = dark
    "dreamy": 0.4,     // Low = crisp, High = dreamy
    "aggressive": 0.2  // Low = smooth, High = aggressive
  }
}
```

**How vibes affect sound:**
- **Energy** → Saturation, compression, tempo feel
- **Dark** → Low-pass filter, detuning
- **Dreamy** → Reverb, chorus, delay
- **Aggressive** → Distortion, transient enhancement

### Genre Mixing (0.0 - 1.0)

```json
{
  "genre_mix": {
    "synthwave": 0.6,  // 60% synthwave
    "lofi": 0.3,       // 30% lofi
    "techno": 0.1      // 10% techno
  }
}
```

Genres blend together. Total doesn't need to equal 1.0.

### Instrument Selection

```json
{
  "instruments": {
    "bass": "analog_mono",    // Bass instrument preset
    "lead": "supersaw",       // Lead synth preset
    "pad": "granular_pad",    // Pad/background preset
    "drums": "808"            // Drum kit preset
  }
}
```

**Available Presets:**

| Type | Presets |
|------|---------|
| Bass | `analog_mono`, `sub_bass`, `fm_bass`, `reese` |
| Lead | `supersaw`, `pluck`, `fm_bell`, `acid` |
| Pad  | `granular_pad`, `string_pad`, `warm_pad`, `dark_pad` |
| Drums | `808`, `909`, `acoustic`, `industrial` |

### Reproducibility

```json
{
  "seed": 483920  // Optional: ensures identical output
}
```

Same seed + same spec = identical music.

## Architecture

```
User adjusts sliders
        ↓
   MusicSpec JSON
        ↓
   FastAPI /generate
        ↓
    Redis Queue
        ↓
    GPU Worker
    ├─ MusicGen → Base audio
    ├─ DDSP Synth → Stems
    └─ Mixer → Final output
        ↓
   Download Mix + Stems
```

## API Endpoints

### Generate Music

```http
POST /generate
Content-Type: application/json

{
  "bpm": 120,
  "key": "C minor",
  "duration": 30,
  "vibe": {...},
  "genre_mix": {...},
  "instruments": {...},
  "stems": true
}

Response:
{
  "job_id": "a3f8c2d1",
  "status": "queued",
  "credits_charged": "5",
  "estimated_time": "30s"
}
```

### Check Status

```http
GET /status/{job_id}

Response:
{
  "job_id": "a3f8c2d1",
  "status": "completed",  // pending, running, completed, failed
  "progress": 100,
  "output_urls": {
    "mix": "/download/a3f8c2d1/mix",
    "bass": "/download/a3f8c2d1/bass",
    "lead": "/download/a3f8c2d1/lead",
    "pad": "/download/a3f8c2d1/pad",
    "drums": "/download/a3f8c2d1/drums"
  }
}
```

### Download Audio

```http
GET /download/{job_id}/mix       # Full mix
GET /download/{job_id}/bass      # Bass stem
GET /download/{job_id}/lead      # Lead stem
GET /download/{job_id}/pad       # Pad stem
GET /download/{job_id}/drums     # Drums stem
```

## Integration with POD Pipeline

### Use Case 1: Product Video Music

Generate custom music for product showcase videos:

```typescript
// Generate music for a product video
const musicSpec = {
  bpm: 110,
  key: 'E minor',
  duration: 15,  // 15s for Instagram Reel
  vibe: {
    energy: 0.7,
    dark: 0.3,
    dreamy: 0.6,
    aggressive: 0.1
  },
  genre_mix: {
    lofi: 0.7,
    synthwave: 0.3
  },
  instruments: {
    bass: 'sub_bass',
    lead: 'pluck',
    pad: 'warm_pad',
    drums: '808'
  },
  stems: false  // Just need the mix
};

const { jobId } = await generateMusic(musicSpec);
const { audioUrl } = await waitForCompletion(jobId);

// Use audioUrl in video creation
createProductVideo(designImage, audioUrl);
```

### Use Case 2: Brand Sonic Identity

Create consistent brand music:

```typescript
// Store brand music spec
const brandMusicSpec = {
  bpm: 120,
  key: 'C major',
  vibe: { energy: 0.6, dark: 0.2, dreamy: 0.5, aggressive: 0.1 },
  genre_mix: { synthwave: 0.5, lofi: 0.5 },
  instruments: { bass: 'analog_mono', lead: 'supersaw', pad: 'granular_pad', drums: '808' },
  seed: 12345  // Same seed = consistent brand sound
};

// Generate variations by changing seed
const variations = await Promise.all(
  [1, 2, 3].map(i =>
    generateMusic({ ...brandMusicSpec, seed: 12345 + i })
  )
);
```

### Use Case 3: TikTok/Instagram Content

Generate trending-style music for social:

```typescript
const tiktokMusic = {
  bpm: 140,  // Faster for TikTok
  key: 'A minor',
  duration: 15,
  vibe: {
    energy: 0.9,
    dark: 0.4,
    dreamy: 0.3,
    aggressive: 0.5
  },
  genre_mix: {
    techno: 0.6,
    synthwave: 0.4
  },
  instruments: {
    bass: 'fm_bass',
    lead: 'acid',
    pad: 'dark_pad',
    drums: '909'
  },
  stems: true  // Get stems for remixing
};
```

## Pricing Model (Credits)

```python
# Base cost: 1 credit per 10 seconds
base = max(1, duration // 10)

# Stems export: +2 credits
stems_cost = 2 if stems else 0

total = base + stems_cost
```

**Examples:**
- 30s preview: **3 credits**
- 30s with stems: **5 credits**
- 60s with stems: **8 credits**
- 120s with stems: **14 credits**

## Advanced Features

### Real-time Mode (Coming Soon)

Live music that evolves based on user interaction:

```typescript
// Connect to live mode
const ws = new WebSocket('ws://localhost:8000/live');

// Send vibe updates in real-time
ws.send(JSON.stringify({
  vibe: {
    energy: 0.9,  // User enters combat
    tension: 0.8
  }
}));

// Receive audio chunks
ws.onmessage = (event) => {
  playAudioChunk(event.data);
};
```

### Custom Instrument Packs

Add your own instrument presets:

```python
# In ddsp_synth.py
CUSTOM_INSTRUMENTS = {
  'bass': {
    'my_custom_bass': {
      'type': 'analog',
      'cutoff': 200,
      'resonance': 0.7,
      # ... DDSP parameters
    }
  }
}
```

## GPU Requirements

### Development Mode (Default)
- **No GPU required**
- Uses mock generation (frequency-based)
- Good for UI/UX testing

### Production Mode
- **NVIDIA GPU with 8GB+ VRAM**
- CUDA 12.1+
- Recommended: RTX 4090, A4000+

Install real MusicGen:
```bash
pip install torch audiocraft
# Worker will auto-detect and use it
```

## Monitoring & Debugging

### View Logs

```bash
# All services
docker-compose logs -f

# Just worker
docker-compose logs -f music-worker

# Just API
docker-compose logs -f music-api
```

### Check Queue

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# See pending jobs
LLEN music_jobs

# View job data
GET job:a3f8c2d1:status
GET job:a3f8c2d1:data
```

### Performance Metrics

```bash
# API health
curl http://localhost:8000/health

# Worker status
docker stats music-worker
```

## Troubleshooting

### "Job stuck in pending"

**Cause:** Worker not running or crashed

**Fix:**
```bash
# Restart worker
docker-compose restart music-worker

# Check logs
docker-compose logs music-worker
```

### "Out of memory"

**Cause:** GPU VRAM exhausted

**Fix:**
- Use smaller model: `MUSICGEN_MODEL=facebook/musicgen-small`
- Reduce duration
- Limit concurrent workers

### "Audio is silent/corrupted"

**Cause:** Mixing error or bad spec

**Fix:**
- Check vibe values are 0.0-1.0
- Ensure instruments are valid presets
- Check worker logs for errors

## Deployment

### Local Development

```bash
cd music-engine
docker-compose up
```

### RunPod GPU Cloud

```bash
# Deploy to RunPod with GPU
cd music-engine
docker build -f docker/worker.Dockerfile -t staticwaves-music .
docker tag staticwaves-music your-dockerhub/staticwaves-music
docker push your-dockerhub/staticwaves-music

# Create RunPod pod with your image
# See runpod-config.json for template
```

### Production Scaling

```bash
# Scale workers horizontally
docker-compose up -d --scale music-worker=4

# All workers pull from same Redis queue
```

## Next Steps

1. **Generate your first track** using the web UI
2. **Experiment with vibe sliders** to understand the sound
3. **Integrate into POD pipeline** for product videos
4. **Deploy to GPU** for production quality
5. **Customize instrument presets** for your brand

---

**Questions?** Check the [main README](README.md) or open an issue.

🎵 **Happy music making!** 🎵

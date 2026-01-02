# StaticWaves AI Music - Quick Start Guide 🎵

Get up and running with AI music generation in under 5 minutes!

## One-Command Start

```bash
./start-staticwaves.sh
```

That's it! The script will:
- ✅ Check and install dependencies
- ✅ Start Redis (job queue)
- ✅ Start Music API server
- ✅ Start DDSP WebSocket server
- ✅ Start Music Worker
- ✅ Start Web GUI
- ✅ Open your browser automatically

## What You Get

### 🎹 Real-Time Live Mode
1. Click "Play Live" in the GUI
2. Adjust vibe sliders (energy, tension, darkness)
3. Select instruments (violin, cello, trumpet, synths)
4. Hear music change instantly

### 🎵 Full Track Generation
1. Set BPM, key, and duration
2. Adjust vibe controls
3. Click "Generate Track"
4. Download mix + stems when complete

### 📊 Live Visualization
- Waveform display (time domain)
- Spectrum analyzer (frequency domain)
- Real-time audio monitoring

## Services Running

| Service | URL | Purpose |
|---------|-----|---------|
| **Web GUI** | http://localhost:3001 | Main interface |
| **Music API** | http://localhost:8000 | Generation endpoints |
| **API Docs** | http://localhost:8000/docs | Swagger docs |
| **DDSP Server** | ws://localhost:8765 | Live audio streaming |
| **Redis** | localhost:6379 | Job queue |

## Usage Examples

### Live Performance Mode

```typescript
// In the GUI
1. Click "Play Live"
2. Adjust sliders in real-time
3. Switch instruments
4. Music adapts instantly
```

### Generate a Track

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "bpm": 120,
    "key": "C minor",
    "duration": 60,
    "vibe": {
      "energy": 0.8,
      "tension": 0.6,
      "darkness": 0.5,
      "complexity": 0.7
    },
    "stems": true
  }'
```

### Automatic Generation

```bash
# One-click song generation
curl -X POST "http://localhost:8000/generate/auto?genre=synthwave&mood=energetic&duration=120"

# Use a preset
curl -X POST http://localhost:8000/generate/preset/workout_energy

# Generate a playlist
curl -X POST "http://localhost:8000/generate/playlist?mood=chill&count=5"
```

## Game Integration

### Unity

```csharp
using StaticWaves;

public class MusicController : MonoBehaviour
{
    void OnCombatStart()
    {
        // Music becomes intense
        StaticWavesMusic.SetCombat();
    }

    void OnExploration()
    {
        // Music becomes calm
        StaticWavesMusic.SetExploration();
    }
}
```

See `game-integration/unity/StaticWavesMusic.cs`

### Unreal Engine

```cpp
#include "StaticWavesMusicSubsystem.h"

void ACombatManager::OnBossEnter()
{
    auto* Music = GetGameInstance()
        ->GetSubsystem<UStaticWavesMusicSubsystem>();

    Music->SetBoss();
}
```

See `game-integration/unreal/StaticWavesMusicSubsystem.h`

## Advanced Features

### Multi-Layer Composition

The system uses 5 independent layers:
- **Rhythm** - Drums and percussion
- **Bass** - Low-end foundation
- **Harmony** - Chords and pads
- **Melody** - Lead instruments
- **Texture** - Atmosphere and FX

Each layer adapts independently based on context.

### DDSP Synthesis

Real instrument models powered by Differentiable Digital Signal Processing:
- Violin, Cello, Bass
- Trumpet, Trombone, Flute
- Analog synths
- FM synthesis
- Custom instruments (trainable)

### WebSocket Audio Streaming

- Low latency (<100ms)
- 32kHz sample rate
- Real-time parameter control
- Polyphonic support

## Troubleshooting

### Port Already in Use

If ports 3000/3001 are busy:
```bash
# The startup script auto-detects free ports
# Check logs/gui.log for actual port
cat logs/gui.log | grep "Local:"
```

### DDSP Server Won't Start

```bash
# Check if Python deps are installed
source music-engine/.venv/bin/activate
pip install websockets numpy

# Check logs
tail -f logs/ddsp-server.log
```

### No Audio in Browser

1. Click anywhere in the page (browser audio policy)
2. Check browser console for errors
3. Ensure DDSP server is running:
   ```bash
   curl ws://localhost:8765
   ```

### Job Stuck in Queue

```bash
# Check worker status
tail -f logs/music-worker.log

# Check Redis
redis-cli
> LLEN music_jobs
> GET job:YOUR_JOB_ID:status
```

## Stopping Services

```bash
./stop-staticwaves.sh
```

This cleanly stops all services and releases ports.

## Directory Structure

```
staticwaves/
├── music-engine/          # Backend services
│   ├── api/              # FastAPI server
│   ├── worker/           # Music generation workers
│   └── shared/           # Shared code
├── mashdeck/             # Frontend
│   └── gui/web/          # React GUI
├── game-integration/      # Unity & Unreal plugins
├── logs/                 # Service logs
├── data/output/          # Generated music files
└── models/ddsp/          # Instrument models
```

## Next Steps

1. **Explore the GUI** - Try all the controls and presets
2. **Read API Docs** - http://localhost:8000/docs
3. **Try Game Integration** - Test Unity or Unreal plugins
4. **Customize Instruments** - Train custom DDSP models
5. **Deploy to Production** - See deployment guides

## Getting Help

- **Documentation**: `/STATICWAVES_AI_MUSIC.md`
- **Music Guide**: `/MUSIC_GUIDE.md`
- **API Reference**: http://localhost:8000/docs
- **Logs**: `tail -f logs/*.log`

## Credits

Built with:
- Meta AudioCraft (MusicGen)
- Google DDSP (Magenta)
- FastAPI
- React + Vite
- Redis

---

**🎵 Enjoy creating AI music! 🎵**

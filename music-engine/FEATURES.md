
# StaticWaves AI Music Engine - Complete Feature List 🎵✨

## 🚀 Automatic Music Generation

### Random Song Generator
Generate complete, unique songs with one click - no configuration needed!

```bash
POST /generate/auto
```

**Parameters:**
- `genre` (optional) - synthwave, techno, house, lofi, ambient, etc.
- `mood` (optional) - energetic, chill, dark, dreamy, uplifting, etc.
- `duration` (optional) - 30-600 seconds
- `include_lyrics` (optional) - Generate AI lyrics with Claude

**Example:**
```bash
curl -X POST "http://localhost:8000/generate/auto?genre=synthwave&mood=dark&duration=180"
```

**What You Get:**
- Complete song structure (intro, verse, chorus, bridge, outro)
- Professionally mixed audio
- Genre-appropriate instruments and vibes
- Optional AI-generated lyrics
- Unique every time!

---

## 🎯 Smart Presets

8 AI-optimized presets for specific activities and moods:

| Preset | Use Case | Vibe | Duration |
|--------|----------|------|----------|
| `morning_motivation` | Start your day | Uplifting, energetic | 3 min |
| `deep_focus` | Study/work concentration | Calm, peaceful | 4 min |
| `workout_energy` | Intense exercise | High energy, aggressive | 2.5 min |
| `sleep_ambient` | Sleep/relaxation | Dreamy, minimal energy | 5 min |
| `party_vibes` | Celebrations | Euphoric, energetic | 3 min |
| `gaming_intensity` | Gaming sessions | Aggressive, intense | 3.5 min |
| `meditation` | Mindfulness | Peaceful, atmospheric | 10 min |
| `creative_flow` | Creative work | Dreamy, medium energy | 4 min |

**Usage:**
```bash
POST /generate/preset/workout_energy
POST /generate/preset/deep_focus
POST /generate/preset/meditation
```

**Example Response:**
```json
{
  "job_id": "abc123",
  "status": "queued",
  "preset": "workout_energy",
  "song_info": {
    "title": "Workout Energy Mix",
    "duration": 150
  }
}
```

---

## 🎶 Playlist Generation

Generate entire playlists with cohesive moods!

```bash
POST /generate/playlist?mood=chill&count=8&duration_per_song=120
```

**Parameters:**
- `mood` (required) - energetic, chill, dark, dreamy, uplifting, aggressive, peaceful, mysterious, euphoric, nostalgic
- `count` (1-20) - Number of songs
- `duration_per_song` (30-300s) - Length of each track

**What You Get:**
- Multiple songs with unified mood
- Each song is unique but thematically consistent
- Perfect for workout mixes, study sessions, road trips

**Example:**
```bash
# Generate 5-song chill playlist
curl -X POST "http://localhost:8000/generate/playlist?mood=chill&count=5&duration_per_song=180"
```

**Response:**
```json
{
  "playlist_id": "playlist_xyz",
  "mood": "chill",
  "song_count": 5,
  "job_ids": ["job1", "job2", "job3", "job4", "job5"],
  "message": "Generating 5 chill songs..."
}
```

---

## 🔄 Song Variations

Create variations of existing songs!

```bash
POST /generate/variations?base_job_id=abc123&count=3
```

**What It Does:**
- Takes an existing song
- Creates similar but unique versions
- Tweaks vibe slightly (±15%)
- Different seeds for variety
- Keeps same genre and structure

**Use Cases:**
- Create album variations
- A/B test different vibes
- Provide user options
- Generate remixes

---

## 🎼 Song Structure System

All automatically generated songs have professional structure:

### Standard Structure (Pop/Electronic)
```
Intro (8s) → Verse (16s) → Chorus (16s) →
Verse (16s) → Chorus (16s) → Bridge (12s) →
Chorus (16s) → Outro (12s)

Total: ~112s
```

### EDM Banger
```
Intro → Build → DROP → Breakdown → Build → DROP → Outro
```

### Lo-Fi Chill
```
Intro → Main Groove → Variation → Return to Groove → Fade Out
```

### Cinematic Epic
```
Mysterious Opening → Rising Action → Epic Climax →
Emotional Moment → Final Rise → Ultimate Climax → Resolution
```

### Trap Anthem
```
Minimal Intro → Verse → Pre-Drop → DROP →
Verse → Pre-Drop → DROP → Outro
```

### Ambient Journey
```
Ethereal Opening → Gradual Evolution → Peak Atmosphere →
Introspective Moment → Peaceful Resolution
```

**Dynamic Structures:**
The AI automatically chooses the best structure based on:
- Genre
- Energy level
- Duration
- Mood

---

## 🌍 Expanded Genres

### 15+ Main Genres
Each with 3-5 sub-genres for precise control:

#### Electronic
- **Synthwave**: retrowave, outrun, darksynth, dreamwave, chillwave
- **Techno**: detroit_techno, minimal_techno, acid_techno, industrial_techno, melodic_techno
- **House**: deep_house, tech_house, progressive_house, tropical_house, future_house
- **Dubstep**: brostep, melodic_dubstep, riddim, drumstep, future_bass
- **Trance**: progressive_trance, uplifting_trance, psytrance, vocal_trance, tech_trance
- **Drum & Bass**: liquid_dnb, neurofunk, jump_up, jungle, darkstep

#### Chill/Ambient
- **Lo-Fi**: lofi_beats, chillhop, jazzhop, study_beats, chill_lofi
- **Ambient**: dark_ambient, space_ambient, drone, atmospheric, cinematic_ambient
- **Chillwave**: vaporwave, future_funk, mallsoft, hardvapour

#### Hip Hop/Trap
- **Trap**: hard_trap, melodic_trap, dark_trap, future_trap, latin_trap
- **Boom Bap**: golden_age, underground_hip_hop, jazz_rap, east_coast

#### Other
- **Indie Electronic**: electropop, indietronica, dream_pop, synth_pop
- **Experimental**: glitch, idm, noise, avant_garde, abstract
- **World Fusion**: ethnic_electronica, tribal_house, oriental_bass, afro_house
- **Cinematic**: epic, trailer_music, orchestral_hybrid, dark_cinematic, uplifting_cinematic

**Explore Genres:**
```bash
GET /genres
GET /genres/synthwave/sub-genres
```

---

## 📝 AI Lyrics Generation

Generate song lyrics with Claude!

**Integrated into auto-generation:**
```bash
POST /generate/auto?include_lyrics=true
```

**What You Get:**
```json
{
  "title": "Neon Dreams",
  "sections": [
    {
      "type": "verse",
      "lyrics": [
        "In the neon glow of city lights",
        "Where synthwave echoes through the nights",
        "Every beat, every sound",
        "Takes me higher off the ground"
      ]
    },
    {
      "type": "chorus",
      "lyrics": [
        "We're riding on electric waves",
        "Dancing through the digital haze",
        "Feel the rhythm, feel the flow",
        "Let the music take control"
      ]
    }
  ],
  "theme": "futuristic nostalgia",
  "mood_tags": ["synthwave", "electronic", "uplifting", "nostalgic"]
}
```

**Requirements:**
- `ANTHROPIC_API_KEY` environment variable
- Claude API access
- Costs ~$0.01-0.02 per song

---

## 🎨 Vibe Profiles

Each genre has a default vibe profile that gets automatically applied:

```python
# Synthwave
vibe = {
    "energy": 0.6,
    "dark": 0.5,
    "dreamy": 0.7,
    "aggressive": 0.3
}

# Dubstep
vibe = {
    "energy": 0.9,
    "dark": 0.7,
    "dreamy": 0.3,
    "aggressive": 0.9
}

# Lo-Fi
vibe = {
    "energy": 0.3,
    "dark": 0.2,
    "dreamy": 0.7,
    "aggressive": 0.1
}
```

These are automatically applied and can be customized in manual mode.

---

## 🎹 Instrument Presets

### Bass Instruments
- `analog_mono` - Classic analog synth bass
- `sub_bass` - Deep sub frequencies
- `fm_bass` - FM synthesis bass
- `reese` - Heavy detuned bass (Drum & Bass style)

### Lead Instruments
- `supersaw` - Thick, lush lead sound
- `pluck` - Short, percussive lead
- `fm_bell` - Bell-like FM tones
- `acid` - Squelchy acid lead (303-style)

### Pad Instruments
- `granular_pad` - Textured, evolving pad
- `string_pad` - String-like sustained pad
- `warm_pad` - Warm, analog-style pad
- `dark_pad` - Dark, atmospheric pad

### Drum Kits
- `808` - Classic TR-808 drum machine
- `909` - TR-909 techno drums
- `acoustic` - Natural drum sounds
- `industrial` - Harsh, metallic drums

---

## 📊 API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | Manual generation (existing) |
| `/generate/auto` | POST | 🆕 Automatic song generation |
| `/generate/preset/{name}` | POST | 🆕 Smart preset generation |
| `/generate/playlist` | POST | 🆕 Playlist generation |
| `/generate/variations` | POST | 🆕 Create song variations |
| `/status/{job_id}` | GET | Check job status |
| `/download/{job_id}/{type}` | GET | Download audio |
| `/genres` | GET | 🆕 List all genres |
| `/genres/{genre}/sub-genres` | GET | 🆕 Get sub-genres |
| `/structures` | GET | 🆕 List song structures |
| `/presets` | GET | 🆕 List smart presets |
| `/health` | GET | Health check |

---

## 🎯 Use Case Examples

### 1. Morning Routine App
```bash
# Generate energizing morning music
POST /generate/preset/morning_motivation
```

### 2. Fitness App
```bash
# Create workout playlist
POST /generate/playlist?mood=energetic&count=10&duration_per_song=180
```

### 3. Study/Focus App
```bash
# Deep focus music
POST /generate/preset/deep_focus
```

### 4. Social Media Content
```bash
# Quick 15s TikTok track
POST /generate/auto?genre=trap&duration=15&mood=aggressive
```

### 5. Video Game
```bash
# Generate variations for level music
POST /generate/auto?genre=cinematic&duration=120
# Then create variations
POST /generate/variations?base_job_id=abc123&count=5
```

### 6. Podcast Intros
```bash
# Create unique podcast intro
POST /generate/auto?genre=indie_electronic&duration=30&mood=uplifting
```

---

## 💡 Pro Tips

### 1. Consistent Brand Sound
Use seeds for reproducible music:
```json
{
  "seed": 12345  // Same seed = same style
}
```

### 2. Evolution Series
Generate evolving tracks that build energy:
```python
# SDK usage
series = auto_generator.generate_evolution_series(base_spec, steps=5)
# Creates 5 tracks that progressively increase in intensity
```

### 3. Genre Exploration
```bash
# Get all genres
GET /genres

# Explore sub-genres
GET /genres/synthwave/sub-genres
```

### 4. Batch Generation
Generate multiple tracks in parallel:
```bash
# Use playlist endpoint for batch
POST /generate/playlist?mood=chill&count=20
```

---

## 🔥 What Makes This Amazing

✅ **Fully Automatic** - No music theory needed
✅ **Professional Quality** - Complete song structures and mixing
✅ **Infinite Variety** - Never generates the same song twice
✅ **15+ Genres** - 80+ sub-genres for precise control
✅ **AI Lyrics** - Optional Claude-powered lyric generation
✅ **Smart Presets** - Activity-optimized music generation
✅ **Playlists** - Generate entire albums with one click
✅ **Variations** - Create remixes and alternatives
✅ **Reproducible** - Seeds for consistent branding
✅ **Scalable** - Queue-based architecture

---

## 📚 Learn More

- [Main README](README.md) - Setup and installation
- [Music Guide](../MUSIC_GUIDE.md) - Detailed usage guide
- [API Docs](http://localhost:8000/docs) - Interactive API documentation

---

**Generated music is royalty-free and ready for commercial use!** 🎉

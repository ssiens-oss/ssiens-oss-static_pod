# MashDeck v1.0 - Complete AI Music Production System

**The world's first AI music system with full-length songs, live vocals, rap battles, and auto-release.**

---

## 🎵 What is MashDeck?

MashDeck is a complete AI-powered music production ecosystem that goes far beyond simple loop generation:

- **Full-length structured songs** (3-6 minutes) with intro, verse, chorus, bridge, outro
- **AI vocals** with rap, singing, harmonies, and backing vocals
- **Live features** including chat-reactive freestyle rap and AI rapper battles
- **Auto-release** to Spotify, TikTok, YouTube Music
- **Creator marketplace** with revenue sharing
- **MIDI export** for DAW integration

This is the system described in the ChatGPT conversation - now fully implemented and ready to use.

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Install system audio dependencies
sudo apt-get install ffmpeg portaudio19-dev
```

### Generate Your First Song

```bash
# Generate a complete EDM track with vocals
python -m mashdeck.cli generate --style edm --output my_first_song --variants

# Output:
#   my_first_song/
#   ├── song_final.wav          # Final mastered track
#   ├── song_plan.json          # Song structure
#   ├── sections/               # Individual sections
#   ├── vocals/                 # Vocal tracks
#   └── variants/               # Platform-specific versions
```

### Other Commands

```bash
# Generate vocals for existing instrumental
python -m mashdeck.cli vocal my_first_song --midi

# Live freestyle rap mode
python -m mashdeck.cli freestyle

# Run AI rapper battle
python -m mashdeck.cli battle --rounds 5

# Auto-release to platforms
python -m mashdeck.cli release my_first_song/song_final.wav --title "My Track" --platforms spotify,tiktok
```

---

## 📋 Features

### 1. Full-Length Song Generation

MashDeck generates **complete, structured songs** not just loops:

- **Song Planner**: AI-driven structure with intro, verses, choruses, bridges, outro
- **Section Generator**: MusicGen-powered section-by-section generation
- **Energy Mapping**: Dynamic energy levels throughout the song
- **Transitions**: Automatic crossfades and risers between sections
- **Mastering**: Broadcast-ready loudness normalization

**Supported Styles**: EDM, Lo-Fi, Trap, Hip-Hop, Ambient, Rock

### 2. AI Vocal System

**Rap Generation**:
- Bar-aware lyrics with syllable timing
- Energy-based flow patterns
- Live freestyle from chat topics

**Sung Melodies**:
- Key-locked melody generation
- Scale-constrained note selection
- Hook/chorus optimization

**Harmonies & Backing**:
- Automatic 3rd/5th/octave harmonies
- Stereo-width backing doubles
- EDM-style chant stacks

**Voice Synthesis**:
- XTTS-based text-to-speech
- Voice cloning support
- Multilingual vocals (EN, ES, FR, DE, JP, etc.)

### 3. Live Features

**Chat-Reactive Freestyle**:
- Extracts trending topics from chat
- Generates freestyle rap in real-time
- Integrates with YouTube/TikTok live streams

**AI Rapper Battles**:
- Two-sided competitive battles
- Real-time scoring (message rate, votes, engagement)
- Chat-fueled lyric generation
- Round-by-round winner declaration

### 4. MIDI Export

Export melodies and harmonies as MIDI for:
- Ableton Live
- FL Studio
- Logic Pro
- Any DAW with MIDI support

### 5. Auto-Release Pipeline

One-command distribution to:
- **Spotify** (via distributor API)
- **TikTok** (auto-creates 30s clips)
- **YouTube Music**

Platform-optimized loudness variants included.

### 6. Creator Marketplace

- Upload and sell presets, voice packs, battle themes
- 60/40 revenue share (creator/platform)
- Token-based economy
- Stripe/PayPal integration ready

---

## 🛠️ Architecture

```
MashDeck/
├── song_engine/          # Full-length song generation
│   ├── planner.py        # Song structure AI
│   ├── generator.py      # MusicGen section generator
│   ├── arranger.py       # Timeline arrangement
│   ├── master.py         # Auto-mastering
│   └── pipeline.py       # End-to-end orchestration
│
├── vocals/               # AI vocal system
│   ├── roles/            # Rap vs sing assignment
│   ├── rap/              # Rap lyric generator
│   ├── sing/             # Melody generator
│   ├── harmony/          # Harmonies engine
│   ├── synthesis.py      # XTTS vocal synthesis
│   ├── midi_export.py    # MIDI export
│   └── pipeline.py       # Vocal generation pipeline
│
├── live/                 # Live features
│   ├── chat/             # Chat ingestion
│   ├── freestyle.py      # Live freestyle engine
│   └── battle/           # AI rapper battles
│
├── release/              # Auto-release
│   ├── spotify.py
│   ├── tiktok.py
│   ├── youtube.py
│   └── pipeline.py
│
└── marketplace/          # Creator economy
    ├── store.py
    ├── payouts.py
    └── assets.py
```

---

## 📊 Token System

MashDeck uses a token economy for metering and monetization:

**Compute Tokens (CT)** - Used for AI operations:
- Full song generation: 40-60 CT
- Vocal generation: 10-20 CT
- Freestyle rap: 3 CT
- Battle round: 5 CT per side

**Access Tokens (AT)** - Unlock features:
- Preset packs
- Voice personas
- Battle themes
- MIDI exports

**Creator Tokens (CR)** - Revenue sharing:
- Earned when others use your assets
- Redeemable for cash or CT

---

## 🎯 Use Cases

### Music Creator
Generate full tracks → Export to DAW → Release to Spotify

### Live Streamer
Chat-reactive music → Freestyle battles → Audience engagement

### Content Creator
Auto-generate TikTok sounds → Viral music for videos

### Producer
MIDI toplines → Vocal references → Creative starting points

### Radio/Podcast
AI DJ host → Auto-generated interludes → Dynamic content

---

## 🔌 Integration with StaticWaves OS

MashDeck is designed to integrate with the StaticWaves POD pipeline:

```python
# Generate music for POD products
from mashdeck import generate_full_song

song = generate_full_song(style="lofi", title="Chill Vibes")

# Use as product audio preview
# Upload to Spotify/TikTok
# Sync with POD designs
```

---

## 📈 Roadmap

### v1.1 (Next Release)
- [ ] DiffSinger integration (formant-corrected singing)
- [ ] OBS native plugin (C++ source)
- [ ] Web UI for live battles
- [ ] GPU worker deployment (RunPod)

### v1.2
- [ ] Voice cloning API
- [ ] Multi-language rap translation
- [ ] Real-time stream integration (YouTube/Twitch)
- [ ] VST plugin support

### v2.0
- [ ] DAW plugins (Ableton/FL Studio)
- [ ] Mobile app
- [ ] Blockchain/NFT integration (optional)
- [ ] White-label licensing

---

## 🤝 Contributing

This is currently a proprietary system being developed as part of StaticWaves OS.

For feature requests or bug reports, please create an issue.

---

## 📜 License

Copyright © 2026 StaticWaves

---

## 🙏 Credits

- **MusicGen**: Meta's Audiocraft library
- **XTTS**: Coqui AI text-to-speech
- **Inspiration**: The comprehensive ChatGPT conversation that designed this system

---

**MashDeck v1.0** - Built with Claude Code and love ❤️

# StaticWaves Music Studio - Quick Start Guide 🎵

Get the **complete GUI** up and running in 5 minutes!

## 🚀 Quick Start (3 Steps)

### Step 1: Start the Music API

```bash
cd music-engine
./scripts/start-music-services.sh
```

This starts:
- ✅ Redis (job queue)
- ✅ Music API (http://localhost:8000)
- ✅ GPU Worker (music generation)

### Step 2: Start the GUI

```bash
# In the root directory
npm run dev:music
```

### Step 3: Open the Music Studio

```
http://localhost:5174
```

**That's it!** You now have the complete Music Studio GUI running! 🎉

---

## 🎨 What You Get

### Beautiful 3-Tab Interface

#### 1. **Auto Tab** - One-Click Generation
- **Random Song** - Generate complete songs instantly
  - Optional: Choose genre, mood, duration
  - Optional: AI lyrics with Claude
- **Quick Presets** - 8 smart presets with icons
  - Morning Motivation
  - Deep Focus
  - Workout Energy
  - Sleep Ambient
  - Party Vibes
  - Gaming Intensity
  - Meditation
  - Creative Flow
- **Playlist** - Generate 3-20 song playlists
  - Choose mood
  - Set song count
  - Configure duration

#### 2. **Manual Tab** - Full Control
- Vibe sliders (energy, dark, dreamy, aggressive)
- Genre mixing
- Instrument selection
- BPM and key controls
- All the features from before!

#### 3. **Library Tab** - Your Music
- All generated tracks
- Real-time progress tracking
- Click to play
- Download options

### Features

✅ **Real-time Progress** - See generation status live
✅ **Waveform Visualization** - Beautiful audio player
✅ **Download Management** - Full mix + stems
✅ **Track Library** - All your generated music
✅ **Responsive UI** - Beautiful gradients and icons
✅ **Status Bar** - Track count and API status

---

## 📸 Screenshots

### Auto Generation
```
┌─────────────────────────────────────────────┐
│  🎵 Music Studio                            │
│  ┌────────┬────────┬────────┐              │
│  │ Auto ✓ │ Manual │ Library│              │
│  └────────┴────────┴────────┘              │
│                                             │
│  ┌──────────────────────────┐              │
│  │ 🎲 Random Song           │              │
│  │ ┌──────┬──────┐          │              │
│  │ │Genre │ Mood │          │              │
│  │ └──────┴──────┘          │              │
│  │ [Generate Random Song]   │              │
│  └──────────────────────────┘              │
│                                             │
│  ┌──────────────────────────┐              │
│  │ Quick Presets            │              │
│  │ ☕ Morning  🧠 Focus      │              │
│  │ 💪 Workout  🌙 Sleep     │              │
│  └──────────────────────────┘              │
└─────────────────────────────────────────────┘
```

### Music Player
```
┌─────────────────────────────────────────────┐
│  Neon Dreams                                │
│  Synthwave • Dark • 180s                    │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │ [Waveform Visualization]              │  │
│  │ 0:45 ━━━━━━━●────────── 3:00         │  │
│  │           ▶️  Pause                   │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Downloads:                                 │
│  [Full Mix] [All Stems]                     │
└─────────────────────────────────────────────┘
```

---

## 🎯 Try These Examples

### Example 1: Generate a Random Dark Synthwave Track
1. Click **Auto** tab
2. Select **Random Song**
3. Choose:
   - Genre: Synthwave
   - Mood: Dark
   - Duration: 180s
4. Click **Generate Random Song**
5. Watch it appear in your library!

### Example 2: Morning Motivation Preset
1. Click **Auto** tab
2. Click **Quick Presets**
3. Click the ☕ **Morning Energy** card
4. Done! Track generates automatically

### Example 3: Workout Playlist
1. Click **Auto** tab
2. Click **Playlist**
3. Select:
   - Mood: Energetic
   - Count: 10 songs
   - Duration: 180s each
4. Click **Generate 10-Track Playlist**
5. All 10 tracks queue up!

### Example 4: Custom Manual Track
1. Click **Manual** tab
2. Adjust sliders:
   - Energy: 80%
   - Dark: 60%
   - Dreamy: 40%
3. Choose instruments
4. Click **Generate Music**

---

## 🎛️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1` | Auto tab |
| `2` | Manual tab |
| `3` | Library tab |
| `Space` | Play/Pause (when track selected) |
| `↓` | Next track in library |
| `↑` | Previous track in library |

---

## 🔧 Configuration

### Environment Variables

Create `.env` in root:

```bash
# Music API
VITE_MUSIC_API_URL=http://localhost:8000

# Optional: Claude API for lyrics
ANTHROPIC_API_KEY=your_claude_api_key_here
```

### Change Default Port

Edit `vite.music.config.ts`:

```typescript
server: {
  port: 5174,  // Change this
}
```

---

## 📚 API Endpoints (Behind the Scenes)

The GUI uses these endpoints:

```
POST /generate/auto
POST /generate/preset/{name}
POST /generate/playlist
GET /status/{job_id}
GET /download/{job_id}/mix
GET /genres
GET /presets
```

---

## 🐛 Troubleshooting

### GUI doesn't load

**Check:**
```bash
# Is the dev server running?
npm run dev:music

# Should see:
# ➜  Local:   http://localhost:5174/
```

### "API not connected"

**Check:**
```bash
# Is the music API running?
curl http://localhost:8000/health

# Should return:
# {"api":"healthy","redis":"healthy"}
```

**Fix:**
```bash
cd music-engine
./scripts/start-music-services.sh
```

### Tracks stuck in "pending"

**Check worker:**
```bash
docker-compose logs music-worker

# Should see:
# ✅ Redis connection successful
# Waiting for jobs...
```

### No audio playback

**Check browser console** for errors
- Ensure CORS is enabled in API
- Check audio file URL is accessible

---

## 🚀 Production Deployment

### Build for Production

```bash
npm run build:music
```

Output: `dist-music/`

### Deploy

```bash
# Serve with any static host
npx serve dist-music

# Or upload to:
# - Vercel
# - Netlify
# - AWS S3 + CloudFront
```

---

## 💡 Pro Tips

### Tip 1: Batch Generation
Use the playlist feature to generate many tracks at once:
```
Playlist → Count: 20 → Generate
```

### Tip 2: Find the Perfect Track
Generate 5 variations of a track you like:
```
Library → Click track → Generate Variations
```

### Tip 3: Custom Presets
Edit `components/AutoMusicGenerator.tsx` to add your own presets!

### Tip 4: Keyboard Workflow
```
1 → Auto Tab
Space → Generate Random
3 → Library Tab
Click track → Space to play
```

---

## 🎉 You're All Set!

You now have a **complete AI music generation studio** with a beautiful GUI!

**Next Steps:**
- Generate your first track
- Try all 8 smart presets
- Create a playlist
- Explore manual controls

**Questions?**
- See [FEATURES.md](FEATURES.md) for all features
- See [MUSIC_GUIDE.md](../MUSIC_GUIDE.md) for advanced usage
- Check API docs: http://localhost:8000/docs

---

🎵 **Happy music making!** 🎵

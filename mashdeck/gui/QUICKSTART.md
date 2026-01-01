# MashDeck GUI - Quick Start Guide

## Easy Option: One-Command Start

From the root directory (`ssiens-oss-static_pod`):

```bash
./start-mashdeck-gui.sh
```

This will:
- Start the FastAPI backend on port 8080
- Start the React frontend on port 3000
- Open your browser automatically

## Manual Option: Step by Step

### 1. Start the Backend (Terminal 1)

```bash
cd mashdeck/gui/api
python3 main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### 2. Start the Frontend (Terminal 2)

```bash
cd mashdeck/gui/web
npm install  # Only needed first time
npm run dev
```

You should see:
```
VITE v6.4.1  ready in 311 ms
➜  Local:   http://localhost:3000/
```

### 3. Open Your Browser

Navigate to: **http://localhost:3000**

## Quick Start from mashdeck/gui Directory

If you're already in the `mashdeck/gui` directory:

```bash
./start.sh
```

## Troubleshooting

**Port 8080 or 3000 already in use?**

Kill existing processes:
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

**Backend won't start?**

Check Python dependencies:
```bash
cd mashdeck
pip install -r requirements.txt
```

**Frontend won't start?**

Reinstall dependencies:
```bash
cd mashdeck/gui/web
rm -rf node_modules package-lock.json
npm install
```

**Module import errors?**

Ensure you're in the correct directory and Python can find the modules:
```bash
# From mashdeck/gui/api
export PYTHONPATH=$PYTHONPATH:../..
python3 main.py
```

## What You'll See

### Home Page (/)
- Feature overview
- Quick navigation cards
- Stats display

### Generate Page (/generate)
- Create full-length songs
- Choose style, BPM, key
- Real-time progress tracking
- Download stems and masters

### Freestyle Page (/freestyle)
- Live chat-reactive rap
- Send messages
- Generate freestyle on demand

### Battle Page (/battle)
- AI rapper battles
- Configure rounds and bars
- Real-time scoring
- Winner declaration

### Marketplace Page (/marketplace)
- Browse assets (presets, voices, MIDI)
- Filter by type
- Purchase with tokens

### Release Page (/release)
- Auto-release to platforms
- Spotify, TikTok, YouTube
- Track release status

## API Endpoints

Backend API documentation: **http://localhost:8080/docs**

WebSocket endpoint: **ws://localhost:8080/ws**

## Default Configuration

- **Backend Port**: 8080
- **Frontend Port**: 3000
- **API Prefix**: /api
- **WebSocket**: /ws

## Next Steps

1. Generate your first song on the Generate page
2. Try the live freestyle feature
3. Run an AI battle
4. Browse the marketplace
5. Auto-release your track

Enjoy MashDeck! 🎵

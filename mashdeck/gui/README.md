# MashDeck GUI

Modern web interface for MashDeck AI Music Production System.

## Features

- **Song Generation**: Create full-length AI songs with customizable parameters
- **Live Freestyle**: Chat-reactive freestyle rap generation
- **AI Battles**: Competitive rapper battles with real-time scoring
- **Marketplace**: Browse and purchase creator assets
- **Auto-Release**: Distribute tracks to Spotify, TikTok, YouTube

## Tech Stack

- **Frontend**: React 18 + Vite
- **Styling**: TailwindCSS
- **Backend**: FastAPI (Python)
- **Real-time**: WebSockets
- **State**: Zustand

## Quick Start

### 1. Start Backend API

```bash
cd mashdeck/gui/api
python main.py
```

Backend will run on `http://localhost:8080`

### 2. Start Frontend

```bash
cd mashdeck/gui/web
npm install
npm run dev
```

Frontend will run on `http://localhost:3000`

### 3. Open Browser

Navigate to `http://localhost:3000`

## API Endpoints

### Song Generation
- `POST /api/generate/song` - Generate a full song
- `GET /api/generate/status/{job_id}` - Check generation status
- `GET /api/styles` - List available music styles

### Freestyle
- `POST /api/freestyle/start` - Start freestyle session
- `POST /api/freestyle/generate` - Generate freestyle rap
- `POST /api/freestyle/chat` - Add chat message

### Battle
- `POST /api/battle/start` - Start AI battle
- `POST /api/battle/round` - Execute battle round
- `POST /api/battle/chat` - Add chat message
- `POST /api/battle/end` - End battle

### Release
- `POST /api/release` - Auto-release track to platforms

### Marketplace
- `GET /api/marketplace/assets` - List assets
- `GET /api/marketplace/asset/{id}` - Get asset details
- `POST /api/marketplace/purchase/{id}` - Purchase asset

### WebSocket
- `WS /ws` - Real-time updates

## Project Structure

```
mashdeck/gui/
├── api/                    # FastAPI backend
│   └── main.py            # API server
│
└── web/                    # React frontend
    ├── src/
    │   ├── pages/         # Page components
    │   │   ├── HomePage.jsx
    │   │   ├── GeneratePage.jsx
    │   │   ├── FreestylePage.jsx
    │   │   ├── BattlePage.jsx
    │   │   ├── MarketplacePage.jsx
    │   │   └── ReleasePage.jsx
    │   ├── App.jsx        # Main app component
    │   └── main.jsx       # Entry point
    │
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

## Development

### Backend Development

The backend API wraps the MashDeck CLI and provides REST endpoints.

```python
# Run backend with auto-reload
uvicorn mashdeck.gui.api.main:app --reload --port 8080
```

### Frontend Development

```bash
# Install dependencies
npm install

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Production Deployment

### Backend

```bash
# Install dependencies
pip install fastapi uvicorn

# Run with gunicorn (production)
gunicorn mashdeck.gui.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend

```bash
# Build production bundle
npm run build

# Serve dist/ with nginx or any static server
```

## Environment Variables

Backend:
- `PORT` - API port (default: 8080)
- `CORS_ORIGINS` - Allowed CORS origins

Frontend:
- `VITE_API_URL` - Backend API URL (default: proxied to localhost:8080)

## Features by Page

### Generate Page
- Style selection (EDM, Lo-Fi, Trap, etc.)
- Custom BPM, key, title
- Platform variants option
- Real-time progress updates
- Audio player preview
- Download options

### Freestyle Page
- Live chat interface
- Real-time message feed
- Freestyle generation on demand
- Audio playback

### Battle Page
- Battle configuration (rounds, bars)
- Live scoring display
- Round-by-round history
- Winner declaration
- Chat simulation for testing

### Marketplace Page
- Asset filtering by type
- Asset cards with stats
- Purchase flow
- Creator attribution

### Release Page
- Track metadata form
- Platform selection
- Release status tracking
- Multi-platform distribution

## WebSocket Events

The GUI uses WebSockets for real-time updates:

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8080/ws')

// Event types:
// - generation_started
// - generation_completed
// - generation_failed
// - freestyle_generated
// - battle_started
// - battle_round_completed
// - battle_ended
```

## Customization

### Theming

Colors are defined in `src/index.css`:

```css
:root {
  --bg-primary: #0a0a0f;
  --bg-secondary: #141420;
  --accent: #8b5cf6;
  --text-primary: #ffffff;
}
```

### API Base URL

Update in `vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://your-backend-url',
      changeOrigin: true
    }
  }
}
```

## Troubleshooting

**Backend won't start**:
- Ensure MashDeck is installed: `pip install -r requirements.txt`
- Check Python path includes parent directory

**Frontend build fails**:
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version (requires 16+)

**WebSocket connection fails**:
- Check backend is running
- Verify port 8080 is not blocked
- Check CORS configuration

## Contributing

This GUI is part of the MashDeck project. See main README for contribution guidelines.

## License

Copyright © 2026 StaticWaves

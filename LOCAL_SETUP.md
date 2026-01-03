# Local Development Setup

This guide will help you run the StaticWaves POD Studio GUI locally with all backend services.

## Quick Start

The easiest way to get started is to use the automated startup script:

```bash
./start-local.sh
```

This script will:
1. Start Redis server (job queue)
2. Set up Python virtual environment
3. Install Music API dependencies
4. Start Music API backend (port 8000)
5. Start Music Studio GUI (port 5174)

When you're done, stop all services with:

```bash
./stop-local.sh
```

## What You Get

After running the startup script, you'll have access to:

### Music Studio GUI
- **URL**: http://localhost:5174
- **Features**: Full music generation interface with manual controls
- **Controls**: BPM, key, vibe sliders, genre mixing, instrument selection

### Music API Backend
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

### Services
- **Redis**: Port 6379 (job queue)
- **Music API**: Port 8000 (FastAPI backend)
- **Frontend**: Port 5174 (Vite dev server)

## Manual Setup (Advanced)

If you prefer to run services individually:

### 1. Start Redis

```bash
redis-server --daemonize yes --logfile logs/redis.log
```

Verify it's running:
```bash
redis-cli ping
# Should return: PONG
```

### 2. Start Music API

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r music-engine/requirements-api.txt

# Set environment variables
export REDIS_HOST=localhost
export REDIS_PORT=6379
export OUTPUT_DIR=$PWD/output

# Start the API
cd music-engine/api
python main.py
```

The API should now be running on http://localhost:8000

### 3. Start Frontend

In a new terminal:

```bash
# Install dependencies (first time only)
npm install

# Start Music Studio dev server
npm run dev:music
```

The GUI should now be accessible at http://localhost:5174

## Configuration

### Environment Variables

The `.env` file contains all configuration. Key variables for local development:

```env
# Music API
VITE_MUSIC_API_URL=http://localhost:8000
REDIS_HOST=localhost
REDIS_PORT=6379

# Output directory for generated audio
OUTPUT_DIR=/data/output

# Optional: Claude API for lyrics generation
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Frontend Proxy Configuration

The Music Studio frontend (port 5174) is configured to proxy `/api/music` requests to the Music API on port 8000. This is configured in `vite.music.config.ts`:

```typescript
server: {
  port: 5174,
  proxy: {
    '/api/music': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api\/music/, '')
    }
  }
}
```

## Testing the Connection

### 1. Test Music API

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {"api":"healthy","redis":"healthy"}
```

### 2. Test Music Generation (Mock)

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "bpm": 120,
    "key": "C",
    "duration": 30,
    "vibe": {
      "energy": 0.7,
      "dark": 0.3,
      "dreamy": 0.5,
      "aggressive": 0.2
    },
    "genre_mix": {
      "electronic": 0.8,
      "hiphop": 0.2
    },
    "instruments": {
      "bass": "808",
      "lead": "synth"
    },
    "stems": false
  }'
```

This will return a job ID. You can check the status with:

```bash
curl http://localhost:8000/status/{job_id}
```

### 3. Test Frontend Connection

Open your browser to http://localhost:5174 and try generating music using the UI. The frontend will communicate with the Music API via the proxy.

## Logs

All logs are stored in the `logs/` directory:

- `logs/redis.log` - Redis server logs
- `logs/music-api.log` - Music API logs

View logs in real-time:

```bash
# Music API logs
tail -f logs/music-api.log

# Redis logs
tail -f logs/redis.log
```

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Check what's using port 8000
lsof -i :8000

# Check what's using port 5174
lsof -i :5174

# Check what's using port 6379 (Redis)
lsof -i :6379
```

Kill the process using the port:
```bash
kill -9 <PID>
```

### Music API Won't Start

Check the logs:
```bash
cat logs/music-api.log
```

Common issues:
- Redis not running: Start Redis first
- Missing dependencies: Run `pip install -r music-engine/requirements-api.txt`
- Port 8000 in use: Stop other services or change the port

### Frontend Can't Connect to API

1. Verify Music API is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check browser console for CORS errors

3. Verify proxy configuration in `vite.music.config.ts`

### Redis Connection Failed

1. Check if Redis is running:
   ```bash
   redis-cli ping
   ```

2. If not running, start it:
   ```bash
   redis-server --daemonize yes --logfile logs/redis.log
   ```

## Development Workflow

### Making Changes

1. **Backend Changes** (Music API)
   - Edit files in `music-engine/api/` or `music-engine/shared/`
   - Restart the Music API:
     ```bash
     ./stop-local.sh
     ./start-local.sh
     ```

2. **Frontend Changes** (React/TypeScript)
   - Edit files in `components/` or service files
   - Vite will auto-reload the browser

### Adding New API Endpoints

1. Add endpoint to `music-engine/api/main.py`
2. Restart Music API
3. Test with curl or Swagger UI (http://localhost:8000/docs)
4. Update frontend service (`services/musicAPI.ts`) to call new endpoint

### Adding New Frontend Features

1. Create/modify components in `components/`
2. Update `MusicStudio.tsx` or `MusicApp.tsx`
3. Use the `musicAPI` service to communicate with backend
4. Test in browser at http://localhost:5174

## Production Notes

This setup is for **local development only**. For production:

1. Use Docker Compose for all services
2. Set up proper environment variables
3. Configure CORS properly
4. Use HTTPS
5. Set up authentication
6. Use a production-grade database instead of Redis for persistence
7. Deploy frontend as static build (`npm run build:music`)

## Next Steps

- **Enable GPU Processing**: Set up the Music Worker for actual audio generation
- **Add Authentication**: Implement user accounts and credit system
- **Deploy**: Use Docker Compose or cloud deployment
- **Integrate ComfyUI**: Add AI image generation for album covers

## Architecture Overview

```
┌─────────────────────┐
│  Music Studio GUI   │  Port 5174 (Vite Dev Server)
│  (React + TS)       │
└──────────┬──────────┘
           │ HTTP
           ▼
    ┌─────────────┐
    │ Vite Proxy  │  /api/music → localhost:8000
    └─────────────┘
           │
           ▼
┌─────────────────────┐
│   Music API         │  Port 8000 (FastAPI)
│   (Python)          │
└──────────┬──────────┘
           │ Redis Protocol
           ▼
┌─────────────────────┐
│   Redis Queue       │  Port 6379
│   (Job Storage)     │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│   Music Worker      │  (Optional - GPU Processing)
│   (MusicGen + DDSP) │
└─────────────────────┘
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Redis Documentation](https://redis.io/documentation)

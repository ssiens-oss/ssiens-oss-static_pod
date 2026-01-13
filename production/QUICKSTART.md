# Production POD Engine - Quick Start

## 30-Second Overview

```
Setup → Configure → Validate → Start ComfyUI → Run Engine → Submit Jobs
```

## Run It Now (Copy & Paste)

### 1️⃣ Setup (1 minute)

```bash
cd /home/user/ssiens-oss-static_pod
npm run production:deploy
```

### 2️⃣ Configure (2 minutes)

```bash
# Edit API key
nano production/.env
# Set: CLAUDE_API_KEY=sk-ant-YOUR_KEY_HERE
# Save: Ctrl+O, Enter, Ctrl+X
```

### 3️⃣ Validate (30 seconds)

```bash
npm run production:validate
```

### 4️⃣ Start ComfyUI (in separate terminal)

```bash
# Terminal 2:
cd /path/to/ComfyUI
python main.py
```

### 5️⃣ Run Engine (30 seconds)

```bash
# Terminal 1:
npm run production:api
```

### 6️⃣ Test (30 seconds)

```bash
# Terminal 3:
# Check health
curl http://localhost:3000/health

# Submit test job
curl -X POST http://localhost:3000/jobs \
  -H "Content-Type: application/json" \
  -d '{"theme":"Cyberpunk","productTypes":["tshirt"],"count":1}'
```

## One-Liner Test (After Setup)

```bash
# Start engine in background and test
npm run production:api & sleep 5 && curl http://localhost:3000/health
```

## Stop Everything

```bash
npm run production:stop
```

## Cheat Sheet

| Command | What It Does |
|---------|--------------|
| `npm run production:deploy` | Setup everything |
| `npm run production:validate` | Check if ready |
| `npm run production:api` | Start (worker pool + API) |
| `npm run production:worker` | Start (single worker) |
| `npm run production:status` | Check status |
| `npm run production:stop` | Stop all |

## API Quick Test

```bash
# Health
curl http://localhost:3000/health

# Stats
curl http://localhost:3000/stats

# Submit job
curl -X POST http://localhost:3000/jobs -H "Content-Type: application/json" \
  -d '{"productTypes":["tshirt"],"theme":"Gaming"}'

# List jobs
curl http://localhost:3000/jobs
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Port 3000 in use | `lsof -i :3000` then kill or change port |
| ComfyUI not found | Start ComfyUI first: `python main.py` |
| API key error | Check `production/.env` has correct key |
| Jobs not processing | Verify ComfyUI is running |

## Files You'll Edit

- `production/.env` - API keys (required)
- `production/config.json` - Settings (optional)

## Ports Used

- `3000` - API Server
- `8188` - ComfyUI (must be running)
- `5432` - PostgreSQL (optional)

## Full Documentation

- 📖 Complete guide: `production/RUN.md`
- 🚀 Deployment: `production/DEPLOYMENT.md`
- 📚 API docs: `production/README.md`

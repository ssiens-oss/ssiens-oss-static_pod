# Production POD Engine - Run Instructions

## Quick Start (5 Minutes)

### Step 1: Initial Setup

```bash
# Run the automated deployment setup
npm run production:deploy
```

This will:
- ✅ Check Node.js and npm versions
- ✅ Install dependencies
- ✅ Create `production/.env` from template
- ✅ Create `production/config.json` from template
- ✅ Create required directories (storage, logs, comfyui_output)
- ⚠️ Warn about missing API key (expected)

### Step 2: Configure API Keys

Edit the environment file with your credentials:

```bash
nano production/.env
```

**Required settings:**
```bash
# REQUIRED: Your Claude API key
CLAUDE_API_KEY=sk-ant-api03-YOUR_ACTUAL_KEY_HERE

# REQUIRED: ComfyUI API URL
COMFYUI_API_URL=http://127.0.0.1:8188

# Optional: Database (use 'memory' for development)
DATABASE_TYPE=memory
```

**Optional platform integrations:**
```bash
# Printify (for product creation)
PRINTIFY_API_KEY=your_printify_key
PRINTIFY_SHOP_ID=your_shop_id

# Shopify (for product publishing)
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_your_token

# Other platforms (TikTok, Etsy, Instagram, Facebook)
# See .env for full list
```

Save the file (Ctrl+O, Enter, Ctrl+X in nano).

### Step 3: Configure Engine Settings (Optional)

Edit the main configuration:

```bash
nano production/config.json
```

Key settings to review:

```json
{
  "orchestrator": {
    "options": {
      "enabledPlatforms": ["printify"],  // Which platforms to use
      "autoPublish": false,               // Auto-publish products
      "tshirtPrice": 19.99,
      "hoodiePrice": 34.99
    }
  },
  "engine": {
    "maxConcurrentJobs": 5,              // Jobs per worker
    "jobTimeout": 3600000,               // 1 hour timeout
    "enableAutoRetry": true
  },
  "workerPool": {
    "workerCount": 3,                    // Number of workers
    "autoRestart": true
  },
  "api": {
    "port": 3000,
    "enableCors": true
  }
}
```

### Step 4: Validate Setup

```bash
npm run production:validate
```

This checks:
- ✅ Node.js version (18+)
- ✅ Configuration files exist
- ✅ API keys are set
- ✅ Dependencies installed
- ⚠️ ComfyUI connectivity (will warn if not running)

Expected output:
```
==================================
Environment Validation
==================================

[✓] Node.js v22.21.1 (OK)
[✓] npm 10.9.4
[✓] production/.env exists
[✓] CLAUDE_API_KEY is set
[✓] COMFYUI_API_URL: http://127.0.0.1:8188
[✓] production/config.json exists
[!] ComfyUI is not reachable (will need to start)

All checks passed! Ready to deploy.
```

### Step 5: Start ComfyUI

**IMPORTANT:** ComfyUI must be running before starting the engine.

```bash
# In a separate terminal, navigate to your ComfyUI installation
cd /path/to/ComfyUI

# Start ComfyUI
python main.py

# Or if using venv:
source venv/bin/activate
python main.py
```

Verify ComfyUI is running:
```bash
curl http://127.0.0.1:8188/system_stats
```

### Step 6: Start the Production Engine

**Option A: Worker Pool with API (Recommended for Production)**

```bash
npm run production:api
```

This starts:
- 3 workers (configurable in config.json)
- REST API server on port 3000
- Job queue with auto-retry
- Health monitoring

**Option B: Single Worker (Good for Development)**

```bash
npm run production:worker
```

This starts a single worker without the API server.

**Option C: Docker (Complete Stack)**

```bash
npm run production:docker
```

This starts everything in Docker containers (requires Docker installed).

### Step 7: Verify the Engine is Running

```bash
# Check status
npm run production:status

# Or check the API directly
curl http://localhost:3000/health
```

Expected response:
```json
{
  "healthy": true,
  "workers": [
    {
      "id": "worker_0_...",
      "healthy": true,
      "health": {
        "healthy": true,
        "worker": true,
        "queue": true,
        "database": true,
        "orchestrator": true
      }
    }
  ]
}
```

## Running Your First Job

### Submit a Test Job

```bash
curl -X POST http://localhost:3000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "Cyberpunk",
    "style": "Neon Art",
    "niche": "Gaming",
    "productTypes": ["tshirt"],
    "count": 1,
    "priority": 10
  }'
```

Response:
```json
{
  "jobId": "job-uuid-here",
  "status": "accepted"
}
```

### Check Job Status

```bash
# Replace <job-id> with the ID from above
curl http://localhost:3000/jobs/<job-id>
```

### Monitor Progress

```bash
# Watch the console output where you started the engine
# Or check status periodically
npm run production:status

# Or view statistics
curl http://localhost:3000/stats
```

## Common Commands

### Management

```bash
# Start engine (worker pool + API)
npm run production:api

# Stop all processes
npm run production:stop

# Check status
npm run production:status

# Validate environment
npm run production:validate
```

### API Endpoints

```bash
# Health check
curl http://localhost:3000/health

# Get statistics
curl http://localhost:3000/stats

# List all jobs
curl http://localhost:3000/jobs

# Get specific job
curl http://localhost:3000/jobs/<job-id>

# List workers
curl http://localhost:3000/workers

# Get metrics
curl http://localhost:3000/metrics?name=job_duration

# Get alerts
curl http://localhost:3000/alerts
```

## Monitoring

### View Logs

Console output shows:
- Worker startup/shutdown
- Job submissions
- Job completions/failures
- Health checks
- Errors and warnings

### Check Worker Health

```bash
curl http://localhost:3000/workers
```

### View Dashboard Data

```bash
# Last 24 hours
curl http://localhost:3000/dashboard

# Last 7 days
curl http://localhost:3000/dashboard?hours=168
```

## Troubleshooting

### Engine Won't Start

1. **Check if already running:**
   ```bash
   npm run production:status
   ```

2. **Check port 3000 availability:**
   ```bash
   lsof -i :3000
   ```

3. **Validate configuration:**
   ```bash
   npm run production:validate
   ```

### ComfyUI Connection Issues

1. **Verify ComfyUI is running:**
   ```bash
   curl http://127.0.0.1:8188/system_stats
   ```

2. **Check ComfyUI URL in .env:**
   ```bash
   grep COMFYUI_API_URL production/.env
   ```

3. **Try accessing ComfyUI web interface:**
   ```
   http://127.0.0.1:8188
   ```

### Jobs Not Processing

1. **Check queue status:**
   ```bash
   curl http://localhost:3000/stats
   ```

2. **Check worker status:**
   ```bash
   curl http://localhost:3000/workers
   ```

3. **View recent alerts:**
   ```bash
   curl http://localhost:3000/alerts
   ```

### API Key Issues

1. **Verify API key is set:**
   ```bash
   grep CLAUDE_API_KEY production/.env
   ```

2. **Ensure no quotes or spaces:**
   ```bash
   # Correct:
   CLAUDE_API_KEY=sk-ant-api03-xxx

   # Wrong:
   CLAUDE_API_KEY="sk-ant-api03-xxx"
   CLAUDE_API_KEY= sk-ant-api03-xxx
   ```

## Stopping the Engine

### Graceful Shutdown

```bash
npm run production:stop
```

This will:
- Send SIGTERM to all engine processes
- Wait for jobs to complete (30 seconds)
- Force kill if still running
- Stop Docker containers if used

### Force Stop

```bash
# Kill all processes immediately
./production/scripts/stop.sh all

# Stop only Docker
./production/scripts/stop.sh docker

# Clean Docker (removes volumes)
./production/scripts/stop.sh docker-clean
```

## Production Deployment

### Using PM2 (Recommended for VPS)

```bash
# Install PM2
npm install -g pm2

# Start with PM2
pm2 start production/examples/worker-pool-api.ts \
  --name pod-engine \
  --interpreter ts-node

# Save configuration
pm2 save

# Setup auto-start on reboot
pm2 startup

# Monitor
pm2 monit

# View logs
pm2 logs pod-engine
```

### Using Docker Compose

```bash
# Build and start all services
npm run production:docker-build

# Check status
cd production && docker-compose ps

# View logs
docker-compose logs -f pod-engine

# Stop
npm run production:stop
```

## Scaling

### Increase Workers

Edit `production/config.json`:
```json
{
  "workerPool": {
    "workerCount": 5  // Increase from 3 to 5
  }
}
```

Restart:
```bash
npm run production:stop
npm run production:api
```

### Increase Concurrency

Edit `production/config.json`:
```json
{
  "engine": {
    "maxConcurrentJobs": 10  // Increase from 5 to 10
  }
}
```

### Dynamic Scaling (via API)

```bash
curl -X POST http://localhost:3000/scale \
  -H "Content-Type: application/json" \
  -d '{"workerCount": 5}'
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CLAUDE_API_KEY` | ✅ Yes | - | Claude API key |
| `COMFYUI_API_URL` | ✅ Yes | http://127.0.0.1:8188 | ComfyUI URL |
| `DATABASE_TYPE` | No | memory | 'memory' or 'postgres' |
| `DATABASE_URL` | No | - | PostgreSQL connection string |
| `WORKER_COUNT` | No | 3 | Number of workers |
| `MAX_CONCURRENT_JOBS` | No | 5 | Jobs per worker |
| `API_PORT` | No | 3000 | API server port |
| `API_AUTH_TOKEN` | No | - | API authentication token |

## Next Steps

1. ✅ Run `npm run production:deploy`
2. ✅ Configure API keys in `production/.env`
3. ✅ Start ComfyUI
4. ✅ Run `npm run production:validate`
5. ✅ Start engine with `npm run production:api`
6. 🎯 Submit your first job!
7. 📊 Monitor via API at http://localhost:3000

## Support

- 📚 Full documentation: `production/README.md`
- 🚀 Deployment guide: `production/DEPLOYMENT.md`
- 💡 Examples: `production/examples/`
- 🐛 Issues: GitHub Issues

**You're ready to run the Production POD Engine!** 🚀

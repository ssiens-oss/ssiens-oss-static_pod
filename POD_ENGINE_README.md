# POD Engine - Production Ready

A production-grade, scalable Print-on-Demand automation engine with job queuing, state persistence, and comprehensive monitoring.

## Features

- **Job Queue System** - Priority-based job scheduling with configurable concurrency
- **State Persistence** - Auto-save and recovery of jobs and state
- **Health Monitoring** - Real-time metrics and health checks
- **Error Recovery** - Automatic retries with exponential backoff
- **WebSocket Support** - Real-time job updates and progress tracking
- **Multi-Platform** - Support for Printify, Shopify, TikTok, Etsy, Instagram, Facebook
- **REST API** - Complete API for job management and monitoring
- **Docker Ready** - Production Dockerfile and docker-compose configurations

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    POD Engine API                        │
│  (Express REST API + WebSocket Server)                   │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                  POD Engine Core                         │
│  • Job Queue (Priority-based)                            │
│  • State Persistence                                     │
│  • Metrics & Monitoring                                  │
│  • Error Recovery & Retries                              │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                  Orchestrator                            │
│  • Pipeline Coordination                                 │
│  • Service Integration                                   │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────┴─────────┬─────────────┬───────────┐
        ▼                   ▼             ▼           ▼
  ┌──────────┐      ┌──────────┐   ┌──────────┐  ┌──────────┐
  │ ComfyUI  │      │  Claude  │   │ Printify │  │ Shopify  │
  │ (Images) │      │(Prompts) │   │  (POD)   │  │ (Store)  │
  └──────────┘      └──────────┘   └──────────┘  └──────────┘
```

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.10+
- ComfyUI installed (optional for testing without GPU)
- Anthropic API key

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
COMFYUI_URL=http://localhost:8188
```

### 3. Start the Engine

```bash
# Using startup script (recommended)
./start-pod-engine.sh

# Or with npm
npm run engine

# Development mode (auto-reload)
npm run engine:dev
```

### 4. Test the API

```bash
# Check health
curl http://localhost:3000/health

# Submit a test job
curl -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful mountain landscape",
    "productTypes": ["tshirt"],
    "autoPublish": false
  }'
```

## Usage

### Submit a Generation Job

```javascript
const response = await fetch('http://localhost:3000/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'A futuristic cityscape at sunset',
    productTypes: ['tshirt', 'hoodie'],
    autoPublish: true
  })
});

const { jobId, job } = await response.json();
console.log('Job submitted:', jobId);
```

### Monitor Job Progress

```javascript
// Poll for status
const checkJob = async (jobId) => {
  const response = await fetch(`http://localhost:3000/api/jobs/${jobId}`);
  const job = await response.json();

  console.log(`Status: ${job.status}, Progress: ${job.progress}%`);

  if (job.status === 'completed') {
    console.log('Result:', job.result);
  } else if (job.status === 'failed') {
    console.log('Error:', job.error);
  }
};

// Or use WebSocket for real-time updates
const socket = io('ws://localhost:3000');
socket.on('job:update', (job) => {
  console.log('Job updated:', job);
});
```

### Batch Generation

```javascript
const response = await fetch('http://localhost:3000/api/generate/batch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    items: [
      { theme: 'nature', style: 'minimalist', productTypes: ['tshirt'] },
      { theme: 'tech', style: 'futuristic', productTypes: ['hoodie'] },
      { theme: 'abstract', style: 'colorful', productTypes: ['tshirt', 'hoodie'] }
    ],
    priority: 'high'
  })
});

const { jobId } = await response.json();
```

## Configuration

### Queue Settings

```env
MAX_CONCURRENT_JOBS=2      # Number of parallel jobs
MAX_JOB_RETRIES=3          # Retry attempts on failure
RETRY_DELAY_MS=5000        # Delay between retries (ms)
JOB_TIMEOUT_MS=600000      # Job timeout (10 minutes)
```

### Persistence Settings

```env
ENABLE_PERSISTENCE=true
STATE_FILE_PATH=/data/pod-engine-state.json
AUTO_SAVE_STATE=true
SAVE_INTERVAL_MS=30000     # Save every 30 seconds
```

### Monitoring Settings

```env
ENABLE_MONITORING=true
METRICS_INTERVAL_MS=10000  # Update metrics every 10 seconds
```

### Platform Configuration

```env
ENABLED_PLATFORMS=printify,shopify,etsy
TSHIRT_PRICE=19.99
HOODIE_PRICE=34.99
```

## Docker Deployment

### Using Docker Compose

```bash
# Build and start
docker-compose -f docker-compose.pod-engine.yml up -d

# View logs
docker-compose -f docker-compose.pod-engine.yml logs -f

# Stop
docker-compose -f docker-compose.pod-engine.yml down
```

### Using Dockerfile

```bash
# Build
docker build -f Dockerfile.pod-engine -t pod-engine:latest .

# Run
docker run -d \
  -p 3000:3000 \
  -p 8188:8188 \
  -v pod-data:/data \
  -e ANTHROPIC_API_KEY=your-key \
  --gpus all \
  pod-engine:latest
```

## RunPod Deployment

### 1. Build and Push Image

```bash
# Build
docker build -f Dockerfile.pod-engine -t your-dockerhub/pod-engine:latest .

# Push
docker push your-dockerhub/pod-engine:latest
```

### 2. Deploy on RunPod

1. Go to RunPod.io
2. Create new pod
3. Select GPU (e.g., RTX A4000)
4. Use custom Docker image: `your-dockerhub/pod-engine:latest`
5. Expose ports: 3000, 8188
6. Set environment variables
7. Start pod

### 3. Access Your Engine

```bash
# Get pod URL from RunPod dashboard
POD_URL="https://your-pod-id.runpod.io"

# Test
curl $POD_URL/health
```

## API Reference

See [POD_ENGINE_API.md](./POD_ENGINE_API.md) for complete API documentation.

**Key Endpoints:**
- `GET /health` - Health check
- `GET /api/metrics` - Engine metrics
- `POST /api/generate` - Quick generation
- `POST /api/generate/batch` - Batch generation
- `GET /api/jobs` - List jobs
- `GET /api/jobs/:id` - Get job details
- `POST /api/jobs/:id/cancel` - Cancel job
- `POST /api/jobs/:id/retry` - Retry failed job

## Monitoring

### Health Checks

```bash
# Basic health
curl http://localhost:3000/health

# Detailed metrics
curl http://localhost:3000/api/metrics
```

### Metrics

The engine tracks:
- Total jobs processed
- Success/failure rates
- Average job completion time
- Current queue size
- System uptime

### Logs

```bash
# Engine logs (stdout)
npm run engine

# ComfyUI logs
tail -f /data/comfyui.log

# Docker logs
docker-compose logs -f pod-engine
```

## Job Lifecycle

```
┌─────────┐
│ Submit  │
│  Job    │
└────┬────┘
     │
     ▼
┌─────────┐     Queue Full?     ┌─────────┐
│ Pending ├────────Yes─────────►│ Waiting │
└────┬────┘                     └────┬────┘
     │                               │
     No                              │
     │                               │
     ▼◄──────────────────────────────┘
┌─────────┐
│ Running │
└────┬────┘
     │
     ├──Success──► ┌───────────┐
     │             │ Completed │
     │             └───────────┘
     │
     └──Failure──► ┌─────────┐
                   │ Retries │
                   │  Left?  │
                   └────┬────┘
                        │
                        ├─Yes─► (Back to Pending)
                        │
                        └─No──► ┌────────┐
                                │ Failed │
                                └────────┘
```

## Error Handling

The engine implements robust error handling:

1. **Automatic Retries** - Failed jobs retry with exponential backoff
2. **Job Timeout** - Long-running jobs are terminated automatically
3. **State Recovery** - Engine state is persisted and recovered on restart
4. **Graceful Shutdown** - Clean shutdown on SIGTERM/SIGINT

### Retry Strategy

```
Attempt 1: Immediate
Attempt 2: 5 seconds delay
Attempt 3: 10 seconds delay
Attempt 4: 15 seconds delay
...
```

## Performance Tuning

### Optimize Concurrency

Adjust based on your GPU and CPU:

```env
# For single GPU
MAX_CONCURRENT_JOBS=1

# For multiple GPUs or powerful hardware
MAX_CONCURRENT_JOBS=4
```

### Adjust Timeouts

```env
# For simple designs
JOB_TIMEOUT_MS=300000  # 5 minutes

# For complex generations
JOB_TIMEOUT_MS=1200000  # 20 minutes
```

### Persistence Tuning

```env
# High-frequency saves (more resilient, higher I/O)
SAVE_INTERVAL_MS=10000

# Low-frequency saves (better performance, less resilient)
SAVE_INTERVAL_MS=60000
```

## Troubleshooting

### Engine won't start

```bash
# Check if port is in use
lsof -i :3000

# Kill existing process
kill $(lsof -t -i:3000)
```

### ComfyUI connection issues

```bash
# Check ComfyUI status
curl http://localhost:8188/system_stats

# Restart ComfyUI
pkill -f comfyui
./start-pod-engine.sh
```

### Jobs stuck in pending

```bash
# Check current jobs
curl http://localhost:3000/api/jobs?status=running

# Check metrics
curl http://localhost:3000/api/metrics
```

### High failure rate

```bash
# Get failed jobs
curl http://localhost:3000/api/jobs?status=failed

# Check logs from a specific job
curl http://localhost:3000/api/jobs/{job-id}
```

## Development

### Project Structure

```
services/
  podEngine.ts         # Core engine implementation
pod-engine-api.ts      # REST API server
start-pod-engine.sh    # Startup script
Dockerfile.pod-engine  # Production Dockerfile
POD_ENGINE_API.md      # API documentation
POD_ENGINE_README.md   # This file
```

### Testing

```bash
# Install dependencies
npm install

# Start in development mode
npm run engine:dev

# Run test generation
curl -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "productTypes": ["tshirt"]}'
```

## Production Checklist

- [ ] Set strong API keys
- [ ] Configure HTTPS/SSL
- [ ] Set up monitoring (Datadog, New Relic, etc.)
- [ ] Configure backup for state files
- [ ] Set up log aggregation
- [ ] Configure alerts for failures
- [ ] Test disaster recovery
- [ ] Document runbooks
- [ ] Set up auto-scaling (if needed)
- [ ] Configure rate limiting

## Support

- **API Documentation**: [POD_ENGINE_API.md](./POD_ENGINE_API.md)
- **Main README**: [README.md](./README.md)
- **Issues**: Open an issue on GitHub

## License

See main project LICENSE file.

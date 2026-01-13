# Production POD Engine

Enterprise-grade Print-on-Demand automation engine with job queuing, worker pools, persistence, monitoring, and HTTP API.

## Features

### Core Capabilities
- **Job Queue System**: Priority-based queue with concurrent job processing
- **Worker Pool**: Horizontal scaling with multiple engine workers
- **Persistence Layer**: PostgreSQL support with in-memory fallback
- **Error Handling**: Automatic retry logic with exponential backoff
- **Monitoring**: Metrics collection, health checks, and alerting
- **HTTP API**: RESTful API for job submission and system control
- **Auto-restart**: Workers automatically restart on failure
- **Graceful Shutdown**: Proper cleanup and job completion

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     HTTP API Server                      │
│            (Job Submission & Monitoring)                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Worker Pool Manager                    │
│            (Load Balancing & Orchestration)             │
└────┬──────────┬──────────┬──────────┬──────────────────┘
     │          │          │          │
┌────▼────┐┌───▼────┐┌───▼────┐┌───▼────┐
│ Worker  ││ Worker ││ Worker ││ Worker │
│    1    ││    2   ││    3   ││    N   │
└────┬────┘└───┬────┘└───┬────┘└───┬────┘
     │          │          │          │
┌────▼──────────▼──────────▼──────────▼────┐
│            Job Queue (Priority)            │
└────────────────┬──────────────────────────┘
                 │
┌────────────────▼──────────────────────────┐
│          Database (PostgreSQL)             │
│    (Jobs, Images, Products, Metrics)      │
└───────────────────────────────────────────┘
                 │
┌────────────────▼──────────────────────────┐
│          Pod Orchestrator                  │
│  ComfyUI → Storage → Printify → Platforms │
└───────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Setup Configuration

Copy the example configuration:

```bash
cp production/config.example.json production/config.json
```

Edit `production/config.json` with your API keys and settings.

### 3. Setup Database (Optional)

For production, use PostgreSQL:

```bash
# Create database
createdb pod_engine

# Run schema
psql pod_engine < production/schema.sql
```

For development, the engine will use in-memory storage automatically.

### 4. Run Single Worker

```bash
npm run production:worker
```

### 5. Run Worker Pool with API

```bash
npm run production:api
```

The API server will start on `http://localhost:3000`

## Configuration

### Environment Variables

```bash
# Required
CLAUDE_API_KEY=sk-ant-...
COMFYUI_API_URL=http://127.0.0.1:8188

# Optional
PRINTIFY_API_KEY=your_key
PRINTIFY_SHOP_ID=your_shop_id
WORKER_COUNT=3
API_PORT=3000
DATABASE_URL=postgresql://...
CONFIG_PATH=/path/to/config.json
```

### Configuration File

See `config.example.json` for full configuration options:

- **orchestrator**: ComfyUI, Claude, storage, and platform integrations
- **engine**: Job processing settings (concurrency, timeouts, retries)
- **database**: Database connection settings
- **workerPool**: Worker pool settings (count, auto-restart)
- **api**: API server settings (port, auth, CORS)

## API Reference

### Submit Job

```bash
POST /jobs
Content-Type: application/json

{
  "theme": "Cyber Punk",
  "style": "Neon Art",
  "niche": "Gaming",
  "productTypes": ["tshirt", "hoodie"],
  "count": 2,
  "autoPublish": false,
  "priority": 10
}
```

Response:
```json
{
  "jobId": "job-uuid",
  "status": "accepted"
}
```

### Get Job Status

```bash
GET /jobs/:id
```

Response:
```json
{
  "job": {
    "id": "job-uuid",
    "status": "completed",
    "priority": 10,
    "request": {...},
    "result": {...},
    "created_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T00:05:00Z"
  },
  "images": [...],
  "products": [...],
  "logs": [...]
}
```

### Health Check

```bash
GET /health
```

Response:
```json
{
  "healthy": true,
  "workers": [
    {
      "id": "worker_0_...",
      "index": 0,
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

### Get Statistics

```bash
GET /stats
```

Response:
```json
{
  "totalWorkers": 3,
  "runningWorkers": 3,
  "errorWorkers": 0,
  "totalJobs": 15,
  "totalCompleted": 12,
  "totalFailed": 1,
  "workers": [...]
}
```

### Dashboard Data

```bash
GET /dashboard?hours=24
```

Response:
```json
{
  "overview": {
    "totalJobs": 15,
    "completedJobs": 12,
    "failedJobs": 1,
    "successRate": 80,
    "avgProcessingTime": 120000
  },
  "recent": {
    "jobs": [...],
    "alerts": [...],
    "metrics": {...}
  },
  "performance": {
    "jobDuration": {...},
    "imageGeneration": {...},
    "productCreation": {...}
  }
}
```

### Scale Worker Pool

```bash
POST /scale
Content-Type: application/json

{
  "workerCount": 5
}
```

### All API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check for all workers |
| GET | /stats | Get worker pool statistics |
| GET | /dashboard?hours=24 | Get dashboard data |
| POST | /jobs | Submit a new job |
| GET | /jobs/:id | Get job details |
| GET | /jobs?status=completed&limit=50 | List jobs |
| GET | /workers | List all workers |
| POST | /workers/:id/restart | Restart a worker |
| POST | /scale | Scale worker pool |
| GET | /metrics?name=job_duration&limit=100 | Get metrics |
| GET | /alerts | Get recent alerts |

## Monitoring

### Metrics

The engine collects metrics automatically:

- `jobs_submitted`: Number of jobs submitted
- `jobs_completed`: Number of jobs completed
- `jobs_failed`: Number of jobs failed
- `jobs_retried`: Number of job retries
- `job_duration`: Job execution time (histogram)
- `workers_running`: Number of running workers (gauge)
- `workers_error`: Number of workers in error state (gauge)

### Alerts

Alerts are triggered for:

- Worker failures
- Job failures
- No workers running
- High error rates
- System exceptions

### Health Checks

Health checks verify:

- Worker status
- Queue status
- Database connectivity
- Orchestrator connectivity (ComfyUI)

## Job Lifecycle

```
┌─────────┐
│ Pending │
└────┬────┘
     │
     │ Added to queue
     ▼
┌─────────┐
│  Queued │
└────┬────┘
     │
     │ Worker picks up job
     ▼
┌────────────┐
│ Processing │
└─────┬──────┘
      │
      ├─── Success ──┐
      │              ▼
      │         ┌───────────┐
      │         │ Completed │
      │         └───────────┘
      │
      └─── Failure ──┐
                     ▼
                ┌─────────┐    Retry attempts
                │ Retrying│────────────┐
                └────┬────┘            │
                     │                 │
                     │ Max retries     │
                     ▼                 │
                ┌────────┐             │
                │ Failed │◄────────────┘
                └────────┘
```

## Error Handling

### Automatic Retry

Jobs are automatically retried on failure:

- Default: 3 retry attempts
- Configurable retry delay (default: 60 seconds)
- Exponential backoff (optional)

### Worker Recovery

Workers automatically restart on failure:

- Auto-restart enabled by default
- Maximum 3 restart attempts
- 5-second delay between restarts
- Failed workers are marked for manual intervention

### Graceful Degradation

- Database failures fall back to in-memory storage
- API failures don't crash workers
- Individual worker failures don't affect pool

## Performance

### Benchmarks

On a 4-core machine with 3 workers:

- **Throughput**: 50-100 jobs/hour (depends on ComfyUI)
- **Latency**: 2-5 minutes per job (image generation + product creation)
- **Concurrency**: 15 concurrent jobs (3 workers × 5 jobs each)

### Optimization Tips

1. **Increase Workers**: Scale horizontally for more throughput
2. **Tune Concurrency**: Adjust `maxConcurrentJobs` per worker
3. **Database**: Use PostgreSQL for persistence and performance
4. **Caching**: Enable image deduplication in storage service
5. **ComfyUI**: Use faster models or GPU acceleration

## Production Deployment

### Docker (Recommended)

```dockerfile
FROM node:18

WORKDIR /app
COPY package*.json ./
RUN npm ci --production

COPY . .
RUN npm run build

ENV NODE_ENV=production
CMD ["npm", "run", "production:api"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pod-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pod-engine
  template:
    metadata:
      labels:
        app: pod-engine
    spec:
      containers:
      - name: pod-engine
        image: pod-engine:latest
        env:
        - name: CLAUDE_API_KEY
          valueFrom:
            secretKeyRef:
              name: pod-engine-secrets
              key: claude-api-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: pod-engine-secrets
              key: database-url
        ports:
        - containerPort: 3000
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Process Manager (PM2)

```json
{
  "apps": [{
    "name": "pod-engine",
    "script": "production/examples/worker-pool-api.ts",
    "instances": 1,
    "exec_mode": "cluster",
    "env": {
      "NODE_ENV": "production",
      "WORKER_COUNT": "3",
      "API_PORT": "3000"
    },
    "error_file": "logs/error.log",
    "out_file": "logs/output.log",
    "log_date_format": "YYYY-MM-DD HH:mm:ss Z"
  }]
}
```

## Troubleshooting

### Workers Not Starting

Check:
1. Database connection
2. ComfyUI availability
3. Configuration file validity
4. API keys and credentials

### Jobs Failing

Check:
1. ComfyUI logs
2. Job logs in database
3. API rate limits
4. Network connectivity

### High Memory Usage

Solutions:
1. Reduce `maxConcurrentJobs`
2. Enable database persistence
3. Clear job history periodically
4. Limit metric retention

### Performance Issues

Solutions:
1. Check ComfyUI performance
2. Monitor database query times
3. Review network latency
4. Scale worker count

## Development

### Run Tests

```bash
npm test
```

### Build

```bash
npm run build
```

### Lint

```bash
npm run lint
```

## License

See LICENSE file

## Support

For issues and questions:
- GitHub Issues: [github.com/ssiens-oss/ssiens-oss-static_pod](https://github.com/ssiens-oss/ssiens-oss-static_pod/issues)
- Documentation: See `/production` directory

## Credits

Built by the SSIENS team for enterprise POD automation.

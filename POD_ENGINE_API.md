# POD Engine API Documentation

Complete API reference for the Production POD Engine.

## Table of Contents

- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Job Types](#job-types)
- [WebSocket Events](#websocket-events)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Quick Start

### Start the POD Engine

```bash
# Using the startup script
./start-pod-engine.sh

# Or with npm
npm run engine

# Or with Docker
docker-compose -f docker-compose.pod-engine.yml up
```

### Check Health

```bash
curl http://localhost:3000/health
```

### Submit a Job

```bash
curl -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic cityscape at sunset",
    "productTypes": ["tshirt", "hoodie"],
    "autoPublish": true
  }'
```

---

## Authentication

Currently, the POD Engine API does not require authentication for local/development use. For production deployments, implement API key authentication or OAuth2.

---

## API Endpoints

### Health & Status

#### `GET /health`

Check the health status of the POD Engine and all services.

**Response:**
```json
{
  "status": "healthy",
  "uptime": 123456,
  "metrics": {
    "totalJobs": 10,
    "completedJobs": 8,
    "failedJobs": 1,
    "runningJobs": 1,
    "pendingJobs": 0,
    "averageJobTime": 45000,
    "successRate": 88.89,
    "uptime": 123456,
    "lastActivity": 1234567890
  },
  "services": {
    "comfyui": true,
    "printify": true,
    "shopify": true
  }
}
```

**Status Values:**
- `healthy` - All systems operational
- `degraded` - Some services unavailable but core functionality works
- `unhealthy` - Critical services down or high failure rate

---

#### `GET /api/info`

Get engine information and configuration.

**Response:**
```json
{
  "name": "POD Engine",
  "version": "1.0.0",
  "config": {
    "maxConcurrent": 2,
    "maxRetries": 3,
    "persistenceEnabled": true,
    "monitoringEnabled": true
  }
}
```

---

#### `GET /api/metrics`

Get current engine metrics.

**Response:**
```json
{
  "totalJobs": 10,
  "completedJobs": 8,
  "failedJobs": 1,
  "runningJobs": 1,
  "pendingJobs": 0,
  "averageJobTime": 45000,
  "successRate": 88.89,
  "uptime": 123456,
  "lastActivity": 1234567890
}
```

---

### Job Management

#### `POST /api/jobs`

Submit a new job to the queue.

**Request Body:**
```json
{
  "type": "generate",
  "request": {
    "prompt": "A beautiful landscape",
    "productTypes": ["tshirt"],
    "autoPublish": true
  },
  "priority": "normal",
  "maxRetries": 3
}
```

**Parameters:**
- `type` (required): Job type - `generate`, `batch`, or `custom`
- `request` (required): Job-specific request data
- `priority` (optional): `low`, `normal`, `high`, or `urgent` (default: `normal`)
- `maxRetries` (optional): Maximum retry attempts (default: from config)

**Response:**
```json
{
  "jobId": "job_1234567890_abc123",
  "job": {
    "id": "job_1234567890_abc123",
    "type": "generate",
    "status": "pending",
    "priority": "normal",
    "progress": 0,
    "createdAt": 1234567890,
    "retryCount": 0,
    "maxRetries": 3,
    "logs": []
  }
}
```

---

#### `GET /api/jobs`

Get all jobs or filter by status.

**Query Parameters:**
- `status` (optional): Filter by status - `pending`, `running`, `completed`, `failed`, or `cancelled`

**Response:**
```json
[
  {
    "id": "job_1234567890_abc123",
    "type": "generate",
    "status": "completed",
    "priority": "normal",
    "progress": 100,
    "createdAt": 1234567890,
    "startedAt": 1234567895,
    "completedAt": 1234567940,
    "result": { ... },
    "retryCount": 0,
    "maxRetries": 3,
    "logs": [...]
  }
]
```

---

#### `GET /api/jobs/:id`

Get a specific job by ID.

**Response:**
```json
{
  "id": "job_1234567890_abc123",
  "type": "generate",
  "status": "running",
  "priority": "normal",
  "progress": 45,
  "request": { ... },
  "createdAt": 1234567890,
  "startedAt": 1234567895,
  "retryCount": 0,
  "maxRetries": 3,
  "logs": [
    {
      "timestamp": 1234567890,
      "message": "Job started",
      "type": "INFO"
    }
  ]
}
```

---

#### `POST /api/jobs/:id/cancel`

Cancel a pending job.

**Response:**
```json
{
  "success": true
}
```

**Error Response:**
```json
{
  "error": "Cannot cancel job"
}
```

---

#### `POST /api/jobs/:id/retry`

Retry a failed job.

**Response:**
```json
{
  "success": true
}
```

---

#### `POST /api/jobs/cleanup`

Clear old completed/failed jobs.

**Request Body:**
```json
{
  "maxAge": 86400000
}
```

**Parameters:**
- `maxAge` (optional): Maximum age in milliseconds (default: 24 hours)

**Response:**
```json
{
  "cleared": 5
}
```

---

### Generation Endpoints

#### `POST /api/generate`

Quick generation endpoint (simplified interface).

**Request Body:**
```json
{
  "prompt": "A beautiful landscape",
  "theme": "nature",
  "style": "photorealistic",
  "niche": "outdoor",
  "productTypes": ["tshirt", "hoodie"],
  "count": 1,
  "autoPublish": true
}
```

**Parameters:**
- `prompt` (optional): Direct prompt for image generation
- `theme` (optional): Theme for AI-generated prompts
- `style` (optional): Style for AI-generated prompts
- `niche` (optional): Niche/category for products
- `productTypes` (required): Array of product types - `tshirt`, `hoodie`
- `count` (optional): Number of designs to generate (default: 1)
- `autoPublish` (optional): Auto-publish to platforms (default: true)

**Response:**
```json
{
  "jobId": "job_1234567890_abc123",
  "job": { ... }
}
```

---

#### `POST /api/generate/batch`

Generate multiple designs in a single batch job.

**Request Body:**
```json
{
  "items": [
    {
      "prompt": "Design 1",
      "productTypes": ["tshirt"]
    },
    {
      "prompt": "Design 2",
      "productTypes": ["hoodie"]
    }
  ],
  "priority": "high"
}
```

**Parameters:**
- `items` (required): Array of generation requests
- `priority` (optional): Job priority

**Response:**
```json
{
  "jobId": "job_1234567890_abc123",
  "job": { ... }
}
```

---

## Job Types

### Generate Job

Creates POD products from a single design.

**Request Format:**
```json
{
  "type": "generate",
  "request": {
    "prompt": "Design prompt",
    "productTypes": ["tshirt", "hoodie"],
    "autoPublish": true
  }
}
```

**Result Format:**
```json
{
  "success": true,
  "generatedImages": [
    {
      "id": "img_123",
      "url": "https://...",
      "prompt": "..."
    }
  ],
  "products": [
    {
      "platform": "printify",
      "productId": "prod_123",
      "url": "https://...",
      "type": "tshirt"
    }
  ],
  "errors": [],
  "totalTime": 45000
}
```

---

### Batch Job

Generates multiple designs in one job.

**Request Format:**
```json
{
  "type": "batch",
  "request": {
    "items": [
      { "prompt": "Design 1", "productTypes": ["tshirt"] },
      { "prompt": "Design 2", "productTypes": ["hoodie"] }
    ]
  }
}
```

**Result Format:**
```json
{
  "results": [
    { "success": true, ... },
    { "success": true, ... }
  ],
  "errors": [],
  "total": 2
}
```

---

## WebSocket Events

Connect to `ws://localhost:3000` to receive real-time updates.

### Events

#### `job:update`

Emitted when a job status changes.

```json
{
  "id": "job_123",
  "status": "running",
  "progress": 45
}
```

---

#### `job:progress`

Emitted when job progress updates (batch jobs).

```json
{
  "id": "job_123",
  "progress": 67
}
```

---

#### `metrics`

Emitted periodically with updated metrics.

```json
{
  "totalJobs": 10,
  "completedJobs": 8,
  "runningJobs": 1
}
```

---

#### `log`

Emitted for important log messages.

```json
{
  "message": "Job completed successfully",
  "type": "SUCCESS",
  "timestamp": 1234567890
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Resource created
- `400` - Bad request (invalid parameters)
- `404` - Resource not found
- `500` - Internal server error
- `503` - Service unavailable

---

## Examples

### Example 1: Simple Generation

```bash
# Submit job
RESPONSE=$(curl -s -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A majestic mountain landscape",
    "productTypes": ["tshirt"],
    "autoPublish": true
  }')

# Extract job ID
JOB_ID=$(echo $RESPONSE | jq -r '.jobId')

# Check job status
curl http://localhost:3000/api/jobs/$JOB_ID
```

---

### Example 2: Batch Generation

```bash
curl -X POST http://localhost:3000/api/generate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "theme": "nature",
        "style": "minimalist",
        "productTypes": ["tshirt"]
      },
      {
        "theme": "technology",
        "style": "futuristic",
        "productTypes": ["hoodie"]
      },
      {
        "theme": "abstract",
        "style": "colorful",
        "productTypes": ["tshirt", "hoodie"]
      }
    ],
    "priority": "high"
  }'
```

---

### Example 3: Monitor with WebSocket

```javascript
const socket = io('ws://localhost:3000');

socket.on('connect', () => {
  console.log('Connected to POD Engine');
});

socket.on('job:update', (job) => {
  console.log('Job update:', job.id, job.status);
});

socket.on('job:progress', (job) => {
  console.log('Progress:', job.id, job.progress + '%');
});

socket.on('metrics', (metrics) => {
  console.log('Metrics:', metrics);
});
```

---

### Example 4: Health Check Script

```bash
#!/bin/bash

HEALTH=$(curl -s http://localhost:3000/health)
STATUS=$(echo $HEALTH | jq -r '.status')

if [ "$STATUS" = "healthy" ]; then
  echo "✓ POD Engine is healthy"
  exit 0
else
  echo "✗ POD Engine is $STATUS"
  exit 1
fi
```

---

### Example 5: Job Cleanup

```bash
# Clear jobs older than 24 hours
curl -X POST http://localhost:3000/api/jobs/cleanup \
  -H "Content-Type: application/json" \
  -d '{
    "maxAge": 86400000
  }'
```

---

### Example 6: Retry Failed Jobs

```bash
# Get all failed jobs
FAILED_JOBS=$(curl -s http://localhost:3000/api/jobs?status=failed)

# Retry each failed job
echo $FAILED_JOBS | jq -r '.[].id' | while read JOB_ID; do
  echo "Retrying job: $JOB_ID"
  curl -X POST http://localhost:3000/api/jobs/$JOB_ID/retry
done
```

---

## Configuration

### Environment Variables

See `.env.example` for all configuration options.

Key settings:
- `PORT` - API server port (default: 3000)
- `MAX_CONCURRENT_JOBS` - Max parallel jobs (default: 2)
- `MAX_JOB_RETRIES` - Retry attempts (default: 3)
- `JOB_TIMEOUT_MS` - Job timeout (default: 600000)
- `ENABLE_PERSISTENCE` - Save state to disk (default: true)
- `ENABLED_PLATFORMS` - Active platforms (default: printify,shopify)

---

## Best Practices

1. **Job Priorities**: Use priorities to ensure important jobs run first
2. **Error Handling**: Always check job status and handle failures
3. **Cleanup**: Regularly clean old jobs to prevent storage bloat
4. **Monitoring**: Use WebSocket events for real-time updates
5. **Retries**: Configure appropriate retry counts for your use case
6. **Timeouts**: Adjust timeouts based on your ComfyUI performance

---

## Troubleshooting

### POD Engine won't start

```bash
# Check if port is in use
lsof -i :3000

# Check logs
tail -f /data/comfyui.log
```

### Jobs stuck in pending

```bash
# Check metrics
curl http://localhost:3000/api/metrics

# Check running jobs
curl http://localhost:3000/api/jobs?status=running
```

### High failure rate

```bash
# Check health
curl http://localhost:3000/health

# Review failed job logs
curl http://localhost:3000/api/jobs?status=failed
```

---

## Support

For issues and feature requests, please open an issue on GitHub.

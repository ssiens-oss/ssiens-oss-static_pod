# RunPod Serverless Deployment Guide

Deploy the POD Pipeline as a RunPod Serverless Endpoint for maximum cost efficiency and automatic scaling.

## What is RunPod Serverless?

RunPod Serverless is a Function-as-a-Service (FaaS) platform that:
- **Auto-scales** from 0 to N workers based on demand
- **Pay per second** of execution time (not idle time)
- **Scales to zero** when not in use
- **90% cheaper** than continuous pods for intermittent workloads
- **Built-in queuing** and load balancing

## Quick Deployment

```bash
./deploy-serverless.sh
```

This script will:
1. Build the serverless Docker image
2. Push to Docker Hub (`staticwaves/staticwaves-pod-pipeline-serverless:latest`)
3. Create a RunPod serverless endpoint
4. Provide test commands

## Serverless Configuration

### Handler Function

The serverless endpoint uses `handler.py` which processes incoming requests:

```python
{
  "input": {
    "operation": "generate",
    "prompt": "Abstract geometric design",
    "style": "artistic",
    "product_type": "tshirt",
    "publish": false
  }
}
```

### Scaling Settings

Default configuration:
- **Min Workers**: 0 (scales to zero when idle)
- **Max Workers**: 3 (can handle 3 concurrent requests)
- **Scaler Type**: Queue Delay
- **Scaler Value**: 4 seconds (starts new worker if queue > 4s)
- **GPU**: NVIDIA A100 or RTX A4000

## Using Your Serverless Endpoint

### 1. Get Your Endpoint ID

After deployment:
1. Go to https://runpod.io/console/serverless
2. Find endpoint: `staticwaves-pod-pipeline-serverless`
3. Copy the Endpoint ID (e.g., `abc123def456`)

### 2. Health Check

```bash
curl -X POST https://api.runpod.ai/v2/<ENDPOINT_ID>/runsync \
  -H "Authorization: Bearer rpa_ZLK5MWU94JE5RJLBF7J0GFTKXY6LHPPPJJGRTI0X1q8bte" \
  -H "Content-Type: application/json" \
  -d '{"input": {"operation": "health"}}'
```

Expected response:
```json
{
  "status": "COMPLETED",
  "output": {
    "status": "healthy",
    "comfyui_running": true
  }
}
```

### 3. Generate a Design

```bash
curl -X POST https://api.runpod.ai/v2/<ENDPOINT_ID>/runsync \
  -H "Authorization: Bearer rpa_ZLK5MWU94JE5RJLBF7J0GFTKXY6LHPPPJJGRTI0X1q8bte" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "operation": "generate",
      "prompt": "Minimalist mountain landscape with geometric shapes",
      "style": "artistic",
      "product_type": "tshirt",
      "publish": false
    }
  }'
```

### 4. Async Requests (Recommended for Long Operations)

For design generation that takes >30 seconds, use async mode:

```bash
# Submit job
RESPONSE=$(curl -X POST https://api.runpod.ai/v2/<ENDPOINT_ID>/run \
  -H "Authorization: Bearer rpa_ZLK5MWU94JE5RJLBF7J0GFTKXY6LHPPPJJGRTI0X1q8bte" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "operation": "generate",
      "prompt": "Abstract art",
      "style": "bold",
      "product_type": "hoodie"
    }
  }')

JOB_ID=$(echo $RESPONSE | jq -r '.id')

# Check status
curl https://api.runpod.ai/v2/<ENDPOINT_ID>/status/$JOB_ID \
  -H "Authorization: Bearer rpa_ZLK5MWU94JE5RJLBF7J0GFTKXY6LHPPPJJGRTI0X1q8bte"
```

## Request Modes

### Synchronous (`/runsync`)
- Waits for completion (max 30 seconds)
- Returns result immediately
- Good for: Health checks, quick operations

### Asynchronous (`/run`)
- Returns immediately with job ID
- Poll for status
- Good for: Design generation, batch processing

### Stream (`/stream`)
- Real-time updates
- WebSocket connection
- Good for: Progress tracking, live updates

## Cost Estimation

Example pricing (RTX A4000):
- **Compute**: $0.00038/second
- **Idle**: Free (scales to zero)

Monthly cost examples:

**100 designs/month** (5 min each):
- Total compute: 500 minutes = 30,000 seconds
- Cost: 30,000 × $0.00038 = **$11.40/month**

**1000 designs/month**:
- Total compute: 5,000 minutes = 300,000 seconds
- Cost: 300,000 × $0.00038 = **$114/month**

Compare to continuous pod: $0.40/hour × 730 hours = **$292/month** (always running)

**Savings: 60-90%** depending on usage pattern

## Advanced Configuration

### Custom Scaling

Edit `deploy-serverless.sh` to customize:

```javascript
{
  "workersMin": 1,        // Keep 1 worker warm (faster cold starts)
  "workersMax": 5,        // Handle more concurrent requests
  "scalerType": "REQUEST_COUNT",
  "scalerValue": 2        // Start new worker per 2 requests
}
```

### GPU Selection

Available GPUs:
- `AMPERE_16` - A100 (fastest, most expensive)
- `AMPERE_8` - A40/A6000 (good balance)
- `ADA_24` - RTX 4090 (great price/performance)

### Environment Variables

Add to deployment mutation:

```javascript
{
  "env": [
    {"key": "ANTHROPIC_API_KEY", "value": "sk-ant-..."},
    {"key": "PRINTIFY_API_KEY", "value": "..."},
    {"key": "AUTO_PUBLISH", "value": "true"}
  ]
}
```

### Network Volumes (Persistent Storage)

For model caching and persistent data:

1. Create network volume at https://runpod.io/console/user/network-volumes
2. Note the volume ID
3. Update deployment:

```javascript
{
  "networkVolumeId": "abc123def456"
}
```

## Monitoring

### RunPod Console

View metrics at https://runpod.io/console/serverless:
- Request count
- Execution time
- Error rate
- Worker utilization
- Cost tracking

### Logs

View real-time logs:
```bash
# In RunPod console
1. Go to Serverless > Your Endpoint
2. Click "Logs" tab
3. Select worker to view logs
```

### Metrics API

Get endpoint metrics:
```bash
curl https://api.runpod.ai/v2/<ENDPOINT_ID>/metrics \
  -H "Authorization: Bearer rpa_ZLK5MWU94JE5RJLBF7J0GFTKXY6LHPPPJJGRTI0X1q8bte"
```

## Troubleshooting

### Cold Start Delays

First request after idle may take 30-60 seconds to start a worker.

**Solutions**:
- Set `workersMin: 1` to keep one worker warm
- Use `/run` (async) instead of `/runsync` for long operations
- Implement warming pings every 5 minutes

### Timeout Errors

If requests timeout:
- Use async mode (`/run`) for operations >30s
- Increase worker GPU tier for faster processing
- Optimize ComfyUI workflow

### Out of Memory

If workers crash:
- Increase GPU tier (more VRAM)
- Reduce batch size
- Clear ComfyUI cache between requests

### Rate Limits

RunPod limits:
- 100 concurrent requests per endpoint
- 10,000 requests per minute

For higher limits, contact RunPod support.

## Integration Examples

### Python SDK

```python
import runpod

runpod.api_key = "rpa_ZLK5MWU94JE5RJLBF7J0GFTKXY6LHPPPJJGRTI0X1q8bte"
endpoint = runpod.Endpoint("ENDPOINT_ID")

# Synchronous
result = endpoint.run_sync({
    "operation": "generate",
    "prompt": "Mountain landscape",
    "style": "minimal"
})

# Asynchronous
job = endpoint.run({
    "operation": "generate",
    "prompt": "Abstract art"
})

# Check status
status = endpoint.status(job.id)
```

### Node.js

```javascript
const fetch = require('node-fetch');

const endpoint = 'https://api.runpod.ai/v2/<ENDPOINT_ID>';
const apiKey = 'rpa_ZLK5MWU94JE5RJLBF7J0GFTKXY6LHPPPJJGRTI0X1q8bte';

async function generateDesign(prompt) {
  const response = await fetch(`${endpoint}/runsync`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      input: {
        operation: 'generate',
        prompt,
        style: 'artistic',
        product_type: 'tshirt'
      }
    })
  });

  return await response.json();
}
```

## Updating Your Endpoint

To deploy updates:

```bash
# 1. Make changes to handler.py or Dockerfile.serverless
# 2. Re-run deployment
./deploy-serverless.sh

# 3. RunPod will automatically use the new image for new workers
```

## Comparison: Serverless vs Pods

| Feature | Serverless | Pods |
|---------|-----------|------|
| **Idle Cost** | $0 (scales to zero) | Full cost |
| **Cold Start** | 30-60 seconds | Instant (always on) |
| **Scaling** | Automatic (0-N) | Manual |
| **Best For** | Intermittent, burst | Continuous, predictable |
| **Queue** | Built-in | DIY |
| **Cost (light use)** | 60-90% cheaper | Higher baseline |

## Security Best Practices

1. **API Key Management**
   - Rotate keys regularly
   - Use environment variables
   - Never commit keys to git

2. **Input Validation**
   - Validate all inputs in handler
   - Sanitize prompts
   - Limit resource usage

3. **Access Control**
   - Use separate endpoints for dev/prod
   - Implement authentication layer
   - Monitor for abuse

## Next Steps

1. ✅ Deploy with `./deploy-serverless.sh`
2. ✅ Get endpoint ID from RunPod console
3. ✅ Test with health check
4. ✅ Generate first design
5. ✅ Integrate into your application
6. ✅ Monitor costs and performance
7. ✅ Scale as needed

---

**Documentation**: See also `PRODUCTION_DEPLOYMENT.md` for pod-based deployment
**Support**: https://docs.runpod.io/serverless/overview

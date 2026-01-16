# RunPod Serverless ComfyUI Setup Guide

This guide will help you set up and configure RunPod Serverless ComfyUI for production image generation.

## Overview

The system automatically switches between local ComfyUI and RunPod Serverless based on environment variables:

- **Local ComfyUI**: Used for development when RunPod credentials are not configured
- **RunPod Serverless**: Used for production when API key and endpoint ID are provided

## Prerequisites

1. A RunPod account ([signup here](https://runpod.io))
2. A deployed RunPod Serverless ComfyUI endpoint
3. RunPod API key

## Step 1: Deploy RunPod Serverless ComfyUI Endpoint

### Option A: Use Existing ComfyUI Template

1. Log in to [RunPod](https://runpod.io)
2. Navigate to **Serverless** → **Endpoints**
3. Click **+ New Endpoint**
4. Search for "ComfyUI" in the template gallery
5. Select a ComfyUI template (recommended: latest SDXL template)
6. Configure:
   - **GPU Type**: A4000, A5000, or RTX 4090 (recommended for SDXL)
   - **Max Workers**: 1-5 (based on your needs)
   - **Idle Timeout**: 5 seconds
   - **Max Execution Time**: 600 seconds (10 minutes)
7. Click **Deploy**

### Option B: Custom Docker Image

If you need a custom ComfyUI setup:

```dockerfile
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel

# Install ComfyUI
WORKDIR /app
RUN git clone https://github.com/comfyanonymous/ComfyUI.git
WORKDIR /app/ComfyUI
RUN pip install -r requirements.txt

# Download models (SDXL base)
RUN mkdir -p models/checkpoints
RUN wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors \
    -O models/checkpoints/sd_xl_base_1.0.safetensors

# RunPod handler
COPY handler.py /app/handler.py

CMD python -u /app/handler.py
```

## Step 2: Get Your API Credentials

### Get Your API Key

1. Go to [RunPod Settings](https://runpod.io/console/user/settings)
2. Navigate to **API Keys**
3. Click **+ API Key**
4. Name it (e.g., "StaticWaves POD")
5. Copy the generated key (starts with `runpod_api_`)

### Get Your Endpoint ID

1. Go to **Serverless** → **Endpoints**
2. Click on your ComfyUI endpoint
3. Copy the **Endpoint ID** from the URL or endpoint details
   - Format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

## Step 3: Configure Environment Variables

Add these to your `.env` file:

```bash
# RunPod Serverless ComfyUI (Production)
RUNPOD_API_KEY=runpod_api_xxxxxxxxxxxxxxxxxxxxxxxxxx
RUNPOD_ENDPOINT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# For Vite frontend access
VITE_RUNPOD_API_KEY=runpod_api_xxxxxxxxxxxxxxxxxxxxxxxxxx
VITE_RUNPOD_ENDPOINT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Security Note**: Never commit your `.env` file to version control!

## Step 4: Verify Setup

### Test Health Check

```typescript
import { imageGenService } from './services/imageGeneration';

const isHealthy = await imageGenService.healthCheck();
console.log('Service Type:', imageGenService.getServiceType());
console.log('Health:', isHealthy ? 'OK' : 'Failed');
```

### Test Image Generation

```typescript
import { imageGenService } from './services/imageGeneration';

const result = await imageGenService.generate({
  prompt: 'a beautiful sunset over mountains, digital art',
  width: 1024,
  height: 1024,
  steps: 20,
  cfg_scale: 7
});

console.log('Generated images:', result.images);
```

## Architecture

### Automatic Service Selection

The `ImageGenerationService` automatically detects which backend to use:

```typescript
// Checks for RunPod credentials
if (RUNPOD_API_KEY && RUNPOD_ENDPOINT_ID) {
  // Use RunPod Serverless
} else {
  // Fall back to local ComfyUI
}
```

### API Endpoints

**RunPod Serverless API**:
- Base URL: `https://api.runpod.ai/v2/{ENDPOINT_ID}`
- `/run` - Async job submission
- `/runsync` - Synchronous execution (waits for result)
- `/status/{job_id}` - Check job status
- `/cancel/{job_id}` - Cancel running job

## Usage Examples

### Single Image Generation

```typescript
import { imageGenService } from './services/imageGeneration';

const result = await imageGenService.generate({
  prompt: 'cyberpunk city at night, neon lights, 4k',
  width: 1024,
  height: 1024,
  steps: 25,
  cfg_scale: 7.5,
  seed: 12345 // Optional: for reproducible results
});

if (result.status === 'completed') {
  console.log('Images:', result.images);
} else {
  console.error('Error:', result.error);
}
```

### Batch Generation

```typescript
const configs = [
  { prompt: 'mountain landscape' },
  { prompt: 'ocean sunset' },
  { prompt: 'forest path' }
];

const results = await imageGenService.generateBatch(configs);
results.forEach((result, i) => {
  if (result.status === 'completed') {
    console.log(`Batch ${i}:`, result.images);
  }
});
```

## Cost Optimization

### RunPod Pricing Tips

1. **Use Spot Instances**: 50-80% cheaper than on-demand
2. **Set Proper Timeouts**:
   - Idle timeout: 5 seconds (wake up quickly, shut down fast)
   - Max execution: 600 seconds (enough for complex workflows)
3. **Right-size GPU**:
   - SDXL: A4000 (cheapest) or RTX 4090 (fastest)
   - SD 1.5: RTX 3090 or cheaper
4. **Scale Workers**: Start with 1-2, increase based on demand
5. **Monitor Usage**: Check RunPod dashboard for actual costs

### Expected Costs (Approximate)

- **RTX A4000**: ~$0.00045/second (~$0.027/minute)
- **RTX 4090**: ~$0.00079/second (~$0.047/minute)
- **Typical SDXL generation**: 15-30 seconds
- **Cost per image**: $0.007 - $0.024

## Workflow Customization

### Modify Workflow JSON

Edit `services/runpod.ts` → `buildWorkflow()` to customize:

```typescript
private buildWorkflow(workflow: RunPodWorkflow): any {
  return {
    // Add your custom ComfyUI nodes here
    "1": { ... },
    "2": { ... },
    // ...
  };
}
```

### Use Custom Models

Update the checkpoint name in the workflow:

```typescript
"4": {
  "inputs": {
    "ckpt_name": "your_custom_model.safetensors"
  },
  "class_type": "CheckpointLoaderSimple"
}
```

Make sure the model is installed in your RunPod endpoint!

## Troubleshooting

### Issue: "RunPod API error (401)"
**Solution**: Check your API key is correct and active

### Issue: "RunPod API error (404)"
**Solution**: Verify your endpoint ID is correct

### Issue: Generation timeout
**Solution**:
- Increase timeout in `.env`: `RUNPOD_TIMEOUT=900000` (15 minutes)
- Check endpoint has available workers
- Verify GPU type supports your workflow

### Issue: Images not returning
**Solution**:
- Check your RunPod handler returns images in correct format
- Verify SaveImage node is in your workflow
- Check RunPod logs for errors

### Debug Mode

Enable verbose logging:

```typescript
// In services/runpod.ts
console.log('[RunPod] Request:', JSON.stringify(requestBody, null, 2));
console.log('[RunPod] Response:', JSON.stringify(responseData, null, 2));
```

## Migration from Local to RunPod

### Zero-Code Migration

Simply set the environment variables - no code changes needed!

```bash
# Before (Local)
COMFYUI_API_URL=http://localhost:8188

# After (RunPod)
RUNPOD_API_KEY=runpod_api_xxx
RUNPOD_ENDPOINT_ID=xxx-xxx-xxx
# System automatically switches!
```

### Feature Comparison

| Feature | Local ComfyUI | RunPod Serverless |
|---------|---------------|-------------------|
| WebSocket Updates | ✅ Yes | ❌ No (polling only) |
| Queue Status | ✅ Yes | ❌ No |
| Batch Processing | ✅ Yes | ✅ Yes |
| Auto-scaling | ❌ No | ✅ Yes |
| Zero Infrastructure | ❌ No | ✅ Yes |
| Cost | Free (your GPU) | Pay per use |

## Production Checklist

- [ ] RunPod endpoint deployed and tested
- [ ] API credentials added to `.env`
- [ ] Environment variables set in production deployment
- [ ] Health check passing
- [ ] Test image generation successful
- [ ] Costs monitored and acceptable
- [ ] Error handling tested
- [ ] Timeout values configured appropriately

## Support

- **RunPod Docs**: https://docs.runpod.io/
- **ComfyUI Docs**: https://github.com/comfyanonymous/ComfyUI
- **Issues**: Create an issue in this repository

## Next Steps

1. ✅ Set up RunPod endpoint
2. ✅ Configure environment variables
3. ✅ Test integration
4. 🚀 Deploy to production
5. 📊 Monitor usage and costs

---

**Ready to generate images at scale! 🎨**

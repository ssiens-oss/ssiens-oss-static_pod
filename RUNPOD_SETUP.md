# RunPod Serverless Configuration

This document explains how to configure the POD Gateway to work with RunPod serverless endpoints.

## Quick Setup

### 1. Update your `.env` file

Add your RunPod serverless credentials:

```bash
# ComfyUI Configuration - Use RunPod serverless endpoint
COMFYUI_API_URL=https://api.runpod.ai/v2/{your-endpoint-id}/runsync

# RunPod Specific
RUNPOD_POD_ID={your-endpoint-id}
RUNPOD_API_KEY={your-runpod-api-key}
```

### 2. Restart the Gateway

```bash
# If running via systemd:
sudo systemctl restart pod-gateway

# If running manually:
cd gateway
python app/main.py
```

### 3. Verify It's Working

Check the logs for:
```
✓ RunPod serverless client initialized
```

When you generate an image, you should see:
```
INFO - Using RunPod Serverless for generation: ...
INFO - Calling RunPod serverless: https://api.runpod.ai/v2/{endpoint-id}/runsync
INFO - ✓ RunPod job completed successfully
```

## How It Works

The gateway automatically detects RunPod serverless endpoints by checking if the URL contains:
- `api.runpod.ai` OR
- `runsync` in the path

When detected, it uses `gateway/app/runpod_adapter.py` to wrap workflows in the correct format:

```json
{
  "input": {
    "workflow": {...},
    "client_id": "pod-gateway-xxxxx"
  }
}
```

## Switching Between Direct ComfyUI and Serverless

### Direct ComfyUI (Local or Pod):
```bash
COMFYUI_API_URL=http://localhost:8188
# or
COMFYUI_API_URL=https://your-pod-id-8188.proxy.runpod.net
```

### RunPod Serverless:
```bash
COMFYUI_API_URL=https://api.runpod.ai/v2/{endpoint_id}/runsync
RUNPOD_API_KEY=your-runpod-api-key
```

The gateway will automatically use the right client based on the URL format.

## Troubleshooting

### Error: "Missing 'workflow' parameter"

This means the RunPod adapter wasn't loaded. Check:
1. `gateway/app/runpod_adapter.py` exists
2. `.env` has `RUNPOD_API_KEY` set
3. Gateway was restarted after updating config

### Error: "RUNPOD_API_KEY is required"

Your `COMFYUI_API_URL` is a serverless endpoint but no API key is set. Add:
```bash
RUNPOD_API_KEY=your-key-here
```

### Want to use direct connection instead?

Change your `.env` to use the pod URL directly:
```bash
COMFYUI_API_URL=https://tju27lse1t35la-8188.proxy.runpod.net
```

No API key needed for direct connections!

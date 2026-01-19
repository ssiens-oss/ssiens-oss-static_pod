# RunPod Serverless ComfyUI Setup Guide

## Overview

RunPod Serverless is perfect for POD workflows:
- ✅ Pay only per generation ($0.01-0.05 per image)
- ✅ No GPU setup or maintenance
- ✅ Fast generation with high-end GPUs
- ✅ Auto-scaling and zero cold starts
- ✅ Pre-configured with models

---

## Step 1: Create RunPod Serverless Endpoint

### 1.1 Go to RunPod Serverless Console
Visit: https://www.runpod.io/console/serverless

### 1.2 Create New Endpoint
1. Click **"+ New Endpoint"**
2. Choose **"ComfyUI"** template (or search for it)
3. Configure:
   - **Name**: `pod-comfyui-serverless`
   - **GPU Type**: Select based on budget
     - RTX 4090 (Recommended): Fast, $0.0004/sec (~$0.02 per image)
     - RTX 3090: Good balance, $0.0003/sec (~$0.015 per image)
     - A100: Fastest, $0.0010/sec (~$0.05 per image)
   - **Max Workers**: 3 (adjust based on needs)
   - **Idle Timeout**: 5 seconds (to save costs)
   - **GPUs/Worker**: 1

4. Click **"Deploy"**

### 1.3 Get Your Endpoint Details
After deployment, you'll see:
- **Endpoint ID**: `abc123def456` (example)
- **Endpoint URL**: `https://api.runpod.ai/v2/abc123def456/runsync`
- **API Key**: Use your existing RunPod API key

---

## Step 2: Configure Your Gateway

### 2.1 Update .env File

```bash
cd ~/ssiens-oss-static_pod

# Edit .env
nano .env
```

Update these lines:

```bash
# RunPod Serverless Configuration
RUNPOD_ENDPOINT_ID=abc123def456  # Your endpoint ID from Step 1.3
RUNPOD_API_KEY=rpa_YOUR_API_KEY_HERE  # Your RunPod API key from dashboard

# ComfyUI URL (Serverless format)
COMFYUI_API_URL=https://api.runpod.ai/v2/abc123def456/runsync
```

### 2.2 Quick Command to Update

```bash
cd ~/ssiens-oss-static_pod

# Replace with YOUR endpoint ID
ENDPOINT_ID="your-endpoint-id-here"

# Update .env
cat >> .env << EOF

# RunPod Serverless
RUNPOD_ENDPOINT_ID=${ENDPOINT_ID}
COMFYUI_API_URL=https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync
EOF

echo "✅ Updated .env with serverless endpoint"
```

---

## Step 3: Test the Connection

### 3.1 Test RunPod Serverless Endpoint

```bash
# Test with your actual endpoint ID and API key
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync" \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "workflow": {
        "prompt": "a beautiful mountain landscape"
      }
    }
  }'
```

If successful, you'll get a JSON response with generation status.

### 3.2 Start Your Gateway

```bash
cd ~/ssiens-oss-static_pod/gateway
python app/main.py
```

### 3.3 Test Image Generation

Open browser to: http://localhost:5000

Try generating an image - it should now use RunPod Serverless!

---

## Step 4: Optimize for Serverless

### 4.1 Serverless-Specific Settings

RunPod Serverless works slightly differently. Create a serverless adapter:

```bash
cd ~/ssiens-oss-static_pod
mkdir -p gateway/app/adapters
```

### 4.2 Request Format

RunPod Serverless uses this request format:

```json
{
  "input": {
    "workflow": {
      "prompt": "your prompt here",
      "width": 1536,
      "height": 1536,
      "steps": 35,
      "cfg_scale": 7.5,
      "sampler_name": "dpmpp_2m",
      "scheduler": "karras"
    }
  }
}
```

---

## Pricing Breakdown

### Example Costs (1536x1536, 35 steps):

| GPU Type | Time/Image | Cost/Image | Cost/100 Images |
|----------|-----------|------------|-----------------|
| RTX 3090 | ~30 sec   | $0.012     | $1.20          |
| RTX 4090 | ~20 sec   | $0.008     | $0.80          |
| A100     | ~15 sec   | $0.015     | $1.50          |

**Idle time**: $0 (serverless scales to zero)

---

## Advantages of Serverless

1. **No Setup**: Pre-configured, works immediately
2. **Cost Efficient**: Pay only for generation time
3. **Scalable**: Handles multiple generations simultaneously
4. **Maintenance Free**: No updates, no CUDA issues
5. **Fast**: High-end GPUs always available
6. **Global**: Low latency worldwide

---

## Monitoring

### Check Endpoint Status

```bash
curl -X GET "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/status" \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY"
```

### View Logs

In RunPod Console:
1. Go to Serverless → Your Endpoint
2. Click "Logs" tab
3. View real-time generation logs

### Monitor Costs

In RunPod Console:
1. Go to "Billing"
2. View serverless usage
3. Set spending limits if needed

---

## Troubleshooting

### Issue: "Endpoint not found"
**Solution**: Check your endpoint ID is correct in .env

### Issue: "Authentication failed"
**Solution**: Verify your RUNPOD_API_KEY in .env

### Issue: "Cold start delay"
**Solution**: First request takes 10-30 seconds to start worker. Subsequent requests are fast.

### Issue: "Timeout"
**Solution**: Increase timeout in your gateway config to 120+ seconds

---

## Alternative: Pre-built Serverless Templates

RunPod offers pre-configured templates:

1. **ComfyUI Official**:
   - Endpoint: Search "ComfyUI" in marketplace
   - Pre-loaded with SDXL models

2. **Stable Diffusion XL**:
   - Endpoint: Search "SDXL" in marketplace
   - Optimized for SDXL generation

3. **Custom Template**:
   - Upload your own ComfyUI workflow
   - Configure custom nodes

---

## Summary

**Setup Steps**:
1. ✅ Create RunPod Serverless endpoint
2. ✅ Get endpoint ID
3. ✅ Update .env with endpoint URL
4. ✅ Restart gateway
5. ✅ Test generation

**Expected Results**:
- Fast generation (15-30 seconds)
- High quality images (1536x1536)
- Pay per use (~$0.01 per image)
- Zero maintenance

---

## Next Steps

After setup:
1. Generate test images
2. Monitor costs in dashboard
3. Adjust worker count based on usage
4. Set up billing alerts

**You're ready for production POD workflow!** 🚀

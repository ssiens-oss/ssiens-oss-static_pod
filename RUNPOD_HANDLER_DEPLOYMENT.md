# RunPod Serverless Handler Deployment

Your RunPod endpoint is working but needs a handler to return generated images.

## 🔍 Current Issue

✅ Endpoint healthy
✅ Jobs completing (52ms execution time)
⚠️ **No image output** - handler not configured

## 📋 Solution

Deploy the custom handler (`runpod-handler.py`) to your RunPod Serverless endpoint.

---

## 🚀 Quick Deployment

### Option 1: Use RunPod's Default ComfyUI Template

If your endpoint was created from RunPod's ComfyUI template, it should already have a handler. The issue might be with how we're sending the workflow.

**Try this**: Update your workflow to match the template's expected format.

### Option 2: Deploy Custom Handler

1. **Create a Docker image with the handler:**

```dockerfile
# Dockerfile.runpod-handler
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel

WORKDIR /app

# Install ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git
WORKDIR /app/ComfyUI
RUN pip install -r requirements.txt

# Download SDXL model
RUN mkdir -p models/checkpoints && \
    wget -q https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors \
    -O models/checkpoints/sd_xl_base_1.0.safetensors

# Install RunPod SDK
RUN pip install runpod requests

# Copy handler
WORKDIR /app
COPY runpod-handler.py /app/handler.py

# Start ComfyUI in background and run handler
CMD python /app/ComfyUI/main.py --listen 0.0.0.0 --port 8188 & \
    sleep 10 && \
    python /app/handler.py
```

2. **Build and push image:**

```bash
# Build image
docker build -f Dockerfile.runpod-handler -t YOUR_DOCKERHUB_USERNAME/comfyui-runpod-handler:latest .

# Push to Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/comfyui-runpod-handler:latest
```

3. **Update RunPod endpoint:**
   - Go to your endpoint settings
   - Update Docker image to: `YOUR_DOCKERHUB_USERNAME/comfyui-runpod-handler:latest`
   - Redeploy

---

## 🔧 Alternative: Check Existing Handler

Your endpoint might already have a handler with a different input format. Let's test:

### Test 1: Raw Prompt Format

Some handlers expect just a text prompt:

```bash
curl -X POST https://api.runpod.ai/v2/a0vhmyan1win34/run \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "a beautiful sunset over mountains"
    }
  }'
```

### Test 2: ComfyUI API Format

Some handlers use ComfyUI's native format:

```bash
curl -X POST https://api.runpod.ai/v2/a0vhmyan1win34/run \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "a beautiful sunset",
      "negative_prompt": "bad quality",
      "width": 512,
      "height": 512,
      "steps": 20
    }
  }'
```

### Test 3: Check Endpoint Docs

Check if your endpoint has API documentation:
```bash
curl https://api.runpod.ai/v2/a0vhmyan1win34/docs \
  -H "Authorization: Bearer $RUNPOD_API_KEY"
```

---

## 📝 Handler Code Explanation

The provided `runpod-handler.py` does:

1. **Receives** ComfyUI workflow via RunPod API
2. **Submits** to local ComfyUI instance (running on worker)
3. **Polls** for completion
4. **Extracts** generated images
5. **Converts** to base64 data URLs
6. **Returns** images in response

**Input format:**
```json
{
  "input": {
    "workflow": { ... ComfyUI workflow nodes ... }
  }
}
```

**Output format:**
```json
{
  "images": [
    "data:image/png;base64,iVBORw0KGgoAAAANS...",
    "data:image/png;base64,iVBORw0KGgoAAAANS..."
  ],
  "prompt_id": "abc123",
  "execution_time": 15
}
```

---

## 🎯 Recommended Next Steps

### Immediate (No Code Deploy):

1. **Contact RunPod Support** - Ask what input format your endpoint expects
2. **Check RunPod Dashboard** - Look for endpoint documentation or example requests
3. **Try template format** - If using RunPod's template, check their docs

### Long-term (Custom Solution):

1. Deploy custom handler with the provided `runpod-handler.py`
2. Update your endpoint to use the custom Docker image
3. Test with our integration

---

## 📞 Getting Help

**RunPod Discord**: https://discord.gg/runpod
**RunPod Docs**: https://docs.runpod.io/serverless/endpoints
**Template Source**: Check if your endpoint template has a GitHub repo

---

## ✅ Verification

After fixing the handler, run:

```bash
./test-runpod-diagnostic.sh
```

You should see:
```
Has 'output' field: 1
Output field content:
{
  "images": [...]
}
```

---

## 🔄 Current Workaround

While fixing the handler, you can use RunPod **Pods** (not Serverless) for immediate image generation:

1. Deploy a ComfyUI Pod (has web interface)
2. Set `COMFYUI_API_URL` to the pod's URL
3. Use local ComfyUI service (`services/comfyui.ts`)

**Pod URL format**: `https://xxxxx-8188.proxy.runpod.net`

---

Need help? The endpoint is running perfectly - just needs the output format configured! 🚀

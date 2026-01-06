# Deploy StaticWaves to RunPod 🚀

Your RunPod API key has been configured. Follow these steps to deploy.

## Prerequisites

- Docker installed on your local machine ([Install Docker](https://www.docker.com/get-started))
- Docker Hub account (free: [Sign up](https://hub.docker.com/signup))
- RunPod account with credits

## Quick Deploy (3 steps)

### Step 1: Run on Your Local Machine

**Important:** This script must run on a machine with Docker installed, not on RunPod.

```bash
# Make sure you're in the project directory
cd ssiens-oss-static_pod

# Run the deployment script
./deploy-docker-runpod.sh
```

### Step 2: Script Will:

1. ✅ Build Docker image (includes ComfyUI + Node.js + all dependencies)
2. ✅ Push to Docker Hub (you'll need to login when prompted)
3. ✅ Deploy to RunPod using your API key
4. ✅ Configure GPU instance (RTX A4000, 16GB RAM, 50GB storage)

### Step 3: Access Your App

After deployment completes:

1. Go to https://www.runpod.io/console/pods
2. Find pod named: **staticwaves-pod-studio**
3. Click **Connect** → Copy the public URL
4. Access GUI at: `https://<pod-id>-5173.proxy.runpod.net`

---

## What Gets Deployed

**Container includes:**
- ✅ Ubuntu 22.04 + CUDA 12.1
- ✅ Node.js 20
- ✅ Python 3.10
- ✅ ComfyUI with SDXL support
- ✅ StaticWaves POD Studio (built React app)
- ✅ Nginx web server

**Ports exposed:**
- `5173` - Main GUI (Vite dev server)
- `8188` - ComfyUI API
- `80` - Nginx (production build)

**Resources:**
- GPU: NVIDIA RTX A4000
- vCPU: 4 cores
- RAM: 16GB
- Disk: 50GB container + 50GB volume
- Cost: ~$0.34/hour

---

## Customize Docker Username

If you want to use your own Docker Hub username:

```bash
DOCKER_USERNAME=yourusername ./deploy-docker-runpod.sh
```

---

## Alternative: Use Pre-built Image

If you don't want to build locally, you can use a pre-built image:

```bash
# Deploy using public image (if available)
curl -X POST "https://api.runpod.io/graphql?api_key=rpa_ZLK5MWU94JE5RJLBF7J0GFTKXY6LHPPPJJGRTI0X1q8bte" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { podFindAndDeployOnDemand(input: { cloudType: ALL, gpuCount: 1, volumeInGb: 50, containerDiskInGb: 50, minVcpuCount: 4, minMemoryInGb: 16, gpuTypeId: \"NVIDIA RTX A4000\", name: \"staticwaves-pod-studio\", imageName: \"staticwaves/pod-studio:latest\", ports: \"5173/http,8188/http\", volumeMountPath: \"/data\" }) { id } }"
  }'
```

---

## Troubleshooting

### "Docker command not found"
Install Docker: https://docs.docker.com/get-docker/

### "Permission denied"
```bash
chmod +x deploy-docker-runpod.sh
```

### "No available GPUs"
Try a different GPU or region in the script:
- Change `gpuTypeId` to: `NVIDIA RTX A5000` or `NVIDIA A40`
- Add `cloudType: SECURE` for dedicated instances

### "Insufficient credits"
Add credits to RunPod: https://www.runpod.io/console/user/billing

### Check pod status
```bash
curl -X POST "https://api.runpod.io/graphql?api_key=rpa_ZLK5MWU94JE5RJLBF7J0GFTKXY6LHPPPJJGRTI0X1q8bte" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { myself { pods { id name runtime { ports { privatePort publicPort } } } } }"}'
```

---

## After Deployment

Once your pod is running:

1. **Download SDXL Model** (if not included):
   ```bash
   # SSH into pod
   ssh root@<pod-ip> -p <ssh-port>

   # Download model
   cd /workspace/ComfyUI/models/checkpoints
   wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
   ```

2. **Configure API Keys**:
   - Add your Anthropic API key via the GUI
   - Configure Printify/Shopify credentials

3. **Start Creating**:
   - Open the GUI
   - Configure your drop settings
   - Hit "Run Single Drop" or "Run Batch Mode"

---

## Cost Estimate

**RunPod GPU Instance:**
- RTX A4000: $0.34/hour
- Running 24/7: ~$245/month
- On-demand usage: Only pay when pod is running

**AI Generation Costs:**
- Claude API: ~$0.01 per design
- ComfyUI: Free (runs on your GPU)

**Total per 100 designs:** ~$1.00 + GPU time

---

Need help? Check the main [README.md](README.md) or [SETUP_GUIDE.md](SETUP_GUIDE.md)

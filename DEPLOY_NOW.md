# 🚀 Deploy POD Engine to RunPod - Quick Guide

**Branch**: `claude/implement-pod-engine-IAaz2`
**Status**: Production Ready ✅

---

## 📋 Pre-Deployment Checklist

- ✅ All code committed and pushed
- ✅ Background removal integrated
- ✅ Mockup generation ready
- ✅ Transparent PNG pipeline configured
- ✅ .env template updated
- ✅ Startup script enhanced with dependencies

---

## 🎯 Deployment Steps

### 1. Launch RunPod Instance

**Recommended Template**: PyTorch (with CUDA support)
- **GPU**: A4000, A5000, or higher
- **Disk Space**: 50GB minimum
- **Region**: Any available

### 2. SSH to RunPod

```bash
ssh <your-runpod-ssh-connection>
# Example: ssh root@ssh.runpod.io -p 12345 -i ~/.ssh/id_ed25519
```

### 3. Clone Repository

```bash
cd /workspace
git clone -b claude/implement-pod-engine-IAaz2 \
  https://github.com/ssiens-oss/ssiens-oss-static_pod.git app

cd app
```

### 4. Configure Environment

```bash
# Copy and edit .env
cp .env.example .env
nano .env  # or vim .env
```

**Required settings**:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
PRINTIFY_API_KEY=your-printify-api-key
PRINTIFY_SHOP_ID=your-shop-id
```

**Already configured (no changes needed)**:
```bash
ENABLE_BACKGROUND_REMOVAL=true
ENABLE_MOCKUPS=true
STORAGE_PATH=/workspace/data/designs
MOCKUP_TEMPLATES_DIR=/workspace/data/mockup-templates
MOCKUP_OUTPUT_DIR=/workspace/data/mockups
```

### 5. Run Startup Script

```bash
chmod +x runpod-start.sh
./runpod-start.sh
```

**The script automatically**:
- ✅ Installs Node.js 20.x
- ✅ Installs/starts ComfyUI
- ✅ Downloads Stable Diffusion model
- ✅ Installs Python dependencies (torch, transformers, rembg, etc.)
- ✅ Creates mockup templates
- ✅ Starts POD Engine API
- ✅ Starts Monitoring GUI

**Wait time**: ~2-5 minutes for first-time setup

---

## ✅ Verify Deployment

### Check Services are Running

```bash
# Check all processes
ps aux | grep -E "ComfyUI|pod-engine" | grep -v grep

# Check API health
curl http://localhost:3000/health

# Check ComfyUI
curl http://localhost:8188
```

**Expected output**:
```json
{"status":"healthy","uptime":12345,"timestamp":"..."}
```

### Check Generated Files

```bash
# Verify mockup templates created
ls -lh /workspace/data/mockup-templates/

# Should see:
# tshirt_base.png
# hoodie_base.png
```

---

## 🎨 Submit First Production Job

### Via API

```bash
curl -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Urban street art design with vibrant geometric patterns",
    "productTypes": ["tshirt", "hoodie"],
    "priority": "high",
    "autoPublish": false
  }'
```

**Expected response**:
```json
{
  "jobId": "job_1234567890_xxxxx",
  "message": "Job submitted successfully",
  "status": "pending"
}
```

### Check Job Status

```bash
JOB_ID="job_1234567890_xxxxx"  # Use the ID from above
curl http://localhost:3000/api/jobs/$JOB_ID | jq .
```

---

## 🖥️ Access Monitoring GUI

### Option 1: SSH Port Forwarding

On your **local machine**:

```bash
ssh -L 3000:localhost:3000 \
    -L 8080:localhost:8080 \
    -L 8188:localhost:8188 \
    <your-runpod-ssh-connection>
```

Then access on your local browser:
- **Monitoring GUI**: http://localhost:8080/monitor.html
- **POD Engine API**: http://localhost:3000
- **ComfyUI**: http://localhost:8188

### Option 2: RunPod Web Interface

Check your RunPod dashboard for exposed ports and web URLs.

---

## 📊 Production Job Flow

When you submit a job, the pipeline automatically:

```
1. ComfyUI generates AI design (4096x4096)
   ↓
2. Save to /workspace/data/designs/img_xxx.png
   ↓
3. Remove background → img_xxx_transparent.png
   ↓
4. Generate mockups:
   - img_xxx_tshirt_mockup.png
   - img_xxx_hoodie_mockup.png
   ↓
5. Upload transparent PNG to Printify
   ↓
6. Create products (t-shirt + hoodie)
   ↓
7. Products ready with NO WHITE BACKGROUNDS!
```

---

## 📁 Output Files Structure

```
/workspace/data/
├── designs/
│   ├── img_1234567890_abc.png              # Original
│   └── img_1234567890_abc_transparent.png  # Transparent
├── mockups/
│   ├── img_1234567890_abc_tshirt_mockup.png
│   └── img_1234567890_abc_hoodie_mockup.png
└── mockup-templates/
    ├── tshirt_base.png
    └── hoodie_base.png
```

---

## 🔧 Troubleshooting

### Services not starting?

```bash
# Check logs
tail -f /workspace/logs/comfyui.log
tail -f /workspace/logs/pod-engine.log

# Restart services
pkill -f "ComfyUI|pod-engine"
./runpod-start.sh
```

### ComfyUI errors?

```bash
# Check Python packages
cd /workspace/ComfyUI
pip install -r requirements.txt
pip install tqdm torch torchsde transformers aiohttp
```

### Background removal not working?

```bash
# Install rembg
pip install "rembg[cpu]" pillow

# Test manually
python services/remove_bg.py test_input.png test_output.png
```

### Mockups not generating?

```bash
# Check templates exist
ls -lh /workspace/data/mockup-templates/

# Regenerate if needed
python services/create_mockup_templates.py

# Test manually
python services/mockup.py \
  /workspace/data/mockup-templates/tshirt_base.png \
  /workspace/data/designs/test.png \
  /workspace/data/mockups/test_mockup.png
```

---

## 🎯 Production Tips

### Replace Placeholder Templates

For professional mockups, replace the auto-generated templates:

```bash
# Download professional product photos
# Upload to /workspace/data/mockup-templates/

# Required files:
# - tshirt_base.png (1200x1400px min, PNG with transparency)
# - hoodie_base.png (1200x1500px min, PNG with transparency)
```

**Sources for templates**:
- Printify mockup downloads
- Placeit.net
- Smartmockups.com
- Printful mockup generator

### Monitor Resource Usage

```bash
# Check GPU usage
nvidia-smi

# Check disk space
df -h /workspace

# Check memory
free -h
```

### Enable Auto-Publish

Once you've tested and verified everything works:

```bash
# Edit .env
nano .env

# Change:
AUTO_PUBLISH=true

# Restart POD Engine
pkill -f pod-engine
npx tsx pod-engine-api.ts > /workspace/logs/pod-engine.log 2>&1 &
```

---

## 🚀 Scaling Production

### Batch Processing

Submit multiple jobs:

```bash
for i in {1..10}; do
  curl -X POST http://localhost:3000/api/generate \
    -H "Content-Type: application/json" \
    -d "{
      \"prompt\": \"Design variation $i\",
      \"productTypes\": [\"tshirt\", \"hoodie\"]
    }"
done
```

### Monitor Queue

```bash
# Get all jobs
curl http://localhost:3000/api/jobs | jq '.[] | {id, status, progress}'

# Get metrics
curl http://localhost:3000/api/metrics | jq .
```

---

## 📚 Documentation

- **Full Guide**: `MOCKUP_AND_TRANSPARENT_PNG_GUIDE.md`
- **Changelog**: `CHANGELOG_TRANSPARENT_MOCKUPS.md`
- **RunPod Guide**: `RUNPOD_COMPLETE_WALKTHROUGH.md`

---

## ✅ Deployment Complete!

Your POD Engine is now running with:
- ✅ AI image generation (ComfyUI + Stable Diffusion)
- ✅ Automatic background removal
- ✅ Transparent PNG generation
- ✅ Product mockup generation
- ✅ Printify integration
- ✅ Monitoring GUI

**Ready for production!** 🎉

---

## 🆘 Support

If you encounter issues:

1. Check logs: `/workspace/logs/`
2. Verify services: `ps aux | grep -E "ComfyUI|pod-engine"`
3. Test components individually (see Troubleshooting section)
4. Review documentation files

**Everything is automated - just run `./runpod-start.sh` and you're live!**

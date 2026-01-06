# ComfyUI Integration for StaticWaves POD

Complete automation pipeline for generating POD-ready designs using ComfyUI + SDXL.

## Quick Start (RunPod)

### 1. Install SDXL Models

```bash
# Download SDXL Base + Refiner (~13GB total)
./scripts/comfyui/install-sdxl.sh
```

### 2. Start ComfyUI

```bash
cd /workspace/ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188
```

### 3. Queue 50 Prompts

```bash
# Uses SDXL by default
./scripts/comfyui/queue-50-prompts.py
```

### 4. Auto-Resize for Printify (New Terminal)

```bash
# Install ImageMagick first
apt install -y imagemagick

# Start resize watcher
./scripts/comfyui/resize-for-printify.py
```

### 5. 🎨 **NEW: Gallery Proofing** (Review Before Publishing!)

```bash
# Start gallery server
./scripts/comfyui/gallery-server.py
```

Open in browser: `http://<pod-ip>:8080`

- ✅ Visual gallery of all generated designs
- ✅ Select which designs to publish
- ✅ Preview full-size images
- ✅ One-click publish to Printify

### 6. Auto-Publish to Printify (Alternative: Publish All)

```bash
# Set your API credentials
export PRINTIFY_API_TOKEN=your_token_here
export PRINTIFY_STORE_ID=your_store_id

# Publish ALL designs (skip gallery)
./scripts/comfyui/push-to-printify.py
```

---

## Scripts Overview

### 🎨 `gallery-server.py` **NEW!**

Web-based gallery for reviewing designs before publishing.

**Features:**
- Visual grid gallery of all designs
- Click to select/deselect designs
- Full-size preview modal
- Batch publish selected designs
- Real-time stats (total, selected, products)

**Usage:**
```bash
./scripts/comfyui/gallery-server.py

# Custom port
GALLERY_PORT=9000 ./scripts/comfyui/gallery-server.py
```

**Access:**
- Local: `http://localhost:8080`
- RunPod: `https://<pod-id>-8080.proxy.runpod.net`

**Keyboard Shortcuts:**
- `Ctrl+A` - Select all
- `Esc` - Close preview modal

---

### 📝 `queue-50-prompts.py`

Auto-queues 50 StaticWaves prompts (25 Cryptid + 25 Brain Rot) into ComfyUI.

**Features:**
- SDXL support (auto-detects model)
- Brand-locked prompts
- Randomized seeds
- Batch generation

**Usage:**
```bash
# Use SDXL (recommended)
COMFYUI_MODEL=sdxl_base_1.0.safetensors ./scripts/comfyui/queue-50-prompts.py

# Or SD 1.5 (fallback)
COMFYUI_MODEL=v1-5-pruned-emaonly.safetensors ./scripts/comfyui/queue-50-prompts.py
```

**Output:**
- Files saved as: `staticwaves_01_*.png` through `staticwaves_50_*.png`
- Location: `/workspace/ComfyUI/output/`

---

### 🖼️ `resize-for-printify.py`

Watches ComfyUI output and auto-resizes to Printify specs (4500×5400).

**Features:**
- Continuous file watcher
- Maintains aspect ratio
- Transparent background support
- Deduplication (won't re-process)

**Requirements:**
```bash
apt install -y imagemagick
```

**Usage:**
```bash
# Default paths
./scripts/comfyui/resize-for-printify.py

# Custom paths
COMFYUI_OUTPUT_DIR=/custom/path \
PRINTIFY_OUTPUT_DIR=/output/path \
./scripts/comfyui/resize-for-printify.py
```

**Output:**
- Location: `/workspace/printify_ready/`
- Format: 4500×5400 PNG

---

### 🚀 `push-to-printify.py`

Auto-creates hoodie + tee products on Printify from resized images.

**Features:**
- Uploads images to Printify
- Creates hoodie + tee per design
- Auto-publishes products
- Batch processing

**Setup:**
```bash
# Get API token: Printify → Account → Connections → API
export PRINTIFY_API_TOKEN=your_token

# Find Store ID: Printify → My Stores
export PRINTIFY_STORE_ID=12345678
```

**Usage:**
```bash
./scripts/comfyui/push-to-printify.py
```

**Products Created:**
- Blueprint: Gildan 18500 (Hoodie) + Gildan 5000 (Tee)
- Print Provider: Generic
- Placement: Front print, centered

---

### ⚙️ `install-sdxl.sh`

Downloads SDXL Base + Refiner models for ComfyUI.

**Usage:**
```bash
# Default: /workspace/ComfyUI/models/checkpoints
./scripts/comfyui/install-sdxl.sh

# Custom directory
COMFYUI_DIR=/custom/path ./scripts/comfyui/install-sdxl.sh
```

**Downloads:**
- `sdxl_base_1.0.safetensors` (6.9 GB)
- `sdxl_refiner_1.0.safetensors` (6.1 GB)

---

## Complete Automation Pipeline

### Workflow A: Gallery Proofing (Recommended)

**Terminal 1: ComfyUI**
```bash
cd /workspace/ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188
```

**Terminal 2: Auto-Resize Watcher**
```bash
./scripts/comfyui/resize-for-printify.py
```

**Terminal 3: Gallery Server**
```bash
./scripts/comfyui/gallery-server.py
```

**Terminal 4: Queue Prompts**
```bash
./scripts/comfyui/queue-50-prompts.py
```

**Browser:** Open gallery at `http://<pod-ip>:8080`
- Review designs visually
- Select which to publish
- Click "Publish to Printify"

---

### Workflow B: Fully Automated (No Proofing)

```bash
# Queue all 50 prompts
./scripts/comfyui/queue-50-prompts.py

# Wait for generation to complete, then publish ALL
./scripts/comfyui/push-to-printify.py
```

---

## SDXL Settings (Recommended)

**For POD Quality:**
- Resolution: 1024×1024
- Steps: 30-36
- CFG: 6.5-7.5
- Sampler: DPM++ 2M Karras
- Batch: 2-4 (GPU-heavy)

**Cost per Design (RunPod):**
- RTX A4000: ~$0.05-0.10
- Total: ~$5-10 for 50 designs

---

## Troubleshooting

### ComfyUI 400 Error
**Issue:** `400 Client Error: Bad Request`

**Fix:**
```bash
# Check model name matches exactly
ls /workspace/ComfyUI/models/checkpoints

# Update script with correct name
COMFYUI_MODEL=your_exact_model_name.safetensors ./scripts/comfyui/queue-50-prompts.py
```

### ImageMagick Not Found
```bash
apt update && apt install -y imagemagick
```

### Printify API Errors
```bash
# Verify credentials
echo $PRINTIFY_API_TOKEN
echo $PRINTIFY_STORE_ID

# Test API connection
curl -H "Authorization: Bearer $PRINTIFY_API_TOKEN" \
  https://api.printify.com/v1/shops.json
```

### No Images in Output
```bash
# Check ComfyUI output directory
ls /workspace/ComfyUI/output

# Check ComfyUI logs for errors
tail -f /workspace/ComfyUI/comfyui.log
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COMFYUI_API_URL` | ComfyUI API endpoint | `http://127.0.0.1:8188/prompt` |
| `COMFYUI_MODEL` | Model filename | `sdxl_base_1.0.safetensors` |
| `COMFYUI_OUTPUT_DIR` | ComfyUI output path | `/workspace/ComfyUI/output` |
| `PRINTIFY_OUTPUT_DIR` | Resized images path | `/workspace/printify_ready` |
| `PRINTIFY_API_TOKEN` | Printify API token | *(required)* |
| `PRINTIFY_STORE_ID` | Printify store ID | *(required)* |

---

## Production Scaling

### Daemonize with systemd

Create `/etc/systemd/system/comfyui-resize.service`:
```ini
[Unit]
Description=ComfyUI Printify Resize Watcher
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/workspace
ExecStart=/usr/bin/python3 /workspace/scripts/comfyui/resize-for-printify.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
systemctl enable comfyui-resize
systemctl start comfyui-resize
```

### Continuous Generation Loop

```bash
while true; do
  ./scripts/comfyui/queue-50-prompts.py
  sleep 3600  # Wait 1 hour
done
```

---

## Next Steps

1. **Add Background Removal:** Integrate Rembg or SAM for transparent PNGs
2. **Multi-Platform Publish:** Extend to Shopify, TikTok Shop, Etsy
3. **LoRA Integration:** Add custom LoRAs for brand consistency
4. **Upscaling:** Add 4x upscale before Printify resize
5. **Webhook Triggers:** Auto-publish when new designs are detected

---

**Need help?** See [main README](../../README.md) or [SETUP_GUIDE](../../SETUP_GUIDE.md)

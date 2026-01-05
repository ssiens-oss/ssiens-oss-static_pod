# Push Images from RunPod ComfyUI to Printify

Two methods available: run from **local machine** (via SSH) or run **directly on RunPod**.

---

## Method 1: Run on RunPod Instance (Recommended)

This is the simpler method - run the script directly on your RunPod instance.

### Setup on RunPod:

1. SSH into your RunPod instance:
```bash
ssh tleofuk3ify4lk-64410e97@ssh.runpod.io -i ~/.ssh/id_ed25519
```

2. Install Python requests library if not already installed:
```bash
pip install requests
```

3. Copy the script to RunPod:
```bash
# On your local machine, from the repo directory:
scp -i ~/.ssh/id_ed25519 scripts/runpod_push_to_printify.py \
  tleofuk3ify4lk-64410e97@ssh.runpod.io:/workspace/
```

4. Set environment variables on RunPod:
```bash
export PRINTIFY_API_KEY='your-printify-api-key'
export PRINTIFY_SHOP_ID='your-shop-id'
```

### Usage on RunPod:

```bash
cd /workspace
python3 runpod_push_to_printify.py
```

Or make it executable and run directly:
```bash
chmod +x runpod_push_to_printify.py
./runpod_push_to_printify.py
```

---

## Method 2: Run from Local Machine (via SSH)

This method connects to your RunPod instance via SSH, downloads images, and uploads them.

### Prerequisites:
1. SSH access to your RunPod instance
2. Printify API credentials configured in `.env`
3. Python dependencies installed locally

### Setup:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your `.env` file with:
```env
PRINTIFY_API_KEY=your-printify-api-key
PRINTIFY_SHOP_ID=your-shop-id
```

3. Ensure your SSH key exists at `~/.ssh/id_ed25519`

### Usage:

Direct Python execution:
```bash
python scripts/push_to_printify.py
```

Or use the convenience wrapper:
```bash
./push_images.sh
```

---

## What the Scripts Do

1. Find all images in `/workspace/ComfyUI/output` (or configured directory)
2. Filter out any files containing "comfyui" in their name
3. Upload each image to Printify via their API
4. Provide a summary of successful and failed uploads

## Notes

- The script will ask for confirmation before uploading
- Supported formats: PNG, JPG, JPEG, WEBP, GIF
- Files containing "comfyui" in the filename are automatically excluded
- You can set a custom output directory with: `export COMFYUI_OUTPUT_DIR=/your/path`

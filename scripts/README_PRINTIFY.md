# Push Images from RunPod ComfyUI to Printify

This script connects to your RunPod instance via SSH, downloads images from the ComfyUI output directory, and uploads them to Printify.

## Prerequisites

1. SSH access to your RunPod instance
2. Printify API credentials configured in `.env`
3. Python dependencies installed

## Setup

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

## Usage

### Direct Python execution:
```bash
python scripts/push_to_printify.py
```

### Or use the convenience wrapper:
```bash
./push_images.sh
```

## What it does

1. Connects to RunPod via SSH: `tleofuk3ify4lk-64410e97@ssh.runpod.io`
2. Lists all images in `/workspace/ComfyUI/output`
3. Filters out any files containing "comfyui" in their name
4. Downloads filtered images to a temporary directory
5. Uploads each image to Printify via their API
6. Provides a summary of successful and failed uploads

## Notes

- The script will ask for confirmation before uploading
- Images are temporarily downloaded to your local machine during the process
- Supported formats: PNG, JPG, JPEG, WEBP, GIF
- Files containing "comfyui" in the filename are automatically excluded

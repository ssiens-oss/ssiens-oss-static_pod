#!/bin/bash
# Process ComfyUI outputs: upscale to print resolution and push to Printify

set -e

echo "══════════════════════════════════════════════════════"
echo "  ComfyUI → Printify Pipeline (4500x5400 Print Ready)"
echo "══════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if we're on RunPod
if [ ! -d "/workspace" ]; then
    echo "Error: Must run on RunPod"
    exit 1
fi

# Find latest ComfyUI output
COMFY_OUTPUT_DIR="/workspace/ComfyUI/output"
if [ ! -d "$COMFY_OUTPUT_DIR" ]; then
    echo "Error: ComfyUI output directory not found"
    exit 1
fi

echo "Searching for latest ComfyUI outputs..."
LATEST_IMAGE=$(find "$COMFY_OUTPUT_DIR" -name "*.png" -type f -printf '%T@ %p\n' | sort -rn | head -1 | cut -d' ' -f2-)

if [ -z "$LATEST_IMAGE" ]; then
    echo "Error: No ComfyUI outputs found in $COMFY_OUTPUT_DIR"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found: $LATEST_IMAGE"
echo ""

# Create processing directory
PROCESS_DIR="/workspace/data/print-ready"
mkdir -p "$PROCESS_DIR"

# Get base filename
BASENAME=$(basename "$LATEST_IMAGE" .png)
OUTPUT_BASE="${PROCESS_DIR}/${BASENAME}_print"

echo "Processing pipeline:"
echo "  1. Upscale to 4500x5400"
echo "  2. Remove background"
echo "  3. Create Printify products (tshirt + hoodie)"
echo ""

# Run Python processing script
python3 <<EOF
import sys
from PIL import Image
import os

print("📐 Upscaling to 4500x5400...")
img = Image.open("$LATEST_IMAGE")

# Upscale to print resolution with high-quality resampling
target_size = (4500, 5400)
upscaled = img.resize(target_size, Image.Resampling.LANCZOS)

# Save upscaled version
upscaled_path = "${OUTPUT_BASE}_upscaled.png"
upscaled.save(upscaled_path, "PNG", optimize=False, quality=100)
print(f"✓ Saved upscaled: {upscaled_path}")

# Remove background
print("🎨 Removing background...")
try:
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Force CPU
    from rembg import remove

    # Remove background from upscaled image
    transparent = remove(upscaled)
    transparent_path = "${OUTPUT_BASE}_transparent.png"
    transparent.save(transparent_path, "PNG")
    print(f"✓ Saved transparent: {transparent_path}")

    # Store path for bash script
    with open("/tmp/transparent_path.txt", "w") as f:
        f.write(transparent_path)

except Exception as e:
    print(f"Warning: Background removal failed: {e}")
    print("Continuing with upscaled image...")
    with open("/tmp/transparent_path.txt", "w") as f:
        f.write(upscaled_path)

print("")
print("✅ Image processing complete!")
EOF

# Get the transparent image path
TRANSPARENT_PATH=$(cat /tmp/transparent_path.txt)

echo ""
echo "══════════════════════════════════════════════════════"
echo "  Uploading to Printify"
echo "══════════════════════════════════════════════════════"
echo ""

# Submit to POD Engine API
cd /workspace/app

# Create unique design name
DESIGN_NAME="Print Ready Design - $(date +%Y%m%d_%H%M%S)"

echo "Submitting to POD Engine..."
echo "  Design: $DESIGN_NAME"
echo "  Image: $TRANSPARENT_PATH"
echo "  Products: T-shirt + Hoodie"
echo ""

# Use curl to submit directly to Printify via our API
# We'll use a direct file upload approach
RESPONSE=$(curl -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"$DESIGN_NAME\",
    \"productTypes\": [\"tshirt\", \"hoodie\"],
    \"autoPublish\": false,
    \"imageOverride\": \"$TRANSPARENT_PATH\"
  }" 2>/dev/null)

echo "$RESPONSE"

# Extract job ID
JOB_ID=$(echo "$RESPONSE" | grep -o '"jobId":"[^"]*"' | cut -d'"' -f4)

if [ -z "$JOB_ID" ]; then
    echo "Error: Failed to submit job"
    exit 1
fi

echo ""
echo -e "${GREEN}✓${NC} Job submitted: $JOB_ID"
echo ""
echo "Monitoring job progress..."
echo ""

# Monitor job
tail -f /workspace/logs/pod-engine.log | grep --line-buffered "$JOB_ID" &
TAIL_PID=$!

# Wait for completion (max 5 minutes)
for i in {1..60}; do
    sleep 5
    STATUS=$(curl -s "http://localhost:3000/api/jobs/$JOB_ID" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

    if [ "$STATUS" = "completed" ]; then
        kill $TAIL_PID 2>/dev/null || true
        echo ""
        echo -e "${GREEN}✅ Job completed successfully!${NC}"
        echo ""
        echo "Check your Printify dashboard:"
        echo "  https://printify.com/app/products"
        echo ""
        echo "Files created:"
        echo "  Upscaled: ${OUTPUT_BASE}_upscaled.png"
        echo "  Transparent: $TRANSPARENT_PATH"
        exit 0
    elif [ "$STATUS" = "failed" ]; then
        kill $TAIL_PID 2>/dev/null || true
        echo ""
        echo "❌ Job failed. Check logs above."
        exit 1
    fi
done

kill $TAIL_PID 2>/dev/null || true
echo ""
echo "⚠️  Job still running after 5 minutes. Check status manually:"
echo "  curl http://localhost:3000/api/jobs/$JOB_ID"

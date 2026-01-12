#!/bin/bash

###############################################################################
# RunPod - Fix Missing Dependencies & Setup ComfyUI
###############################################################################

set -e

echo "=========================================="
echo "  Fixing POD Engine Dependencies"
echo "=========================================="

# Stop any running services first
echo "▶ Stopping services..."
./stop-pod-engine.sh 2>/dev/null || true

# Install/Setup ComfyUI
if [ ! -d "ComfyUI" ]; then
    echo "▶ Installing ComfyUI..."

    # Clone ComfyUI
    git clone https://github.com/comfyanonymous/ComfyUI.git
    cd ComfyUI

    # Install dependencies
    pip install -r requirements.txt
    pip install sqlalchemy

    # Download SDXL model (if not exists)
    mkdir -p models/checkpoints
    if [ ! -f "models/checkpoints/sd_xl_base_1.0.safetensors" ]; then
        echo "▶ Downloading SDXL model (this may take a few minutes)..."
        wget -q --show-progress -O models/checkpoints/sd_xl_base_1.0.safetensors \
            "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
    fi

    cd ..
    echo "✓ ComfyUI installed"
else
    echo "▶ ComfyUI already exists, installing missing dependencies..."
    cd ComfyUI
    pip install sqlalchemy
    pip install -r requirements.txt
    cd ..
    echo "✓ Dependencies updated"
fi

# Update environment for RunPod paths
echo "▶ Configuring RunPod paths..."
sed -i 's|COMFYUI_OUTPUT_DIR=.*|COMFYUI_OUTPUT_DIR=/workspace/ssiens-oss-static_pod/ComfyUI/output|g' .env
sed -i 's|COMFYUI_API_URL=.*|COMFYUI_API_URL=http://localhost:8188|g' .env
sed -i 's|POD_IMAGE_DIR=.*|POD_IMAGE_DIR=/workspace/ssiens-oss-static_pod/ComfyUI/output|g' gateway/.env

echo "✓ Paths configured"

# Create output directory
mkdir -p ComfyUI/output

echo ""
echo "=========================================="
echo "  Fix Complete!"
echo "=========================================="
echo ""
echo "Start services with:"
echo "  ./start-pod-engine.sh"
echo ""

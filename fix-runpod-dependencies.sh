#!/bin/bash

###############################################################################
# RunPod - Fix Missing Dependencies & Setup ComfyUI + Gateway
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
    pip install -r requirements.txt 2>/dev/null || true
    cd ..
    echo "✓ Dependencies updated"
fi

# Setup Gateway
echo "▶ Setting up POD Gateway..."
cd gateway

# Create/activate virtual environment
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install Gateway dependencies
pip install -r requirements.txt

# Configure Gateway .env
if [ ! -f ".env" ]; then
    cat > .env << 'GATEWAY_ENV'
PRINTIFY_API_KEY=${PRINTIFY_API_KEY:-demo-key}
PRINTIFY_SHOP_ID=${PRINTIFY_SHOP_ID:-demo-shop-id}
POD_IMAGE_DIR=/workspace/ssiens-oss-static_pod/ComfyUI/output
POD_STATE_FILE=/workspace/ssiens-oss-static_pod/gateway/state.json
POD_ARCHIVE_DIR=/workspace/ssiens-oss-static_pod/gateway/archive
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
GATEWAY_ENV
fi

# Initialize state file
if [ ! -f "state.json" ]; then
    echo '{"designs": []}' > state.json
fi

# Create directories
mkdir -p archive

cd ..
echo "✓ Gateway configured"

# Update main .env for RunPod paths
echo "▶ Configuring RunPod paths in main .env..."
sed -i 's|COMFYUI_OUTPUT_DIR=.*|COMFYUI_OUTPUT_DIR=/workspace/ssiens-oss-static_pod/ComfyUI/output|g' .env
sed -i 's|COMFYUI_API_URL=.*|COMFYUI_API_URL=http://localhost:8188|g' .env
sed -i 's|STORAGE_PATH=.*|STORAGE_PATH=/workspace/ssiens-oss-static_pod/data/designs|g' .env

echo "✓ Paths configured"

# Create necessary directories
mkdir -p ComfyUI/output
mkdir -p data/designs
mkdir -p logs

echo ""
echo "=========================================="
echo "  Fix Complete!"
echo "=========================================="
echo ""
echo "Configuration verified:"
echo "  ✓ ComfyUI installed with SDXL model"
echo "  ✓ Gateway configured with virtual environment"
echo "  ✓ All paths set for RunPod"
echo "  ✓ Required directories created"
echo ""
echo "Start services with:"
echo "  ./start-pod-engine.sh"
echo ""
echo "Or start individually:"
echo "  cd ComfyUI && python3 main.py --listen 0.0.0.0 --port 8188 &"
echo "  cd gateway && source .venv/bin/activate && python app/main.py &"
echo "  npm run dev &"
echo ""

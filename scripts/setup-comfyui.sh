#!/bin/bash
# Setup ComfyUI for local development

set -e

echo "🎨 Setting up ComfyUI..."

# Configuration
COMFYUI_DIR="${COMFYUI_DIR:-./ComfyUI}"
MODELS_DIR="${COMFYUI_DIR}/models"

# Clone ComfyUI if not exists
if [ ! -d "$COMFYUI_DIR" ]; then
    echo "Cloning ComfyUI repository..."
    git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFYUI_DIR"
else
    echo "ComfyUI directory already exists"
fi

cd "$COMFYUI_DIR"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip3 install -r requirements.txt

# Create models directory structure
echo "Creating models directory structure..."
mkdir -p "${MODELS_DIR}/checkpoints"
mkdir -p "${MODELS_DIR}/vae"
mkdir -p "${MODELS_DIR}/loras"
mkdir -p "${MODELS_DIR}/embeddings"

# Download SDXL model if not exists
SDXL_MODEL="${MODELS_DIR}/checkpoints/sd_xl_base_1.0.safetensors"
if [ ! -f "$SDXL_MODEL" ]; then
    echo "Downloading SDXL model (this may take a while)..."
    wget -O "$SDXL_MODEL" \
        "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
else
    echo "SDXL model already exists"
fi

echo "✅ ComfyUI setup complete!"
echo ""
echo "To start ComfyUI, run:"
echo "  cd $COMFYUI_DIR"
echo "  python3 main.py --listen 0.0.0.0 --port 8188"

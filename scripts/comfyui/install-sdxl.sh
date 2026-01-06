#!/bin/bash
# Install SDXL Models for ComfyUI
# Production-ready for POD quality generation

set -e

COMFYUI_DIR="${COMFYUI_DIR:-/workspace/ComfyUI}"
MODELS_DIR="${COMFYUI_DIR}/models/checkpoints"

echo "╔════════════════════════════════════════════════════╗"
echo "║  SDXL Model Installation for ComfyUI             ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Check if ComfyUI exists
if [ ! -d "$COMFYUI_DIR" ]; then
    echo "❌ ComfyUI not found at: $COMFYUI_DIR"
    echo "Please install ComfyUI first or set COMFYUI_DIR environment variable"
    exit 1
fi

# Create models directory
mkdir -p "$MODELS_DIR"
cd "$MODELS_DIR"

echo "📁 Models directory: $MODELS_DIR"
echo ""

# Download SDXL Base
if [ -f "sdxl_base_1.0.safetensors" ]; then
    echo "✅ SDXL Base already installed"
else
    echo "📥 Downloading SDXL Base (~6.9 GB)..."
    wget -O sdxl_base_1.0.safetensors \
        --progress=bar:force \
        https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
    echo "✅ SDXL Base downloaded"
fi

echo ""

# Download SDXL Refiner
if [ -f "sdxl_refiner_1.0.safetensors" ]; then
    echo "✅ SDXL Refiner already installed"
else
    echo "📥 Downloading SDXL Refiner (~6.1 GB)..."
    wget -O sdxl_refiner_1.0.safetensors \
        --progress=bar:force \
        https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors
    echo "✅ SDXL Refiner downloaded"
fi

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║  ✅ SDXL Installation Complete                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Installed models:"
ls -lh "$MODELS_DIR"/sdxl_*.safetensors
echo ""
echo "🔄 Restart ComfyUI to use SDXL models"
echo ""
echo "Recommended SDXL settings for POD:"
echo "  • Resolution: 1024×1024"
echo "  • Steps: 30-36"
echo "  • CFG: 6.5-7.5"
echo "  • Sampler: DPM++ 2M Karras"
echo "  • Batch: 2-4 (SDXL is GPU-heavy)"

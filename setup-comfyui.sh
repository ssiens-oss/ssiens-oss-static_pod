#!/bin/bash
echo "🎨 ComfyUI Installation Script"
echo "================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Install location
INSTALL_DIR="$HOME/ComfyUI"
echo "📦 Installing ComfyUI to: $INSTALL_DIR"
echo ""

# Clone ComfyUI
if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️  ComfyUI directory already exists"
    read -p "Remove and reinstall? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
    else
        echo "Skipping installation"
        exit 0
    fi
fi

echo "📥 Cloning ComfyUI..."
git clone https://github.com/comfyanonymous/ComfyUI.git "$INSTALL_DIR"

cd "$INSTALL_DIR"

echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "✅ ComfyUI installed successfully!"
echo ""
echo "🚀 To start ComfyUI:"
echo "   cd $INSTALL_DIR"
echo "   python3 main.py --listen"
echo ""
echo "📝 Note: You'll need to download models to ComfyUI/models/"
echo "   Default model: models/checkpoints/ (put .safetensors files here)"
echo ""

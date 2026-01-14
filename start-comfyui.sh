#!/bin/bash
# ComfyUI Startup Script

set -e

cd "$(dirname "$0")/ComfyUI"

echo "🎨 Starting ComfyUI..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ComfyUI will be available at: http://localhost:8188"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188

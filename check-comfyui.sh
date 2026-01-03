#!/bin/bash

echo "🎨 Checking ComfyUI Status..."
echo ""

COMFYUI_URL="http://localhost:8188"

# Try to connect to ComfyUI
if curl -s --max-time 5 "$COMFYUI_URL/system_stats" > /dev/null 2>&1; then
    echo "✅ ComfyUI is RUNNING at $COMFYUI_URL"
    echo ""
    echo "System Info:"
    curl -s "$COMFYUI_URL/system_stats" | head -10
    echo ""
    echo "Ready to proceed!"
else
    echo "❌ ComfyUI is NOT running at $COMFYUI_URL"
    echo ""
    echo "Please start ComfyUI first:"
    echo "  1. Navigate to your ComfyUI directory"
    echo "  2. Run: python main.py"
    echo "  3. Wait for it to start (should see 'Starting server')"
    echo "  4. Run this script again"
    echo ""
    echo "Or use RunPod:"
    echo "  1. Go to runpod.io"
    echo "  2. Deploy ComfyUI template"
    echo "  3. Update COMFYUI_API_URL in .env"
    exit 1
fi

#!/bin/bash

# Pod Engine Pipeline Startup Script
# Starts the complete pod engine pipeline with full GUI

echo "🚀 Starting Pod Engine Pipeline..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
  echo ""
fi

# Check if ComfyUI is running
echo "🔍 Checking ComfyUI connection..."
if curl -s http://localhost:8188 > /dev/null 2>&1; then
  echo "✅ ComfyUI is running"
else
  echo "⚠️  ComfyUI is not running at http://localhost:8188"
  echo ""
  echo "To start ComfyUI, run in another terminal:"
  echo "  cd ComfyUI"
  echo "  python3 main.py --listen 0.0.0.0 --port 8188"
  echo ""
  echo "Continuing anyway..."
fi

echo ""
echo "🌟 Starting Pod Engine GUI..."
echo "   Access at: http://localhost:5174"
echo ""
echo "Features:"
echo "  ✓ ComfyUI + RunPod integration"
echo "  ✓ Local save from RunPod"
echo "  ✓ Proofing system"
echo "  ✓ Multi-platform publishing"
echo ""

npm run pod-engine

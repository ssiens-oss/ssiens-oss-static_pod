#!/bin/bash
# Stop POD Pipeline

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

echo "🛑 Stopping POD Pipeline..."
echo ""

# Kill by PID files if they exist
if [ -f .comfy.pid ]; then
    kill $(cat .comfy.pid) 2>/dev/null && echo "  ✓ ComfyUI stopped" || echo "  - ComfyUI not running"
    rm .comfy.pid
fi

if [ -f .gallery.pid ]; then
    kill $(cat .gallery.pid) 2>/dev/null && echo "  ✓ Gallery Bridge stopped" || echo "  - Gallery Bridge not running"
    rm .gallery.pid
fi

if [ -f .webui.pid ]; then
    kill $(cat .webui.pid) 2>/dev/null && echo "  ✓ Web UI stopped" || echo "  - Web UI not running"
    rm .webui.pid
fi

# Fallback: kill by process name
pkill -f "ComfyUI/main.py" 2>/dev/null
pkill -f "uvicorn gallery.server" 2>/dev/null
pkill -f "http.server 8088" 2>/dev/null

echo ""
echo "✅ POD Pipeline stopped"

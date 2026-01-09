#!/bin/bash
# Complete POD Pipeline Launcher
# Starts: Gallery Bridge + Web UI
# (Add ComfyUI separately if running locally)

set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

# Activate virtual environment if it exists
if [ -d "$REPO_ROOT/.venv" ]; then
    source "$REPO_ROOT/.venv/bin/activate"
    echo "✓ Virtual environment activated"
fi

echo "🚀 Starting POD Pipeline..."
echo "📂 Repository: $REPO_ROOT"
echo ""

# Install dependencies if needed
pip install -q fastapi uvicorn 2>/dev/null || true

# Kill any existing instances
pkill -f "uvicorn gallery.server" 2>/dev/null || true
pkill -f "http.server 8088" 2>/dev/null || true

sleep 1

# Check for ComfyUI
if [ -d "$REPO_ROOT/ComfyUI" ]; then
    echo "🎨 Starting ComfyUI on :8188..."
    pkill -f "ComfyUI/main.py" 2>/dev/null || true
    cd "$REPO_ROOT/ComfyUI"
    nohup python3 main.py --listen 0.0.0.0 --port 8188 >> "$REPO_ROOT/comfy.log" 2>&1 &
    COMFY_PID=$!
    echo "  ComfyUI PID: $COMFY_PID"
    sleep 3
    cd "$REPO_ROOT"
fi

# Start Gallery Bridge (with all features)
echo "🌉 Starting Gallery Bridge on :8099..."
nohup python3 -m uvicorn gallery.server:app --host 0.0.0.0 --port 8099 >> "$REPO_ROOT/gallery.log" 2>&1 &
GALLERY_PID=$!
echo "  Gallery PID: $GALLERY_PID"

sleep 2

# Start Web UI server
echo "🖼  Starting Web UI on :8088..."
nohup python3 -m http.server 8088 >> "$REPO_ROOT/webui.log" 2>&1 &
WEBUI_PID=$!
echo "  Web UI PID: $WEBUI_PID"

sleep 1

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ POD Pipeline ONLINE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🌐 Services:"
if [ -n "$COMFY_PID" ]; then
    echo "    ComfyUI:        http://localhost:8188"
fi
echo "    Gallery API:    http://localhost:8099"
echo "    Web Gallery:    http://localhost:8088/view-gallery.html"
echo ""
echo "  📡 API Endpoints:"
echo "    List designs:   GET  http://localhost:8099/designs"
echo "    Live stream:    GET  http://localhost:8099/stream"
echo "    Export ZIP:     GET  http://localhost:8099/export"
echo "    Publish image:  POST http://localhost:8099/publish/{image}"
echo "    Delete image:   DEL  http://localhost:8099/designs/{image}"
echo ""
echo "  📝 Logs:"
if [ -n "$COMFY_PID" ]; then
    echo "    ComfyUI:   tail -f $REPO_ROOT/comfy.log"
fi
echo "    Gallery:   tail -f $REPO_ROOT/gallery.log"
echo "    Web UI:    tail -f $REPO_ROOT/webui.log"
echo ""
echo "  🛑 Stop:"
echo "    ./stop-pod-pipeline.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save PIDs for stop script
echo "$GALLERY_PID" > .gallery.pid
echo "$WEBUI_PID" > .webui.pid
[ -n "$COMFY_PID" ] && echo "$COMFY_PID" > .comfy.pid

echo "✨ Pipeline ready! Open http://localhost:8088/view-gallery.html"
echo ""

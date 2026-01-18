#!/bin/bash
# Stop POD Pipeline Services

echo "🛑 Stopping POD Pipeline Services..."
echo ""

# Stop ComfyUI
if [ -f /tmp/pod-comfyui.pid ]; then
    COMFYUI_PID=$(cat /tmp/pod-comfyui.pid)
    if ps -p $COMFYUI_PID > /dev/null 2>&1; then
        echo "🎨 Stopping ComfyUI (PID: $COMFYUI_PID)..."
        kill $COMFYUI_PID
        echo "✅ ComfyUI stopped"
    else
        echo "⚠️  ComfyUI not running"
    fi
    rm /tmp/pod-comfyui.pid
fi

# Stop Gateway
if [ -f /tmp/pod-gateway.pid ]; then
    GATEWAY_PID=$(cat /tmp/pod-gateway.pid)
    if ps -p $GATEWAY_PID > /dev/null 2>&1; then
        echo "🌐 Stopping Gateway (PID: $GATEWAY_PID)..."
        kill $GATEWAY_PID
        echo "✅ Gateway stopped"
    else
        echo "⚠️  Gateway not running"
    fi
    rm /tmp/pod-gateway.pid
fi

# Clean up any stray processes
pkill -f "comfyui.*main.py" 2>/dev/null || true
pkill -f "gateway.*main.py" 2>/dev/null || true

echo ""
echo "✅ All services stopped"

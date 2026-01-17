#!/bin/bash
set -e

echo "🚀 Starting POD Pipeline Production Environment..."

# Start ComfyUI
echo "⚙️  Starting ComfyUI..."
cd /workspace/ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188 > /var/log/comfyui.log 2>&1 &
COMFYUI_PID=$!

# Wait for ComfyUI to be ready
echo "⏳ Waiting for ComfyUI to initialize..."
for i in {1..30}; do
    if curl -sf http://localhost:8188/system_stats > /dev/null 2>&1; then
        echo "✅ ComfyUI is ready"
        break
    fi
    echo "   Attempt $i/30..."
    sleep 2
done

# Test Nginx configuration
echo "🔍 Testing Nginx configuration..."
nginx -t

# Start Nginx
echo "🌐 Starting Nginx..."
nginx

echo "✅ All services started successfully!"
echo "📊 Access the dashboard at http://localhost"
echo "🎨 ComfyUI API available at http://localhost:8188"

# Monitor services
while true; do
    if ! kill -0 $COMFYUI_PID 2>/dev/null; then
        echo "❌ ComfyUI process died, restarting..."
        cd /workspace/ComfyUI
        python3 main.py --listen 0.0.0.0 --port 8188 > /var/log/comfyui.log 2>&1 &
        COMFYUI_PID=$!
    fi
    sleep 10
done

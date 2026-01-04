#!/bin/bash
# Quick Service Restart Script
# Use this when API keys are already configured and you just need to restart services

echo "🔄 Restarting POD Engine Services..."
echo ""

# Kill existing processes
echo "Stopping existing services..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "pod-engine-api" 2>/dev/null || true
sleep 3

# Verify ports are free
if netstat -tlnp 2>/dev/null | grep -q ":8188 "; then
    echo "⚠ Port 8188 still in use, waiting..."
    sleep 5
fi

if netstat -tlnp 2>/dev/null | grep -q ":3000 "; then
    echo "⚠ Port 3000 still in use, waiting..."
    sleep 5
fi

echo "✓ Services stopped"
echo ""

# Start ComfyUI
echo "Starting ComfyUI..."
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188 > /workspace/logs/comfyui.log 2>&1 &
echo "  Waiting for ComfyUI..."
sleep 15

if curl -s http://localhost:8188 > /dev/null 2>&1; then
    echo "✓ ComfyUI running"
else
    echo "✗ ComfyUI failed to start (check /workspace/logs/comfyui.log)"
fi

echo ""

# Start POD Engine
echo "Starting POD Engine API..."
cd /workspace/app
npx tsx pod-engine-api.ts > /workspace/logs/pod-engine.log 2>&1 &
echo "  Waiting for POD Engine..."
sleep 10

if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo "✓ POD Engine running"
    curl -s http://localhost:3000/health | grep -o '"uptime":[0-9]*' | awk -F':' '{print "  Uptime: " $2 "s"}'
else
    echo "✗ POD Engine failed to start (check /workspace/logs/pod-engine.log)"
fi

echo ""
echo "════════════════════════════════════════════════════"
echo "✅ Services Restarted"
echo "════════════════════════════════════════════════════"
echo "ComfyUI:        http://localhost:8188"
echo "POD Engine:     http://localhost:3000"
echo "Monitor:        http://localhost:8080/monitor.html"
echo ""
echo "Test with:"
echo "  curl -X POST http://localhost:3000/api/generate \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"prompt\": \"Test design\", \"productTypes\": [\"tshirt\"]}'"
echo ""

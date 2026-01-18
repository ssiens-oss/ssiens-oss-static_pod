#!/bin/bash
# Full POD Pipeline Startup Script
# Starts ComfyUI + Gateway + Monitoring

set -e

echo "🚀 Starting Full POD Serverless Pipeline"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check ComfyUI
COMFYUI_DIR="$HOME/ComfyUI"
if [ ! -d "$COMFYUI_DIR" ]; then
    echo -e "${RED}❌ ComfyUI not found at $COMFYUI_DIR${NC}"
    echo ""
    echo "Please install ComfyUI first:"
    echo "  ./setup-comfyui.sh"
    echo ""
    echo "Or install manually:"
    echo "  git clone https://github.com/comfyanonymous/ComfyUI.git ~/ComfyUI"
    echo "  cd ~/ComfyUI && pip install -r requirements.txt"
    exit 1
fi

echo -e "${GREEN}✅ ComfyUI found${NC}"

# Check environment
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please create .env with required variables"
    exit 1
fi

echo -e "${GREEN}✅ Environment configured${NC}"
echo ""

# Start ComfyUI in background
echo "🎨 Starting ComfyUI..."
cd "$COMFYUI_DIR"
python3 main.py --listen --port 8188 > /tmp/comfyui.log 2>&1 &
COMFYUI_PID=$!
echo -e "${GREEN}✅ ComfyUI started (PID: $COMFYUI_PID)${NC}"
echo "   Logs: tail -f /tmp/comfyui.log"
echo "   URL: http://localhost:8188"

# Wait for ComfyUI to start
echo ""
echo "⏳ Waiting for ComfyUI to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8188/system_stats > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ComfyUI is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Return to project directory
cd - > /dev/null

# Start Gateway
echo ""
echo "🌐 Starting POD Gateway..."
cd gateway
python app/main.py > /tmp/pod-gateway.log 2>&1 &
GATEWAY_PID=$!
echo -e "${GREEN}✅ Gateway started (PID: $GATEWAY_PID)${NC}"
echo "   Logs: tail -f /tmp/pod-gateway.log"
echo "   URL: http://localhost:5000"

cd - > /dev/null

# Save PIDs
echo "$COMFYUI_PID" > /tmp/pod-comfyui.pid
echo "$GATEWAY_PID" > /tmp/pod-gateway.pid

echo ""
echo "================================================"
echo -e "${GREEN}🎉 Full Pipeline Started Successfully!${NC}"
echo "================================================"
echo ""
echo "📊 Service Status:"
echo "   ComfyUI:  http://localhost:8188 (PID: $COMFYUI_PID)"
echo "   Gateway:  http://localhost:5000 (PID: $GATEWAY_PID)"
echo ""
echo "📝 Logs:"
echo "   ComfyUI:  tail -f /tmp/comfyui.log"
echo "   Gateway:  tail -f /tmp/pod-gateway.log"
echo ""
echo "🛑 To stop all services:"
echo "   ./stop-pipeline.sh"
echo ""
echo "💡 Next steps:"
echo "   1. Open http://localhost:5000 in your browser"
echo "   2. Generate images via ComfyUI or upload manually"
echo "   3. Approve and publish to Printify"
echo ""

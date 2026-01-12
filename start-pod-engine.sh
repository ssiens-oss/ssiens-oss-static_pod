#!/bin/bash
set -e
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}Starting POD Engine...${NC}\n"
set -a
source .env 2>/dev/null || true
set +a

mkdir -p logs

# Start ComfyUI
if [ -d "ComfyUI" ]; then
    echo -e "${CYAN}▶ Starting ComfyUI...${NC}"
    cd ComfyUI
    python3 main.py --listen 0.0.0.0 --port 8188 > ../logs/comfyui.log 2>&1 &
    COMFYUI_PID=$!
    echo $COMFYUI_PID > ../logs/comfyui.pid
    cd ..
    echo -e "${GREEN}✓ ComfyUI started (PID: $COMFYUI_PID)${NC}"
    echo -e "${YELLOW}  http://localhost:8188${NC}"
else
    echo -e "${YELLOW}⚠ ComfyUI not found${NC}"
fi

sleep 3

# Start Gateway with PYTHONPATH
echo -e "${CYAN}▶ Starting POD Gateway...${NC}"
cd gateway
source .venv/bin/activate
# Set PYTHONPATH so 'from app import' works correctly
export PYTHONPATH=/workspace/ssiens-oss-static_pod/gateway:$PYTHONPATH
python app/main.py > ../logs/gateway.log 2>&1 &
GATEWAY_PID=$!
echo $GATEWAY_PID > ../logs/gateway.pid
cd ..
echo -e "${GREEN}✓ Gateway started (PID: $GATEWAY_PID)${NC}"
echo -e "${YELLOW}  http://localhost:5000${NC}"

# Start Web UI
echo -e "${CYAN}▶ Starting Web UI...${NC}"
npm run dev > logs/webui.log 2>&1 &
WEBUI_PID=$!
echo $WEBUI_PID > logs/webui.pid
echo -e "${GREEN}✓ Web UI started (PID: $WEBUI_PID)${NC}"
echo -e "${YELLOW}  http://localhost:3000${NC}"

cat > logs/pod-engine.pids << PIDS
COMFYUI_PID=$COMFYUI_PID
GATEWAY_PID=$GATEWAY_PID
WEBUI_PID=$WEBUI_PID
PIDS

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   POD Engine Started Successfully!       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Services:${NC}"
echo "  ComfyUI:      http://localhost:8188"
echo "  POD Gateway:  http://localhost:5000"
echo "  Web UI:       http://localhost:3000"
echo ""
echo -e "${CYAN}Logs: tail -f logs/*.log${NC}"
echo -e "${CYAN}Stop: ./stop-pod-engine.sh${NC}"

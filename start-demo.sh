#!/bin/bash
set -e
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}Starting POD Engine (Demo Mode)...${NC}\n"
echo -e "${YELLOW}⚠ Running in DEMO mode with mock services${NC}\n"

mkdir -p logs

# Start Gateway (demo mode - will show UI but can't actually publish)
echo -e "${CYAN}▶ Starting POD Gateway...${NC}"
cd gateway
source .venv/bin/activate
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
echo -e "${YELLOW}  http://localhost:5173${NC}"

cat > logs/pod-demo.pids << PIDS
GATEWAY_PID=$GATEWAY_PID
WEBUI_PID=$WEBUI_PID
PIDS

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Demo Services Started!                 ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Demo Services:${NC}"
echo "  POD Gateway:  http://localhost:5000"
echo "  Web UI:       http://localhost:5173"
echo ""
echo -e "${YELLOW}Note: ComfyUI not started in demo mode${NC}"
echo -e "${YELLOW}Note: Configure real API keys for production${NC}"
echo ""
echo -e "${CYAN}Logs: tail -f logs/*.log${NC}"
echo -e "${CYAN}Stop: ./stop-demo.sh${NC}"

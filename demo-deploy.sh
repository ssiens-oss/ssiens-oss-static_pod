#!/bin/bash

###############################################################################
# Demo POD Engine Deployment (No API keys required)
###############################################################################

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}═════════════════════════════════════${NC}"
echo -e "${CYAN}  POD Engine Demo Deploy${NC}"
echo -e "${CYAN}═════════════════════════════════════${NC}\n"

echo -e "${YELLOW}⚠ Demo Mode - Using placeholder credentials${NC}"
echo -e "${YELLOW}  This will set up the infrastructure only.${NC}"
echo -e "${YELLOW}  For actual usage, configure real API keys.${NC}\n"

# Create demo .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# Install Gateway dependencies
echo -e "${CYAN}▶ Setting up POD Gateway...${NC}"
cd gateway
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Gateway dependencies installed${NC}"

# Configure Gateway with demo values
cat > .env << 'GATEWAY_ENV'
PRINTIFY_API_KEY=demo-key-change-me
PRINTIFY_SHOP_ID=demo-shop-id
POD_IMAGE_DIR=/workspace/comfyui/output
POD_STATE_FILE=./state.json
POD_ARCHIVE_DIR=./archive
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=true
GATEWAY_ENV

# Initialize state
if [ ! -f "state.json" ]; then
    echo '{"designs": []}' > state.json
fi

mkdir -p archive output
cd ..
echo -e "${GREEN}✓ Gateway configured (demo mode)${NC}"

# Install Node dependencies
echo -e "${CYAN}▶ Installing Node.js dependencies...${NC}"
if [ ! -d "node_modules" ]; then
    npm install --silent
    echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Node.js dependencies already installed${NC}"
fi

# Create logs directory
mkdir -p logs

# Create demo startup script
cat > start-demo.sh << 'START_DEMO'
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
START_DEMO

chmod +x start-demo.sh

cat > stop-demo.sh << 'STOP_DEMO'
#!/bin/bash
GREEN='\033[0;32m'
NC='\033[0m'

echo "Stopping demo services..."

if [ -f logs/pod-demo.pids ]; then
    source logs/pod-demo.pids
    for pid_var in GATEWAY_PID WEBUI_PID; do
        pid=${!pid_var}
        if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
            kill $pid
            echo -e "${GREEN}✓ Stopped $pid_var${NC}"
        fi
    done
    rm logs/pod-demo.pids
fi
STOP_DEMO

chmod +x stop-demo.sh

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Demo Deployment Complete!              ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Start demo:${NC}"
echo -e "  ${YELLOW}./start-demo.sh${NC}"
echo ""
echo -e "${CYAN}Access:${NC}"
echo "  • POD Gateway:  http://localhost:5000"
echo "  • Web UI:       http://localhost:5173"
echo ""
echo -e "${YELLOW}⚠ Remember: This is demo mode!${NC}"
echo -e "${YELLOW}  Configure real API keys in .env for production use.${NC}"
echo ""

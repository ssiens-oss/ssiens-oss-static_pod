#!/bin/bash

###############################################################################
# Quick POD Engine Deployment (Non-Interactive)
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}═════════════════════════════════════${NC}"
echo -e "${CYAN}  POD Engine Quick Deploy${NC}"
echo -e "${CYAN}═════════════════════════════════════${NC}\n"

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${RED}✗ Please edit .env with your API keys!${NC}"
    echo -e "${CYAN}Required:${NC}"
    echo "  - ANTHROPIC_API_KEY"
    echo "  - PRINTIFY_API_KEY"
    echo "  - PRINTIFY_SHOP_ID"
    echo ""
    echo "Then run: ./quick-deploy.sh"
    exit 1
fi

# Load environment
set -a
source .env 2>/dev/null || true
set +a

# Validate critical variables
echo -e "${CYAN}▶ Validating configuration...${NC}"
MISSING=()
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" == "sk-ant-your-api-key-here" ]; then
    MISSING+=("ANTHROPIC_API_KEY")
fi
if [ -z "$PRINTIFY_API_KEY" ] || [ "$PRINTIFY_API_KEY" == "your-printify-api-key" ]; then
    MISSING+=("PRINTIFY_API_KEY")
fi
if [ -z "$PRINTIFY_SHOP_ID" ] || [ "$PRINTIFY_SHOP_ID" == "your-shop-id" ]; then
    MISSING+=("PRINTIFY_SHOP_ID")
fi

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "${RED}✗ Missing required variables in .env:${NC}"
    for var in "${MISSING[@]}"; do
        echo "  - $var"
    done
    exit 1
fi
echo -e "${GREEN}✓ Configuration valid${NC}"

# Install Gateway dependencies
echo -e "${CYAN}▶ Setting up POD Gateway...${NC}"
cd gateway
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Gateway dependencies installed${NC}"

# Configure Gateway
if [ ! -f ".env" ]; then
    cat > .env << GATEWAY_ENV
PRINTIFY_API_KEY=$PRINTIFY_API_KEY
PRINTIFY_SHOP_ID=$PRINTIFY_SHOP_ID
POD_IMAGE_DIR=${POD_IMAGE_DIR:-/workspace/comfyui/output}
POD_STATE_FILE=${POD_STATE_FILE:-./state.json}
POD_ARCHIVE_DIR=${POD_ARCHIVE_DIR:-./archive}
FLASK_HOST=${FLASK_HOST:-0.0.0.0}
FLASK_PORT=${FLASK_PORT:-5000}
GATEWAY_ENV
fi

# Initialize state
if [ ! -f "state.json" ]; then
    echo '{"designs": []}' > state.json
fi

# Create directories
mkdir -p archive
cd ..
echo -e "${GREEN}✓ Gateway configured${NC}"

# Install Node dependencies
echo -e "${CYAN}▶ Installing Node.js dependencies...${NC}"
if [ ! -d "node_modules" ]; then
    npm install --silent
    echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Node.js dependencies already installed${NC}"
fi

# Setup ComfyUI if needed
if [ ! -d "ComfyUI" ]; then
    echo -e "${CYAN}▶ Setting up ComfyUI...${NC}"
    if [ -f "./scripts/setup-comfyui.sh" ]; then
        ./scripts/setup-comfyui.sh
        echo -e "${GREEN}✓ ComfyUI installed${NC}"
    else
        echo -e "${YELLOW}⚠ ComfyUI setup script not found, skipping...${NC}"
    fi
else
    echo -e "${GREEN}✓ ComfyUI already installed${NC}"
fi

# Create logs directory
mkdir -p logs

# Create startup scripts if they don't exist
if [ ! -f "start-pod-engine.sh" ]; then
    echo -e "${CYAN}▶ Creating startup scripts...${NC}"

    cat > start-pod-engine.sh << 'START_SCRIPT'
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

# Start Gateway
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
echo "  Web UI:       http://localhost:5173"
echo ""
echo -e "${CYAN}Logs: tail -f logs/*.log${NC}"
echo -e "${CYAN}Stop: ./stop-pod-engine.sh${NC}"
START_SCRIPT

    chmod +x start-pod-engine.sh

    cat > stop-pod-engine.sh << 'STOP_SCRIPT'
#!/bin/bash
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Stopping POD Engine..."

if [ -f logs/pod-engine.pids ]; then
    source logs/pod-engine.pids
    for pid_var in COMFYUI_PID GATEWAY_PID WEBUI_PID; do
        pid=${!pid_var}
        if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
            kill $pid
            echo -e "${GREEN}✓ Stopped $pid_var${NC}"
        fi
    done
    rm logs/pod-engine.pids
else
    echo -e "${RED}✗ No PID file found${NC}"
fi
STOP_SCRIPT

    chmod +x stop-pod-engine.sh
    echo -e "${GREEN}✓ Startup scripts created${NC}"
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Deployment Complete!                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo ""
echo -e "  1. Start services:"
echo -e "     ${YELLOW}./start-pod-engine.sh${NC}"
echo ""
echo -e "  2. Access services:"
echo "     • POD Gateway:  http://localhost:5000"
echo "     • ComfyUI:      http://localhost:8188"
echo "     • Web UI:       http://localhost:5173"
echo ""
echo -e "  3. Stop services:"
echo -e "     ${YELLOW}./stop-pod-engine.sh${NC}"
echo ""

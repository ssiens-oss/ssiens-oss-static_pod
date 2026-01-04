#!/bin/bash
# Production Deployment Script for RunPod
# Configures API keys and starts all services

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║     POD Engine - Production Deployment            ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running on RunPod
if [ ! -d "/workspace" ]; then
    echo -e "${RED}Error: This script must be run on RunPod (missing /workspace directory)${NC}"
    echo "For local testing, use: npm run dev"
    exit 1
fi

# Get current directory (should be /workspace/app)
APP_DIR=$(pwd)
echo -e "${GREEN}✓${NC} App directory: $APP_DIR"
echo ""

# Step 1: Configure API Keys
echo "════════════════════════════════════════════════════"
echo "Step 1: Configuring API Keys"
echo "════════════════════════════════════════════════════"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗${NC} .env file not found"
    echo "Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        exit 1
    fi
fi

# Prompt for API keys if not set
CURRENT_ANTHROPIC=$(grep "^ANTHROPIC_API_KEY=" .env | cut -d'=' -f2)
if [ "$CURRENT_ANTHROPIC" = "sk-ant-your-api-key-here" ] || [ -z "$CURRENT_ANTHROPIC" ]; then
    echo -e "${YELLOW}Anthropic API key not configured${NC}"
    read -p "Enter your Anthropic API key (sk-ant-...): " ANTHROPIC_KEY
    sed -i "s|sk-ant-your-api-key-here|$ANTHROPIC_KEY|" .env
    echo -e "${GREEN}✓${NC} Anthropic API key configured"
else
    echo -e "${GREEN}✓${NC} Anthropic API key already configured"
fi

CURRENT_PRINTIFY=$(grep "^PRINTIFY_API_KEY=" .env | cut -d'=' -f2)
if [ "$CURRENT_PRINTIFY" = "your-printify-api-key" ] || [ -z "$CURRENT_PRINTIFY" ]; then
    echo -e "${YELLOW}Printify API key not configured${NC}"
    read -p "Enter your Printify API key (JWT token): " PRINTIFY_KEY
    sed -i "s|your-printify-api-key|$PRINTIFY_KEY|" .env
    echo -e "${GREEN}✓${NC} Printify API key configured"
else
    echo -e "${GREEN}✓${NC} Printify API key already configured"
fi

CURRENT_SHOP=$(grep "^PRINTIFY_SHOP_ID=" .env | cut -d'=' -f2)
if [ "$CURRENT_SHOP" = "your-shop-id" ] || [ -z "$CURRENT_SHOP" ]; then
    echo -e "${YELLOW}Printify Shop ID not configured${NC}"
    read -p "Enter your Printify Shop ID: " SHOP_ID
    sed -i "s|your-shop-id|$SHOP_ID|" .env
    echo -e "${GREEN}✓${NC} Printify Shop ID configured"
else
    echo -e "${GREEN}✓${NC} Printify Shop ID already configured"
fi

echo ""

# Step 2: Clean up existing processes
echo "════════════════════════════════════════════════════"
echo "Step 2: Cleaning Up Existing Processes"
echo "════════════════════════════════════════════════════"
echo ""

# Kill ComfyUI processes
if pgrep -f "python.*main.py" > /dev/null; then
    echo "Killing existing ComfyUI processes..."
    pkill -f "python.*main.py" || true
    sleep 2
    echo -e "${GREEN}✓${NC} ComfyUI processes killed"
else
    echo -e "${GREEN}✓${NC} No existing ComfyUI processes"
fi

# Kill POD Engine processes
if pgrep -f "pod-engine-api" > /dev/null; then
    echo "Killing existing POD Engine processes..."
    pkill -f "pod-engine-api" || true
    sleep 2
    echo -e "${GREEN}✓${NC} POD Engine processes killed"
else
    echo -e "${GREEN}✓${NC} No existing POD Engine processes"
fi

# Verify ports are free
if netstat -tlnp 2>/dev/null | grep -q ":8188 "; then
    echo -e "${RED}✗${NC} Port 8188 still in use"
    echo "Waiting for port to be released..."
    sleep 5
fi

if netstat -tlnp 2>/dev/null | grep -q ":3000 "; then
    echo -e "${RED}✗${NC} Port 3000 still in use"
    echo "Waiting for port to be released..."
    sleep 5
fi

echo ""

# Step 3: Start ComfyUI
echo "════════════════════════════════════════════════════"
echo "Step 3: Starting ComfyUI"
echo "════════════════════════════════════════════════════"
echo ""

# Verify ComfyUI directory
if [ ! -d "/workspace/ComfyUI" ]; then
    echo -e "${RED}✗${NC} ComfyUI not found at /workspace/ComfyUI"
    echo "Running installation..."
    cd /workspace
    git clone https://github.com/comfyanonymous/ComfyUI
    cd ComfyUI
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓${NC} ComfyUI installed"
fi

cd /workspace/ComfyUI

# Check if model exists
MODEL_DIR="/workspace/ComfyUI/models/checkpoints"
if [ ! -f "$MODEL_DIR/v1-5-pruned-emaonly.safetensors" ]; then
    echo "Downloading SD 1.5 model..."
    mkdir -p "$MODEL_DIR"
    wget -q -O "$MODEL_DIR/v1-5-pruned-emaonly.safetensors" \
        "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
    echo -e "${GREEN}✓${NC} Model downloaded"
else
    echo -e "${GREEN}✓${NC} SD 1.5 model found"
fi

# Install required Python packages
echo "Verifying Python dependencies..."
REQUIRED_PACKAGES="tqdm torch torchsde transformers aiohttp safetensors"
MISSING=""

for pkg in $REQUIRED_PACKAGES; do
    if ! python -c "import $pkg" 2>/dev/null; then
        MISSING="$MISSING $pkg"
    fi
done

if [ ! -z "$MISSING" ]; then
    echo "Installing missing packages:$MISSING"
    pip install -q $MISSING
    echo -e "${GREEN}✓${NC} Python dependencies installed"
else
    echo -e "${GREEN}✓${NC} All Python dependencies present"
fi

# Start ComfyUI
echo "Starting ComfyUI..."
mkdir -p /workspace/logs
python main.py --listen 0.0.0.0 --port 8188 > /workspace/logs/comfyui.log 2>&1 &
COMFYUI_PID=$!

echo "Waiting for ComfyUI to start (this may take 30-60 seconds)..."
for i in {1..30}; do
    if curl -s http://localhost:8188 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} ComfyUI is running (PID: $COMFYUI_PID)"
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# Verify ComfyUI is responding
if ! curl -s http://localhost:8188 > /dev/null 2>&1; then
    echo -e "${RED}✗${NC} ComfyUI failed to start"
    echo "Check logs: tail -f /workspace/logs/comfyui.log"
    exit 1
fi

echo ""

# Step 4: Start POD Engine API
echo "════════════════════════════════════════════════════"
echo "Step 4: Starting POD Engine API"
echo "════════════════════════════════════════════════════"
echo ""

cd "$APP_DIR"

# Install Node dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    echo -e "${GREEN}✓${NC} Node.js dependencies installed"
else
    echo -e "${GREEN}✓${NC} Node.js dependencies found"
fi

# Start POD Engine
echo "Starting POD Engine API..."
npx tsx pod-engine-api.ts > /workspace/logs/pod-engine.log 2>&1 &
POD_ENGINE_PID=$!

echo "Waiting for POD Engine to start..."
for i in {1..15}; do
    if curl -s http://localhost:3000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} POD Engine is running (PID: $POD_ENGINE_PID)"
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# Verify POD Engine is responding
if ! curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo -e "${RED}✗${NC} POD Engine failed to start"
    echo "Check logs: tail -f /workspace/logs/pod-engine.log"
    exit 1
fi

echo ""

# Step 5: Verify Installation
echo "════════════════════════════════════════════════════"
echo "Step 5: Verifying Installation"
echo "════════════════════════════════════════════════════"
echo ""

# Check API health
HEALTH=$(curl -s http://localhost:3000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} POD Engine API is healthy"
    echo "$HEALTH" | grep -o '"uptime":[0-9]*' | awk -F':' '{print "  Uptime: " $2 "s"}'
else
    echo -e "${RED}✗${NC} POD Engine health check failed"
fi

# Check directories
echo ""
echo "Directory structure:"
for dir in "/workspace/data/designs" "/workspace/data/mockups" "/workspace/data/mockup-templates"; do
    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}✓${NC} $dir"
    else
        echo -e "  ${YELLOW}!${NC} $dir (will be created on first use)"
    fi
done

echo ""

# Summary
echo "════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════"
echo ""
echo "Services Running:"
echo "  • ComfyUI:        http://localhost:8188"
echo "  • POD Engine API: http://localhost:3000"
echo "  • Monitor GUI:    http://localhost:8080/monitor.html"
echo ""
echo "Process IDs:"
echo "  • ComfyUI:        $COMFYUI_PID"
echo "  • POD Engine:     $POD_ENGINE_PID"
echo ""
echo "Logs:"
echo "  • ComfyUI:        tail -f /workspace/logs/comfyui.log"
echo "  • POD Engine:     tail -f /workspace/logs/pod-engine.log"
echo ""
echo "Next Steps:"
echo "  1. Test the API:"
echo "     curl -X POST http://localhost:3000/api/generate \\"
echo "       -H \"Content-Type: application/json\" \\"
echo "       -d '{\"prompt\": \"Urban geometric art\", \"productTypes\": [\"tshirt\"]}'"
echo ""
echo "  2. Access from local machine via SSH port forwarding:"
echo "     ssh -L 3000:localhost:3000 -L 8080:localhost:8080 -L 8188:localhost:8188 <runpod-connection>"
echo ""
echo "  3. Monitor jobs:"
echo "     curl http://localhost:3000/api/jobs | jq ."
echo ""
echo "════════════════════════════════════════════════════"

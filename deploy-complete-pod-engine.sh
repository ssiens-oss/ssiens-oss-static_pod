#!/bin/bash
#
# Complete POD Engine Deployment Script
# Deploys both TypeScript orchestrator and Python automation
#

set -e

echo "======================================================================"
echo "  StaticWaves Complete POD Engine Deployment"
echo "======================================================================"
echo ""

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect environment
if [ -d "/workspace" ]; then
    ENV="runpod"
    echo "🚀 Detected RunPod environment"
else
    ENV="local"
    echo "💻 Detected local environment"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env with your API keys before continuing${NC}"
    echo "   Required: PRINTIFY_API_KEY, PRINTIFY_SHOP_ID, ANTHROPIC_API_KEY"
    exit 1
fi

echo ""
echo "======================================================================"
echo "  Step 1: Installing Dependencies"
echo "======================================================================"
echo ""

# Node.js dependencies
if command -v npm &> /dev/null; then
    echo "📦 Installing Node.js dependencies..."
    npm install
    echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  npm not found, skipping TypeScript orchestrator${NC}"
fi

# Python dependencies
if command -v python3 &> /dev/null; then
    echo "🐍 Installing Python dependencies..."

    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        echo "Creating requirements.txt..."
        cat > requirements.txt <<EOF
python-dotenv>=1.0.0
requests>=2.31.0
Pillow>=10.0.0
EOF
    fi

    pip install -r requirements.txt
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${RED}Error: Python 3 not found${NC}"
    exit 1
fi

echo ""
echo "======================================================================"
echo "  Step 2: Configuring Services"
echo "======================================================================"
echo ""

# Load environment variables
source .env

# Validate critical variables
if [ -z "$PRINTIFY_API_KEY" ] || [ "$PRINTIFY_API_KEY" == "your-printify-api-key" ]; then
    echo -e "${RED}Error: PRINTIFY_API_KEY not set in .env${NC}"
    exit 1
fi

if [ -z "$PRINTIFY_SHOP_ID" ] || [ "$PRINTIFY_SHOP_ID" == "your-shop-id" ]; then
    echo -e "${RED}Error: PRINTIFY_SHOP_ID not set in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Configuration validated${NC}"
echo "  - Printify API Key: ${PRINTIFY_API_KEY:0:20}..."
echo "  - Printify Shop ID: $PRINTIFY_SHOP_ID"
echo "  - Auto-publish: ${AUTO_PUBLISH:-true}"
echo "  - T-Shirt Price: \$${DEFAULT_TSHIRT_PRICE:-19.99}"
echo "  - Hoodie Price: \$${DEFAULT_HOODIE_PRICE:-34.99}"

echo ""
echo "======================================================================"
echo "  Step 3: Deployment Mode Selection"
echo "======================================================================"
echo ""
echo "Select deployment mode:"
echo "  1) Full Stack (TypeScript UI + Python automation)"
echo "  2) RunPod Automation Only (headless)"
echo "  3) TypeScript Orchestrator Only"
echo ""
read -p "Enter choice [1-3]: " deployment_mode

case $deployment_mode in
    1)
        echo ""
        echo "🚀 Deploying Full Stack..."
        echo ""

        # Build TypeScript
        if command -v npm &> /dev/null; then
            echo "Building TypeScript application..."
            npm run build
            echo -e "${GREEN}✓ Build complete${NC}"
        fi

        # Copy Python scripts to workspace
        if [ "$ENV" == "runpod" ]; then
            echo "Copying Python scripts to /workspace..."
            cp scripts/runpod_push_to_printify.py /workspace/
            chmod +x /workspace/runpod_push_to_printify.py
            echo -e "${GREEN}✓ Python scripts deployed${NC}"
        fi

        echo ""
        echo "======================================================================"
        echo "  Deployment Complete!"
        echo "======================================================================"
        echo ""
        echo "Next steps:"
        echo ""
        echo "  1. Start ComfyUI:"
        echo "     cd ComfyUI && python3 main.py --listen 0.0.0.0 --port 8188"
        echo ""
        echo "  2. Start Web UI:"
        echo "     npm run dev"
        echo ""
        echo "  3. Access UI at: http://localhost:5173"
        echo ""
        echo "  4. For batch automation, run:"
        echo "     python3 scripts/runpod_push_to_printify.py"
        echo ""
        ;;

    2)
        echo ""
        echo "🤖 Deploying RunPod Automation..."
        echo ""

        # Copy script to /workspace if on RunPod
        if [ "$ENV" == "runpod" ]; then
            cp scripts/runpod_push_to_printify.py /workspace/
            chmod +x /workspace/runpod_push_to_printify.py
            echo -e "${GREEN}✓ Script deployed to /workspace/${NC}"
        fi

        echo ""
        echo "======================================================================"
        echo "  Deployment Complete!"
        echo "======================================================================"
        echo ""
        echo "Run automation with:"
        echo "  python3 /workspace/runpod_push_to_printify.py"
        echo ""
        echo "Or schedule with cron:"
        echo "  crontab -e"
        echo "  0 2 * * * cd /workspace && python3 runpod_push_to_printify.py"
        echo ""
        ;;

    3)
        echo ""
        echo "🎨 Deploying TypeScript Orchestrator..."
        echo ""

        # Build TypeScript
        if command -v npm &> /dev/null; then
            echo "Building TypeScript application..."
            npm run build
            echo -e "${GREEN}✓ Build complete${NC}"
        fi

        echo ""
        echo "======================================================================"
        echo "  Deployment Complete!"
        echo "======================================================================"
        echo ""
        echo "Next steps:"
        echo ""
        echo "  1. Start ComfyUI:"
        echo "     cd ComfyUI && python3 main.py --listen 0.0.0.0 --port 8188"
        echo ""
        echo "  2. Start Web UI:"
        echo "     npm run dev"
        echo ""
        echo "  3. Access UI at: http://localhost:5173"
        echo ""
        ;;

    *)
        echo -e "${RED}Invalid selection${NC}"
        exit 1
        ;;
esac

echo ""
echo "📚 Documentation:"
echo "  - Complete Guide: POD_ENGINE_INTEGRATION.md"
echo "  - Quick Start: README.md"
echo "  - Printify Docs: scripts/README_PRINTIFY.md"
echo ""
echo -e "${GREEN}✓ Deployment successful!${NC}"

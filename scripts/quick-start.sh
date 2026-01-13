#!/bin/bash
# Quick Start Script - Get running in 60 seconds!

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║        🚀 POD Pipeline - Quick Start (60 seconds)          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Docker
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo -e "${BLUE}▶${NC} Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    # Set local defaults
    sed -i.bak 's|COMFYUI_API_URL=.*|COMFYUI_API_URL=http://localhost:8188|g' .env
    sed -i.bak 's|STORAGE_TYPE=.*|STORAGE_TYPE=local|g' .env
    sed -i.bak 's|STORAGE_PATH=.*|STORAGE_PATH=./data/designs|g' .env
    # Enable local prompts (free mode)
    echo "USE_LOCAL_PROMPTS=true" >> .env
    rm .env.bak 2>/dev/null || true
fi

echo -e "${BLUE}▶${NC} Creating directories..."
mkdir -p data/designs comfyui-data/models/checkpoints comfyui-data/output

echo -e "${BLUE}▶${NC} Starting services..."
docker-compose up -d

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🌐 Web UI:       http://localhost:5173"
echo "  🎨 ComfyUI:      http://localhost:8188"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo ""
echo "  1. Wait 30 seconds for services to start"
echo "  2. Open http://localhost:5173"
echo "  3. Click 'Run Single Drop' to test"
echo ""
echo "⚠️  First time? Download the SDXL model:"
echo "    ./scripts/setup-local.sh"
echo ""
echo "📚 Full guide: FREE_DEPLOYMENT.md"
echo ""
echo "💡 Stop services: docker-compose down"
echo ""

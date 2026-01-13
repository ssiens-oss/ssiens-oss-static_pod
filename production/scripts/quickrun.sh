#!/bin/bash

# Quick Setup and Run Script for Production POD Engine

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║   🚀 Production POD Engine - Quick Setup & Run          ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists and has API key
if [ -f "production/.env" ]; then
    source production/.env

    if [ "$CLAUDE_API_KEY" = "sk-ant-your-api-key-here" ] || [ -z "$CLAUDE_API_KEY" ]; then
        echo -e "${YELLOW}⚠️  Claude API key not configured${NC}"
        echo ""
        echo "Please enter your Claude API key:"
        echo -n "> "
        read -r API_KEY

        if [ ! -z "$API_KEY" ]; then
            # Update .env file with the API key
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' "s/CLAUDE_API_KEY=.*/CLAUDE_API_KEY=$API_KEY/" production/.env
            else
                # Linux
                sed -i "s/CLAUDE_API_KEY=.*/CLAUDE_API_KEY=$API_KEY/" production/.env
            fi
            echo -e "${GREEN}✅ API key saved to production/.env${NC}"
        else
            echo -e "${RED}❌ No API key provided${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Claude API key is configured${NC}"
    fi
else
    echo -e "${RED}❌ production/.env not found${NC}"
    exit 1
fi

echo ""

# Check ComfyUI
echo "🔍 Checking ComfyUI..."
COMFYUI_URL=${COMFYUI_API_URL:-http://127.0.0.1:8188}

if curl -f -s -m 3 "$COMFYUI_URL/system_stats" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ComfyUI is running at $COMFYUI_URL${NC}"
else
    echo -e "${YELLOW}⚠️  ComfyUI is not running${NC}"
    echo ""
    echo "ComfyUI must be running before starting the engine."
    echo ""
    echo "Start ComfyUI in another terminal:"
    echo "  cd /path/to/ComfyUI"
    echo "  python main.py"
    echo ""
    echo -n "Continue anyway? [y/N]: "
    read -r CONTINUE

    if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
        echo "Exiting. Please start ComfyUI first."
        exit 1
    fi
fi

echo ""
echo "🎛️  Choose run mode:"
echo ""
echo "  1) Production (Worker Pool + API) - Recommended"
echo "     • 3 workers processing jobs in parallel"
echo "     • REST API on http://localhost:3000"
echo "     • Auto-retry on failures"
echo ""
echo "  2) Development (Single Worker)"
echo "     • One worker for testing"
echo "     • No API server"
echo ""
echo "  3) Docker (Complete Stack)"
echo "     • PostgreSQL, Redis, ComfyUI, Engine"
echo "     • Requires Docker"
echo ""
echo -n "Select [1-3, default: 1]: "
read -r MODE

MODE=${MODE:-1}

echo ""
echo "════════════════════════════════════════════════════════════"

case $MODE in
    1)
        echo -e "${BLUE}🚀 Starting Production Mode (Worker Pool + API)${NC}"
        echo ""
        echo "The engine will start on:"
        echo "  • API: http://localhost:3000"
        echo "  • Workers: 3"
        echo ""
        echo "Press Ctrl+C to stop"
        echo ""
        sleep 2

        npm run production:api
        ;;

    2)
        echo -e "${BLUE}🚀 Starting Development Mode (Single Worker)${NC}"
        echo ""
        echo "Press Ctrl+C to stop"
        echo ""
        sleep 2

        npm run production:worker
        ;;

    3)
        echo -e "${BLUE}🚀 Starting Docker Mode${NC}"
        echo ""

        if ! command -v docker-compose >/dev/null 2>&1; then
            echo -e "${RED}❌ Docker Compose not found${NC}"
            echo "Please install Docker first"
            exit 1
        fi

        echo "Starting Docker services..."
        npm run production:docker

        echo ""
        echo -e "${GREEN}✅ Docker services started${NC}"
        echo ""
        echo "Check status: cd production && docker-compose ps"
        echo "View logs: docker-compose logs -f pod-engine"
        echo "Stop: npm run production:stop"
        ;;

    *)
        echo -e "${RED}Invalid selection${NC}"
        exit 1
        ;;
esac

#!/bin/bash
set -e

echo "🚀 StaticWaves POD Studio - Complete RunPod Setup"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }

# =============================================================================
# PART 1: SYSTEM SETUP
# =============================================================================

echo "📦 Part 1: System Dependencies"
echo "================================"
echo ""

# Update system
print_info "Updating package lists..."
apt-get update -qq

# Install base tools
print_info "Installing base tools..."
apt-get install -y git curl wget nano netcat-openbsd python3-pip unzip > /dev/null 2>&1
print_status "Base tools installed"

# Install Node.js 20+
echo ""
print_info "Checking Node.js version..."
NODE_VERSION=$(node -v 2>/dev/null || echo "none")
if [[ "$NODE_VERSION" == "none" ]] || [[ ! "$NODE_VERSION" =~ ^v2[0-9] ]]; then
    print_warning "Installing Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi
print_status "Node.js $(node -v) installed"

# Install PM2
if ! command -v pm2 &> /dev/null; then
    print_info "Installing PM2..."
    npm install -g pm2 --silent
fi
print_status "PM2 installed"

# =============================================================================
# PART 2: COMFYUI / FORGE SETUP
# =============================================================================

echo ""
echo "🎨 Part 2: ComfyUI / Forge Setup"
echo "================================="
echo ""

# Check if GPU is available
if nvidia-smi &> /dev/null; then
    print_status "NVIDIA GPU detected!"
    nvidia-smi --query-gpu=name --format=csv,noheader
    HAS_GPU=true
else
    print_warning "No NVIDIA GPU detected - will use placeholder images"
    HAS_GPU=false
fi

# Check if Forge is already running on port 3000
if nc -z localhost 3000 2>/dev/null; then
    print_status "Forge/ComfyUI already running on port 3000"
    COMFYUI_RUNNING=true
else
    COMFYUI_RUNNING=false

    if [ "$HAS_GPU" = true ]; then
        print_info "Setting up ComfyUI for AI image generation..."

        # Install ComfyUI if not present
        if [ ! -d ~/ComfyUI ]; then
            print_info "Cloning ComfyUI repository..."
            cd ~
            git clone https://github.com/comfyanonymous/ComfyUI.git
            cd ComfyUI

            # Install dependencies
            print_info "Installing ComfyUI dependencies..."
            pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 --quiet
            pip3 install -r requirements.txt --quiet

            # Download SD 1.5 model if not present
            if [ ! -f models/checkpoints/sd_v1-5.safetensors ]; then
                print_info "Downloading Stable Diffusion 1.5 model (4GB)..."
                mkdir -p models/checkpoints
                wget -q --show-progress -O models/checkpoints/sd_v1-5.safetensors \
                    "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
            fi

            print_status "ComfyUI installed"
        fi

        # Start ComfyUI in background
        print_info "Starting ComfyUI on port 8188..."
        cd ~/ComfyUI
        pm2 start "python3 main.py --listen 0.0.0.0 --port 8188" --name comfyui

        # Wait for ComfyUI to start
        sleep 5
        if curl -s http://localhost:8188/system_stats > /dev/null; then
            print_status "ComfyUI started successfully"
            COMFYUI_RUNNING=true
        else
            print_warning "ComfyUI may still be starting..."
        fi
    else
        print_info "Skipping ComfyUI setup (no GPU) - will use placeholder images"
    fi
fi

# =============================================================================
# PART 3: POD STUDIO API SETUP
# =============================================================================

echo ""
echo "🛍️  Part 3: POD Studio API Setup"
echo "================================="
echo ""

# Navigate to project
cd ~/ssiens-oss-static_pod || {
    print_error "Project directory not found at ~/ssiens-oss-static_pod"
    print_info "Please clone the repository first:"
    print_info "  cd ~"
    print_info "  git clone <repo-url> ssiens-oss-static_pod"
    exit 1
}

# Pull latest code
print_info "Pulling latest code..."
git fetch origin claude/repo-analysis-g6UHk
git checkout claude/repo-analysis-g6UHk
git pull origin claude/repo-analysis-g6UHk
print_status "Code updated"

# Check .env
echo ""
if [ ! -f .env ]; then
    print_error ".env file not found!"
    echo ""
    echo "Create .env with:"
    echo "  ANTHROPIC_API_KEY=sk-ant-api03-..."
    echo "  CLAUDE_MODEL=claude-3-haiku-20240307"
    echo "  PRINTIFY_API_KEY=eyJ0eXAi..."
    echo "  PRINTIFY_SHOP_ID=25860767"
    echo ""
    exit 1
fi

# Update .env with ComfyUI URL if running
if [ "$COMFYUI_RUNNING" = true ]; then
    if grep -q "COMFYUI_API_URL" .env; then
        sed -i 's|COMFYUI_API_URL=.*|COMFYUI_API_URL=http://localhost:8188|' .env
    else
        echo "COMFYUI_API_URL=http://localhost:8188" >> .env
    fi
    print_status "ComfyUI URL configured in .env"
fi

print_status ".env file found"

# Install dependencies
echo ""
print_info "Installing npm dependencies..."
npm install --silent
print_status "Dependencies installed"

# Build frontend
print_info "Building frontend..."
npm run build
print_status "Frontend built"

# =============================================================================
# PART 4: START SERVICES
# =============================================================================

echo ""
echo "🚀 Part 4: Starting Services"
echo "============================="
echo ""

# Clean up old processes
print_info "Cleaning up old processes..."
pm2 delete pod-studio-api 2>/dev/null || true
pkill -f "tsx.*server.ts" 2>/dev/null || true
sleep 2
print_status "Cleanup complete"

# Start API server
print_info "Starting POD Studio API on port 3001..."
pm2 start "npm run dev:server" --name pod-studio-api
pm2 save > /dev/null 2>&1
print_status "API server started"

# Wait for server
sleep 3

# =============================================================================
# PART 5: HEALTH CHECKS
# =============================================================================

echo ""
echo "🏥 Part 5: Health Checks"
echo "========================"
echo ""

# Test API health
MAX_RETRIES=10
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:3001/health > /dev/null; then
        print_status "API server is healthy"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_error "API server failed to start"
    pm2 logs pod-studio-api --lines 20 --nostream
    exit 1
fi

# Check services
CONFIG_TEST=$(curl -s http://localhost:3001/api/config/test)
echo "$CONFIG_TEST" | grep -q '"claude":true' && print_status "Claude AI: Connected" || print_warning "Claude AI: Not configured"
echo "$CONFIG_TEST" | grep -q '"printify":true' && print_status "Printify: Connected" || print_warning "Printify: Not configured"
echo "$CONFIG_TEST" | grep -q '"shopify":true' && print_status "Shopify: Connected" || print_warning "Shopify: Not configured"
echo "$CONFIG_TEST" | grep -q '"comfyui":true' && print_status "ComfyUI: Connected" || print_warning "ComfyUI: Using placeholders"

# =============================================================================
# PART 6: DISPLAY INFO
# =============================================================================

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 POD Studio is Ready!${NC}"
echo "=================================================="
echo ""

# Get RunPod ID from hostname
RUNPOD_ID=$(hostname | cut -d'-' -f1)

echo "📊 Running Services:"
pm2 list

echo ""
echo "🌐 Access URLs:"
if [ "$COMFYUI_RUNNING" = true ]; then
    echo "   ComfyUI/Forge:  https://${RUNPOD_ID}-8188.proxy.runpod.net"
fi
echo "   POD Dashboard:  https://${RUNPOD_ID}-3001.proxy.runpod.net"
echo "   API Health:     https://${RUNPOD_ID}-3001.proxy.runpod.net/health"
echo ""

echo "🔧 Local URLs (inside container):"
if [ "$COMFYUI_RUNNING" = true ]; then
    echo "   ComfyUI:  http://localhost:8188"
fi
echo "   API:      http://localhost:3001"
echo ""

echo "📝 Quick Commands:"
echo "   View logs:        pm2 logs"
echo "   Restart all:      pm2 restart all"
echo "   Stop all:         pm2 stop all"
echo "   Test Printify:    cd ~/ssiens-oss-static_pod && npx tsx test-printify.ts"
echo ""

if [ "$HAS_GPU" = true ] && [ "$COMFYUI_RUNNING" = true ]; then
    echo "🎨 AI Image Generation: ENABLED (Real Stable Diffusion)"
else
    echo "🎨 AI Image Generation: PLACEHOLDERS (No GPU or ComfyUI not running)"
fi

echo ""
echo "🧪 Test Production Run:"
echo "   1. Open: https://${RUNPOD_ID}-3001.proxy.runpod.net"
echo "   2. Enter theme: 'Cyberpunk streetwear'"
echo "   3. Enter style: 'Bold neon graphics'"
echo "   4. Set count: 3"
echo "   5. Click 'Run Pipeline'"
echo ""
echo "Ready to create POD products! 🚀"

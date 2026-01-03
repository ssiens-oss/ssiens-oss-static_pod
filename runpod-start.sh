#!/bin/bash

# RunPod Production Startup Script
# Starts all services for the POD Engine production environment

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║      POD Engine - RunPod Production Start         ║"
echo "╚════════════════════════════════════════════════════╝"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if running on RunPod
if [ ! -z "$RUNPOD_POD_ID" ]; then
    log "Running on RunPod (Pod ID: $RUNPOD_POD_ID)"
fi

# Create necessary directories
log "Creating directories..."
mkdir -p /workspace/data/designs
mkdir -p /workspace/data/comfyui/output
mkdir -p /workspace/data/chrome-profile
mkdir -p /workspace/data/pod-engine-state
mkdir -p /workspace/logs
log_success "Directories created"

# Check environment variables
log "Checking environment variables..."
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-your-api-key-here" ]; then
    log_warning "ANTHROPIC_API_KEY not set or using default value"
    log_warning "Set it in .env file or environment"
fi

# Check and install Node.js if needed
if ! command -v node &> /dev/null; then
    log "Node.js not found. Installing Node.js 20.x..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs

    # Verify installation succeeded
    if command -v node &> /dev/null; then
        log_success "Node.js installed: $(node --version)"
        log_success "npm installed: $(npm --version)"
    else
        log_error "Node.js installation failed!"
        exit 1
    fi
else
    log "Node.js found: $(node --version)"
fi

# Install/Start ComfyUI
COMFYUI_PATH=${COMFYUI_PATH:-/workspace/ComfyUI}

if [ ! -d "$COMFYUI_PATH" ]; then
    log "ComfyUI not found. Installing..."
    cd /workspace
    git clone https://github.com/comfyanonymous/ComfyUI.git ComfyUI
    cd ComfyUI
    log "Installing ComfyUI dependencies..."
    pip install -r requirements.txt
    log_success "ComfyUI installed"
else
    log "ComfyUI found at $COMFYUI_PATH"
fi

# Download Stable Diffusion model if not present
MODEL_DIR="$COMFYUI_PATH/models/checkpoints"
MODEL_FILE="v1-5-pruned-emaonly.safetensors"
mkdir -p "$MODEL_DIR"

if [ ! -f "$MODEL_DIR/$MODEL_FILE" ]; then
    log "Stable Diffusion model not found. Downloading..."
    log "This is a 4GB download and will take 2-3 minutes..."
    cd "$MODEL_DIR"
    wget -q --show-progress https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/$MODEL_FILE

    # Verify download
    if [ -f "$MODEL_FILE" ]; then
        FILE_SIZE=$(ls -lh "$MODEL_FILE" | awk '{print $5}')
        log_success "Model downloaded: $FILE_SIZE"

        # Verify file is not corrupt (should be ~4GB)
        ACTUAL_SIZE=$(stat -f%z "$MODEL_FILE" 2>/dev/null || stat -c%s "$MODEL_FILE" 2>/dev/null)
        if [ "$ACTUAL_SIZE" -lt 4000000000 ]; then
            log_warning "Model file seems smaller than expected. May be incomplete."
        fi
    else
        log_error "Model download failed!"
        log_error "You can download manually: wget https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/$MODEL_FILE"
    fi
else
    MODEL_COUNT=$(ls -1 $MODEL_DIR/*.safetensors 2>/dev/null | wc -l)
    log "AI model(s) found: $MODEL_COUNT checkpoint(s)"
    log "Using model: $MODEL_FILE"
fi

log "Starting ComfyUI..."
cd $COMFYUI_PATH
python main.py --listen 0.0.0.0 --port 8188 > /workspace/logs/comfyui.log 2>&1 &
COMFYUI_PID=$!
log_success "ComfyUI started (PID: $COMFYUI_PID)"

# Wait for ComfyUI to be ready
log "Waiting for ComfyUI to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:8188 > /dev/null 2>&1; then
        log_success "ComfyUI is ready!"
        break
    fi
    if [ $i -eq 60 ]; then
        log_error "ComfyUI failed to start within 60 seconds"
        exit 1
    fi
    sleep 2
done

# Install app dependencies if needed
APP_PATH=${APP_PATH:-/workspace/app}
cd "$APP_PATH"

# Check if node_modules exists and has required packages
NEEDS_INSTALL=false
if [ ! -d "node_modules" ]; then
    NEEDS_INSTALL=true
    log "node_modules not found. Installing dependencies..."
elif [ ! -d "node_modules/express" ] || [ ! -d "node_modules/tsx" ]; then
    NEEDS_INSTALL=true
    log "Required packages missing. Reinstalling dependencies..."
fi

if [ "$NEEDS_INSTALL" = true ]; then
    npm install

    # Verify critical packages installed
    if [ -d "node_modules/express" ] && [ -d "node_modules/tsx" ]; then
        PACKAGE_COUNT=$(ls -1 node_modules | wc -l)
        log_success "Dependencies installed: $PACKAGE_COUNT packages"
    else
        log_error "Dependency installation failed! Missing critical packages."
        log_error "Try running: cd $APP_PATH && npm install"
        exit 1
    fi
else
    PACKAGE_COUNT=$(ls -1 node_modules | wc -l)
    log "Dependencies found: $PACKAGE_COUNT packages"
fi

# Start POD Engine API
log "Starting POD Engine API..."
npm run engine > /workspace/logs/pod-engine.log 2>&1 &
POD_ENGINE_PID=$!
log_success "POD Engine API started (PID: $POD_ENGINE_PID)"

# Wait for POD Engine to be ready
log "Waiting for POD Engine to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000/health > /dev/null 2>&1; then
        log_success "POD Engine API is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "POD Engine failed to start within 30 seconds"
        exit 1
    fi
    sleep 2
done

# Start Monitoring GUI
log "Starting Monitoring GUI..."
npm run monitor > /workspace/logs/monitor.log 2>&1 &
MONITOR_PID=$!
log_success "Monitoring GUI started (PID: $MONITOR_PID)"

# Wait for Monitor to be ready
log "Waiting for Monitor to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        log_success "Monitoring GUI is ready!"
        break
    fi
    sleep 2
done

# Print status
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║              All Services Running!                 ║"
echo "╠════════════════════════════════════════════════════╣"
echo "║                                                    ║"
echo "║  📊 Monitoring GUI:  http://localhost:5173        ║"
echo "║  🔧 POD Engine API:  http://localhost:3000        ║"
echo "║  🎨 ComfyUI:         http://localhost:8188        ║"
echo "║                                                    ║"
echo "║  Process IDs:                                      ║"
echo "║    ComfyUI:   $COMFYUI_PID"
echo "║    Engine:    $POD_ENGINE_PID"
echo "║    Monitor:   $MONITOR_PID"
echo "║                                                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Save PIDs for later use
echo "COMFYUI_PID=$COMFYUI_PID" > /workspace/.service_pids
echo "POD_ENGINE_PID=$POD_ENGINE_PID" >> /workspace/.service_pids
echo "MONITOR_PID=$MONITOR_PID" >> /workspace/.service_pids

log_success "All services started successfully!"
log "Logs are available in /workspace/logs/"

# Function to handle shutdown
shutdown() {
    echo ""
    log "Shutting down services..."

    if [ ! -z "$MONITOR_PID" ]; then
        log "Stopping Monitor (PID: $MONITOR_PID)..."
        kill $MONITOR_PID 2>/dev/null || true
    fi

    if [ ! -z "$POD_ENGINE_PID" ]; then
        log "Stopping POD Engine (PID: $POD_ENGINE_PID)..."
        kill -TERM $POD_ENGINE_PID 2>/dev/null || true
        sleep 2
    fi

    if [ ! -z "$COMFYUI_PID" ]; then
        log "Stopping ComfyUI (PID: $COMFYUI_PID)..."
        kill $COMFYUI_PID 2>/dev/null || true
    fi

    log_success "All services stopped"
    exit 0
}

# Trap signals
trap shutdown SIGTERM SIGINT

# Keep script running and tail logs
log "Following logs... (Ctrl+C to stop)"
echo ""
tail -f /workspace/logs/*.log

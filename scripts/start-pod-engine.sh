#!/bin/bash
# Start Pod Engine - Complete startup for all services
# This script starts ComfyUI, Music API, Music Worker, and Redis

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "\n${PURPLE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Configuration
COMFYUI_DIR="${COMFYUI_DIR:-./ComfyUI}"
COMFYUI_PORT="${COMFYUI_PORT:-8188}"
MUSIC_API_PORT="${MUSIC_API_PORT:-8000}"
REDIS_PORT="${REDIS_PORT:-6379}"
WEB_PORT="${WEB_PORT:-5173}"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    print_success "Virtual environment activated"
else
    print_warning "Virtual environment not found. Run ./scripts/setup-pod-engine.sh first"
fi

# Banner
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗  ██████╗ ██████╗     ███████╗███╗   ██╗ ██████╗   ║
║   ██╔══██╗██╔═══██╗██╔══██╗    ██╔════╝████╗  ██║██╔════╝   ║
║   ██████╔╝██║   ██║██║  ██║    █████╗  ██╔██╗ ██║██║  ███╗  ║
║   ██╔═══╝ ██║   ██║██║  ██║    ██╔══╝  ██║╚██╗██║██║   ██║  ║
║   ██║     ╚██████╔╝██████╔╝    ███████╗██║ ╚████║╚██████╔╝  ║
║   ╚═╝      ╚═════╝ ╚═════╝     ╚══════╝╚═╝  ╚═══╝ ╚═════╝   ║
║                                                               ║
║           Complete Pod Engine - Starting Services            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

print_header "Starting Pod Engine Services"

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0

    print_step "Waiting for $name to be ready..."

    while [ $attempt -lt $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|404"; then
            print_success "$name is ready!"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    print_error "$name failed to start"
    return 1
}

# Create logs directory
mkdir -p logs

# Step 1: Start Redis
print_header "Step 1/5: Starting Redis"

if check_port $REDIS_PORT; then
    print_warning "Redis already running on port $REDIS_PORT"
else
    print_step "Starting Redis on port $REDIS_PORT..."
    redis-server --port $REDIS_PORT --daemonize yes --dir ./data --logfile logs/redis.log
    sleep 2

    if check_port $REDIS_PORT; then
        print_success "Redis started successfully"
    else
        print_error "Failed to start Redis"
        exit 1
    fi
fi

# Step 2: Start ComfyUI
print_header "Step 2/5: Starting ComfyUI"

if check_port $COMFYUI_PORT; then
    print_warning "ComfyUI already running on port $COMFYUI_PORT"
else
    if [ ! -d "$COMFYUI_DIR" ]; then
        print_error "ComfyUI directory not found: $COMFYUI_DIR"
        print_step "Run ./scripts/setup-pod-engine.sh first to install ComfyUI"
        exit 1
    fi

    print_step "Starting ComfyUI on port $COMFYUI_PORT..."
    cd "$COMFYUI_DIR"
    nohup python main.py --listen 0.0.0.0 --port $COMFYUI_PORT > ../logs/comfyui.log 2>&1 &
    cd ..

    wait_for_service "http://localhost:$COMFYUI_PORT" "ComfyUI"
fi

# Step 3: Start Music API
print_header "Step 3/5: Starting Music API"

if check_port $MUSIC_API_PORT; then
    print_warning "Music API already running on port $MUSIC_API_PORT"
else
    print_step "Starting Music API on port $MUSIC_API_PORT..."

    # Set environment variables
    export REDIS_HOST=localhost
    export REDIS_PORT=$REDIS_PORT
    export OUTPUT_DIR=./data/output

    mkdir -p ./data/output

    nohup python -m uvicorn music-engine.api.main:app \
        --host 0.0.0.0 \
        --port $MUSIC_API_PORT \
        > logs/music-api.log 2>&1 &

    wait_for_service "http://localhost:$MUSIC_API_PORT/health" "Music API"
fi

# Step 4: Start Music Worker
print_header "Step 4/5: Starting Music Worker"

print_step "Starting Music Worker (GPU)..."

# Set environment variables
export REDIS_HOST=localhost
export REDIS_PORT=$REDIS_PORT
export OUTPUT_DIR=./data/output
export MUSICGEN_MODEL=facebook/musicgen-medium

nohup python music-engine/worker/worker.py > logs/music-worker.log 2>&1 &
WORKER_PID=$!

sleep 3

if ps -p $WORKER_PID > /dev/null; then
    print_success "Music Worker started (PID: $WORKER_PID)"
else
    print_warning "Music Worker may not have started correctly (check logs/music-worker.log)"
fi

# Step 5: Show service status
print_header "Step 5/5: Service Status"

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                     Services Started                          ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║                                                               ║"
echo "║  🎨 ComfyUI:        http://localhost:$COMFYUI_PORT                     ║"
echo "║  🎵 Music API:      http://localhost:$MUSIC_API_PORT                      ║"
echo "║  💾 Redis:          localhost:$REDIS_PORT                          ║"
echo "║  ⚙️  Music Worker:   Running (GPU)                            ║"
echo "║                                                               ║"
echo "║  📊 API Docs:       http://localhost:$MUSIC_API_PORT/docs               ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

print_header "Logs"

echo "Logs are being written to:"
echo "  - logs/redis.log"
echo "  - logs/comfyui.log"
echo "  - logs/music-api.log"
echo "  - logs/music-worker.log"
echo ""
echo "To view logs in real-time:"
echo "  tail -f logs/music-worker.log"
echo ""

print_header "Next Steps"

echo "To start the web UI:"
echo "  npm run dev          # POD Pipeline UI (port $WEB_PORT)"
echo "  npm run dev:music    # Music Studio UI"
echo ""
echo "To generate music:"
echo "  curl http://localhost:$MUSIC_API_PORT/generate/auto"
echo ""
echo "To stop all services:"
echo "  ./scripts/stop-pod-engine.sh"
echo ""

print_success "Pod Engine is ready! 🚀"

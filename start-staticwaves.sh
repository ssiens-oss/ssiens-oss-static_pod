#!/bin/bash

###############################################################################
# StaticWaves AI Music System - One-Command Startup
# Starts all services for the complete music generation platform
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   ███████╗████████╗ █████╗ ████████╗██╗ ██████╗           ║
║   ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██║██╔════╝           ║
║   ███████╗   ██║   ███████║   ██║   ██║██║                ║
║   ╚════██║   ██║   ██╔══██║   ██║   ██║██║                ║
║   ███████║   ██║   ██║  ██║   ██║   ██║╚██████╗           ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝           ║
║                                                            ║
║   ██╗    ██╗ █████╗ ██╗   ██╗███████╗███████╗             ║
║   ██║    ██║██╔══██╗██║   ██║██╔════╝██╔════╝             ║
║   ██║ █╗ ██║███████║██║   ██║█████╗  ███████╗             ║
║   ██║███╗██║██╔══██║╚██╗ ██╔╝██╔══╝  ╚════██║             ║
║   ╚███╔███╔╝██║  ██║ ╚████╔╝ ███████╗███████║             ║
║    ╚══╝╚══╝ ╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝             ║
║                                                            ║
║              AI Music Generation Platform                  ║
║                    Version 1.0.0                           ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Function to print status messages
print_status() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check dependencies
print_status "Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi
print_success "Python 3 found"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi
print_success "Node.js found"

# Check Redis (optional, will start with Docker if not found)
if command -v redis-server &> /dev/null; then
    print_success "Redis found"
    HAS_REDIS=true
else
    print_warning "Redis not found - will use Docker"
    HAS_REDIS=false
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p logs
mkdir -p data/output
mkdir -p models/ddsp
print_success "Directories created"

# Setup Python virtual environment for music engine
print_status "Setting up Python environment..."
if [ ! -d "music-engine/.venv" ]; then
    python3 -m venv music-engine/.venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment exists"
fi

# Activate venv and install dependencies
source music-engine/.venv/bin/activate
pip install -q -r music-engine/requirements-api.txt
pip install -q -r music-engine/requirements-worker.txt
print_success "Python dependencies installed"

# Setup Node.js dependencies for GUI
print_status "Setting up Node.js dependencies..."
cd mashdeck/gui/web
if [ ! -d "node_modules" ]; then
    npm install --silent
    print_success "Node modules installed"
else
    print_success "Node modules exist"
fi
cd ../../..

# Start Redis
print_status "Starting Redis..."
if [ "$HAS_REDIS" = true ]; then
    redis-server --daemonize yes --port 6379 > logs/redis.log 2>&1
    print_success "Redis started on port 6379"
else
    # Use Docker
    if command -v docker &> /dev/null; then
        docker run -d --name staticwaves-redis -p 6379:6379 redis:alpine > /dev/null 2>&1 || true
        print_success "Redis Docker container started"
    else
        print_error "Neither Redis nor Docker found. Please install one."
        exit 1
    fi
fi

# Start Music API
print_status "Starting Music API server..."
cd music-engine
source .venv/bin/activate
nohup python api/main.py > ../logs/music-api.log 2>&1 &
API_PID=$!
echo $API_PID > ../logs/music-api.pid
cd ..
sleep 2

# Check if API started successfully
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "Music API started on http://localhost:8000 (PID: $API_PID)"
else
    print_error "Failed to start Music API"
    cat logs/music-api.log
    exit 1
fi

# Start DDSP WebSocket server
print_status "Starting DDSP WebSocket server..."
cd music-engine
source .venv/bin/activate
nohup python worker/ddsp_websocket_server.py > ../logs/ddsp-server.log 2>&1 &
DDSP_PID=$!
echo $DDSP_PID > ../logs/ddsp-server.pid
cd ..
sleep 2
print_success "DDSP server started on ws://localhost:8765 (PID: $DDSP_PID)"

# Start Music Worker (for offline generation)
print_status "Starting Music Worker..."
cd music-engine
source .venv/bin/activate
nohup python worker/worker.py > ../logs/music-worker.log 2>&1 &
WORKER_PID=$!
echo $WORKER_PID > ../logs/music-worker.pid
cd ..
sleep 1
print_success "Music Worker started (PID: $WORKER_PID)"

# Start GUI
print_status "Starting Web GUI..."
cd mashdeck/gui/web
nohup npm run dev > ../../../logs/gui.log 2>&1 &
GUI_PID=$!
echo $GUI_PID > ../../../logs/gui.pid
cd ../../..
sleep 3

# Find the actual port (Vite might use 3001 if 3000 is busy)
GUI_PORT=$(grep -oP 'Local:\s+http://localhost:\K\d+' logs/gui.log | head -1)
if [ -z "$GUI_PORT" ]; then
    GUI_PORT=3001
fi

print_success "Web GUI started on http://localhost:$GUI_PORT (PID: $GUI_PID)"

# Print summary
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ StaticWaves is now running!${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Services:${NC}"
echo -e "  ${BLUE}•${NC} Music API:        ${GREEN}http://localhost:8000${NC}"
echo -e "  ${BLUE}•${NC} API Docs:         ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  ${BLUE}•${NC} DDSP WebSocket:   ${GREEN}ws://localhost:8765${NC}"
echo -e "  ${BLUE}•${NC} Web GUI:          ${GREEN}http://localhost:$GUI_PORT${NC}"
echo -e "  ${BLUE}•${NC} Redis:            ${GREEN}localhost:6379${NC}"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo -e "  ${BLUE}•${NC} API:              ${CYAN}tail -f logs/music-api.log${NC}"
echo -e "  ${BLUE}•${NC} DDSP Server:      ${CYAN}tail -f logs/ddsp-server.log${NC}"
echo -e "  ${BLUE}•${NC} Worker:           ${CYAN}tail -f logs/music-worker.log${NC}"
echo -e "  ${BLUE}•${NC} GUI:              ${CYAN}tail -f logs/gui.log${NC}"
echo ""
echo -e "${YELLOW}Features:${NC}"
echo -e "  ${GREEN}✓${NC} Real-time DDSP instrument synthesis"
echo -e "  ${GREEN}✓${NC} WebSocket audio streaming"
echo -e "  ${GREEN}✓${NC} Multi-layer ensemble composition"
echo -e "  ${GREEN}✓${NC} Live waveform + spectrum visualization"
echo -e "  ${GREEN}✓${NC} Genre mixing & vibe controls"
echo -e "  ${GREEN}✓${NC} Automatic song generation"
echo -e "  ${GREEN}✓${NC} Stem export (bass, lead, pad, drums)"
echo ""
echo -e "${YELLOW}Quick Start:${NC}"
echo -e "  1. Open ${GREEN}http://localhost:$GUI_PORT${NC} in your browser"
echo -e "  2. Click ${CYAN}'Play Live'${NC} to start real-time synthesis"
echo -e "  3. Adjust ${CYAN}vibe sliders${NC} to control the music"
echo -e "  4. Or click ${CYAN}'Generate Track'${NC} for a full song"
echo ""
echo -e "${YELLOW}Game Integration:${NC}"
echo -e "  ${BLUE}•${NC} Unity:   See ${CYAN}game-integration/unity/StaticWavesMusic.cs${NC}"
echo -e "  ${BLUE}•${NC} Unreal:  See ${CYAN}game-integration/unreal/StaticWavesMusicSubsystem.h${NC}"
echo ""
echo -e "${YELLOW}To stop all services:${NC}"
echo -e "  ${CYAN}./stop-staticwaves.sh${NC}"
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}🎵 Enjoy creating music with AI! 🎵${NC}"
echo ""

# Save service info
cat > logs/services.txt << EOF
API_PID=$API_PID
DDSP_PID=$DDSP_PID
WORKER_PID=$WORKER_PID
GUI_PID=$GUI_PID
GUI_PORT=$GUI_PORT
EOF

# Open browser (optional)
if command -v xdg-open &> /dev/null; then
    sleep 2
    xdg-open "http://localhost:$GUI_PORT" 2>/dev/null &
elif command -v open &> /dev/null; then
    sleep 2
    open "http://localhost:$GUI_PORT" 2>/dev/null &
fi

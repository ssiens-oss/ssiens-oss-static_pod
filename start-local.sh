#!/usr/bin/env bash
set -e

# StaticWaves POD - Local Development Startup Script
# This script starts all services needed to run the GUI locally

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  StaticWaves POD - Local Startup      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create logs directory
mkdir -p logs

# Function to check if a port is in use
check_port() {
    lsof -i:$1 > /dev/null 2>&1
    return $?
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0

    echo -ne "${YELLOW}⏳ Waiting for $name to start...${NC}"

    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "\r${GREEN}✅ $name is ready!${NC}                    "
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
        echo -ne "\r${YELLOW}⏳ Waiting for $name to start... ($attempt/$max_attempts)${NC}"
    done

    echo -e "\r${RED}❌ $name failed to start${NC}                    "
    return 1
}

# Step 1: Check if Redis is running
echo -e "${BLUE}[1/4]${NC} Checking Redis..."
if check_port 6379; then
    echo -e "${GREEN}✅ Redis is already running on port 6379${NC}"
else
    echo -e "${YELLOW}📦 Starting Redis...${NC}"
    redis-server --daemonize yes --logfile "$SCRIPT_DIR/logs/redis.log"
    sleep 2
    if check_port 6379; then
        echo -e "${GREEN}✅ Redis started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start Redis${NC}"
        exit 1
    fi
fi
echo ""

# Step 2: Install Python dependencies for Music API
echo -e "${BLUE}[2/4]${NC} Setting up Music API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installing Music API dependencies...${NC}"
    pip install -q -r music-engine/requirements-api.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi
echo ""

# Step 3: Start Music API
echo -e "${BLUE}[3/4]${NC} Starting Music API..."
if check_port 8000; then
    echo -e "${YELLOW}⚠️  Music API is already running on port 8000${NC}"
else
    export REDIS_HOST=localhost
    export REDIS_PORT=6379
    export OUTPUT_DIR="$SCRIPT_DIR/output"
    mkdir -p "$OUTPUT_DIR"

    cd music-engine/api
    python main.py > "$SCRIPT_DIR/logs/music-api.log" 2>&1 &
    MUSIC_API_PID=$!
    echo $MUSIC_API_PID > "$SCRIPT_DIR/logs/music-api.pid"
    cd "$SCRIPT_DIR"

    if wait_for_service "http://localhost:8000/health" "Music API"; then
        echo -e "${GREEN}✅ Music API started (PID: $MUSIC_API_PID)${NC}"
    else
        echo -e "${RED}❌ Music API failed to start. Check logs/music-api.log${NC}"
        exit 1
    fi
fi
echo ""

# Step 4: Install frontend dependencies and start dev server
echo -e "${BLUE}[4/4]${NC} Starting Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
fi

echo -e "${GREEN}✅ Starting Music Studio GUI...${NC}"
echo ""

# Print summary
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  All Services Started Successfully!   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}🌐 Services:${NC}"
echo -e "  ${GREEN}•${NC} Music API:     http://localhost:8000"
echo -e "  ${GREEN}•${NC} API Docs:      http://localhost:8000/docs"
echo -e "  ${GREEN}•${NC} Music Studio:  http://localhost:5174 ${YELLOW}(starting...)${NC}"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "  ${GREEN}•${NC} Redis:     logs/redis.log"
echo -e "  ${GREEN}•${NC} Music API: logs/music-api.log"
echo ""
echo -e "${BLUE}🛑 To stop services:${NC}"
echo -e "  ${YELLOW}./stop-local.sh${NC}"
echo ""
echo -e "${GREEN}Starting frontend dev server...${NC}"
echo ""

# Start the frontend (this will block)
npm run dev:music

# Cleanup on exit (if user presses Ctrl+C)
trap cleanup EXIT

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    if [ -f "logs/music-api.pid" ]; then
        kill $(cat logs/music-api.pid) 2>/dev/null || true
        rm logs/music-api.pid
    fi
}

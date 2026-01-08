#!/bin/bash
# Stop Pod Engine - Stops all running services

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}Stopping Pod Engine Services...${NC}\n"

# Stop ComfyUI
if pgrep -f "python.*main.py.*8188" > /dev/null; then
    echo -e "${CYAN}▶ Stopping ComfyUI...${NC}"
    pkill -f "python.*main.py.*8188" || true
    echo -e "${GREEN}✓ ComfyUI stopped${NC}"
else
    echo -e "${YELLOW}⚠ ComfyUI not running${NC}"
fi

# Stop Music API
if pgrep -f "uvicorn.*music-engine.api.main" > /dev/null; then
    echo -e "${CYAN}▶ Stopping Music API...${NC}"
    pkill -f "uvicorn.*music-engine.api.main" || true
    echo -e "${GREEN}✓ Music API stopped${NC}"
else
    echo -e "${YELLOW}⚠ Music API not running${NC}"
fi

# Stop Music Worker
if pgrep -f "python.*music-engine/worker/worker.py" > /dev/null; then
    echo -e "${CYAN}▶ Stopping Music Worker...${NC}"
    pkill -f "python.*music-engine/worker/worker.py" || true
    echo -e "${GREEN}✓ Music Worker stopped${NC}"
else
    echo -e "${YELLOW}⚠ Music Worker not running${NC}"
fi

# Stop Redis (optional - comment out if you want to keep Redis running)
if pgrep redis-server > /dev/null; then
    echo -e "${CYAN}▶ Stopping Redis...${NC}"
    redis-cli shutdown || true
    sleep 1
    echo -e "${GREEN}✓ Redis stopped${NC}"
else
    echo -e "${YELLOW}⚠ Redis not running${NC}"
fi

echo -e "\n${GREEN}All services stopped!${NC}\n"

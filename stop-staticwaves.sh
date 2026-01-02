#!/bin/bash

###############################################################################
# StaticWaves - Stop All Services
###############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}Stopping StaticWaves services...${NC}"
echo ""

# Read service info
if [ -f "logs/services.txt" ]; then
    source logs/services.txt
fi

# Stop GUI
if [ ! -z "$GUI_PID" ] && kill -0 $GUI_PID 2>/dev/null; then
    kill $GUI_PID
    echo -e "${GREEN}✓${NC} Stopped Web GUI (PID: $GUI_PID)"
else
    echo -e "${YELLOW}⚠${NC} GUI not running"
fi

# Stop Worker
if [ ! -z "$WORKER_PID" ] && kill -0 $WORKER_PID 2>/dev/null; then
    kill $WORKER_PID
    echo -e "${GREEN}✓${NC} Stopped Music Worker (PID: $WORKER_PID)"
else
    echo -e "${YELLOW}⚠${NC} Worker not running"
fi

# Stop DDSP Server
if [ ! -z "$DDSP_PID" ] && kill -0 $DDSP_PID 2>/dev/null; then
    kill $DDSP_PID
    echo -e "${GREEN}✓${NC} Stopped DDSP Server (PID: $DDSP_PID)"
else
    echo -e "${YELLOW}⚠${NC} DDSP Server not running"
fi

# Stop API
if [ ! -z "$API_PID" ] && kill -0 $API_PID 2>/dev/null; then
    kill $API_PID
    echo -e "${GREEN}✓${NC} Stopped Music API (PID: $API_PID)"
else
    echo -e "${YELLOW}⚠${NC} API not running"
fi

# Stop Redis (if started by us)
if pgrep -f "redis-server.*6379" > /dev/null; then
    pkill -f "redis-server.*6379"
    echo -e "${GREEN}✓${NC} Stopped Redis"
fi

# Stop Redis Docker container if running
if docker ps | grep -q staticwaves-redis 2>/dev/null; then
    docker stop staticwaves-redis > /dev/null 2>&1
    docker rm staticwaves-redis > /dev/null 2>&1
    echo -e "${GREEN}✓${NC} Stopped Redis Docker container"
fi

# Clean up PID files
rm -f logs/*.pid
rm -f logs/services.txt

echo ""
echo -e "${GREEN}✓ All StaticWaves services stopped${NC}"
echo ""

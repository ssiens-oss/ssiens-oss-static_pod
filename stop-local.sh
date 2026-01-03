#!/usr/bin/env bash

# StaticWaves POD - Stop Local Services Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping StaticWaves POD services...${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Stop Music API
if [ -f "logs/music-api.pid" ]; then
    PID=$(cat logs/music-api.pid)
    if kill -0 $PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping Music API (PID: $PID)...${NC}"
        kill $PID
        rm logs/music-api.pid
        echo -e "${GREEN}✅ Music API stopped${NC}"
    else
        echo -e "${YELLOW}Music API is not running${NC}"
        rm logs/music-api.pid
    fi
else
    echo -e "${YELLOW}No Music API PID file found${NC}"
fi

# Stop Redis
echo -e "${YELLOW}Stopping Redis...${NC}"
redis-cli shutdown 2>/dev/null && echo -e "${GREEN}✅ Redis stopped${NC}" || echo -e "${YELLOW}Redis was not running${NC}"

echo ""
echo -e "${GREEN}All services stopped!${NC}"

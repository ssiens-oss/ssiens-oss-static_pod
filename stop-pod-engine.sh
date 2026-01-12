#!/bin/bash
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Stopping POD Engine..."

if [ -f logs/pod-engine.pids ]; then
    source logs/pod-engine.pids

    for pid_var in COMFYUI_PID GATEWAY_PID WEBUI_PID; do
        pid=${!pid_var}
        if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
            kill $pid
            echo -e "${GREEN}✓ Stopped $pid_var ($pid)${NC}"
        fi
    done

    rm logs/pod-engine.pids
else
    echo -e "${RED}✗ No PID file found${NC}"
    echo "Attempting to kill any running services..."
    pkill -f "comfyui" || true
    pkill -f "gateway" || true
    pkill -f "vite" || true
fi

echo "Stopped."

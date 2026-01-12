#!/bin/bash
GREEN='\033[0;32m'
NC='\033[0m'

echo "Stopping demo services..."

if [ -f logs/pod-demo.pids ]; then
    source logs/pod-demo.pids
    for pid_var in GATEWAY_PID WEBUI_PID; do
        pid=${!pid_var}
        if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
            kill $pid
            echo -e "${GREEN}✓ Stopped $pid_var${NC}"
        fi
    done
    rm logs/pod-demo.pids
fi

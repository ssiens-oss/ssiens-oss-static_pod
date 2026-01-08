#!/bin/bash
#
# StaticWaves POD Engine - Stop Script
#

echo "🛑 Stopping StaticWaves POD Engine..."
echo ""

# Try to kill using saved PIDs first
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo "✓ Stopped backend (PID: $BACKEND_PID)"
    fi
    rm logs/backend.pid
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "✓ Stopped frontend (PID: $FRONTEND_PID)"
    fi
    rm logs/frontend.pid
fi

# Fallback: kill by process name
pkill -f "python3.*main.py" 2>/dev/null && echo "✓ Stopped backend processes"
pkill -f "vite" 2>/dev/null && echo "✓ Stopped frontend processes"
pkill -f "node.*vite" 2>/dev/null

sleep 1

echo ""
echo "✨ All services stopped successfully!"
echo ""

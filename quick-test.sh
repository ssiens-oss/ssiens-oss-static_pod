#!/bin/bash

# Quick Test Script for Local Development
# Tests the POD Engine with GUI monitoring

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║         POD Engine - Quick Test                   ║"
echo "╚════════════════════════════════════════════════════╝"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Start POD Engine API in background
log "Starting POD Engine API..."
npm run engine > /tmp/pod-engine-test.log 2>&1 &
ENGINE_PID=$!
echo "ENGINE_PID=$ENGINE_PID" > /tmp/.test_pids

# Wait for API
log "Waiting for API..."
for i in {1..15}; do
    if curl -s http://localhost:3000/health > /dev/null 2>&1; then
        success "API is ready"
        break
    fi
    sleep 1
done

# Start Monitor GUI in background
log "Starting Monitor GUI..."
npm run monitor > /tmp/monitor-test.log 2>&1 &
MONITOR_PID=$!
echo "MONITOR_PID=$MONITOR_PID" >> /tmp/.test_pids

# Wait for Monitor
log "Waiting for Monitor..."
for i in {1..15}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        success "Monitor is ready"
        break
    fi
    sleep 1
done

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║            Services Running!                       ║"
echo "║                                                    ║"
echo "║  📊 Monitor GUI:  http://localhost:5173           ║"
echo "║  🔧 Engine API:   http://localhost:3000           ║"
echo "║                                                    ║"
echo "║  PIDs: Engine=$ENGINE_PID Monitor=$MONITOR_PID"
echo "╚════════════════════════════════════════════════════╝"
echo ""

log "Submitting test job..."
JOB_ID=$(curl -s -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test design", "priority": "high"}' | \
  grep -o '"jobId":"[^"]*"' | cut -d'"' -f4)

success "Job submitted: $JOB_ID"

log "Opening monitor in browser..."
sleep 2

echo ""
echo "Monitor GUI is running at: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services..."

# Cleanup function
cleanup() {
    echo ""
    log "Stopping services..."
    kill $MONITOR_PID 2>/dev/null || true
    kill $ENGINE_PID 2>/dev/null || true
    success "All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep script running
tail -f /tmp/pod-engine-test.log /tmp/monitor-test.log

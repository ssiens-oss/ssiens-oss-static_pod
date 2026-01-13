#!/bin/bash

# Production POD Engine Status Check Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Load environment
if [ -f "production/.env" ]; then
    set -a
    source production/.env 2>/dev/null || true
    set +a
fi

API_PORT=${API_PORT:-3000}
COMFYUI_URL=${COMFYUI_API_URL:-http://127.0.0.1:8188}

echo "=================================="
echo "Production POD Engine Status"
echo "=================================="
echo ""

# Check Node processes
log_info "Checking Node.js processes..."
PIDS=$(ps aux | grep -E 'node.*production/(examples|scripts)' | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    log_warning "No Node.js engine processes running"
else
    log_success "Engine processes found:"
    echo "$PIDS" | while read -r PID; do
        PROC_INFO=$(ps -p "$PID" -o pid,etime,comm,args --no-headers)
        echo "    PID $PROC_INFO"
    done
fi
echo ""

# Check Docker
log_info "Checking Docker services..."
if command -v docker-compose >/dev/null 2>&1; then
    if [ -f "production/docker-compose.yml" ]; then
        cd production
        DOCKER_STATUS=$(docker-compose ps 2>/dev/null)
        if echo "$DOCKER_STATUS" | grep -q "Up"; then
            log_success "Docker services are running:"
            docker-compose ps
        else
            log_warning "Docker services are not running"
        fi
        cd ..
    else
        log_warning "docker-compose.yml not found"
    fi
else
    log_warning "docker-compose not installed"
fi
echo ""

# Check API health
log_info "Checking API server..."
if curl -f -s "http://localhost:$API_PORT/health" > /dev/null 2>&1; then
    log_success "API server is healthy at http://localhost:$API_PORT"

    # Get detailed health info
    HEALTH_DATA=$(curl -s "http://localhost:$API_PORT/health")
    echo "    Health: $HEALTH_DATA"

    echo ""
    log_info "Getting statistics..."
    STATS=$(curl -s "http://localhost:$API_PORT/stats")
    echo "    Stats: $STATS"
else
    log_error "API server is not responding at http://localhost:$API_PORT"
fi
echo ""

# Check ComfyUI
log_info "Checking ComfyUI..."
if curl -f -s "$COMFYUI_URL/system_stats" > /dev/null 2>&1; then
    log_success "ComfyUI is running at $COMFYUI_URL"
else
    log_error "ComfyUI is not responding at $COMFYUI_URL"
fi
echo ""

# Check database (if PostgreSQL)
if [ "$DATABASE_TYPE" = "postgres" ] && command -v psql >/dev/null 2>&1; then
    log_info "Checking PostgreSQL..."
    if psql "$DATABASE_URL" -c "SELECT 1" >/dev/null 2>&1; then
        log_success "PostgreSQL is accessible"
    else
        log_error "PostgreSQL is not accessible"
    fi
    echo ""
fi

# Summary
echo "=================================="
echo "Quick Commands"
echo "=================================="
echo ""
echo "View logs:     tail -f logs/*.log"
echo "Health check:  curl http://localhost:$API_PORT/health"
echo "Statistics:    curl http://localhost:$API_PORT/stats"
echo "Submit job:    curl -X POST http://localhost:$API_PORT/jobs -H 'Content-Type: application/json' -d '{...}'"
echo "Stop engine:   ./production/scripts/stop.sh"
echo ""

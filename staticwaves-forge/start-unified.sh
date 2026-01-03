#!/bin/bash
# StaticWaves Forge - One-Click Boot System for RunPod
# Starts all services in the correct order with health checks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration - Auto-detect base directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORGE_DIR="$SCRIPT_DIR"
LOG_DIR="/tmp/staticwaves-logs"
PID_DIR="/tmp/staticwaves-pids"

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Banner
clear
echo -e "${PURPLE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                                        ║${NC}"
echo -e "${PURPLE}║         ${CYAN}✨ StaticWaves Forge ${PURPLE}${YELLOW}One-Click Boot${PURPLE} ✨         ║${NC}"
echo -e "${PURPLE}║                                                        ║${NC}"
echo -e "${PURPLE}║         ${GREEN}Unified RunPod Instance Startup${PURPLE}            ║${NC}"
echo -e "${PURPLE}║                                                        ║${NC}"
echo -e "${PURPLE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Progress indicator
show_progress() {
    local service=$1
    local status=$2
    if [ "$status" == "start" ]; then
        echo -e "${YELLOW}▶  Starting ${service}...${NC}"
    elif [ "$status" == "done" ]; then
        echo -e "${GREEN}✓  ${service} started successfully${NC}"
    elif [ "$status" == "fail" ]; then
        echo -e "${RED}✗  ${service} failed to start${NC}"
    fi
}

# Health check function
wait_for_service() {
    local name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo -e "${CYAN}   Waiting for $name to be ready...${NC}"

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}   ✓ $name is healthy${NC}"
            return 0
        fi
        echo -ne "${YELLOW}   ⏳ Attempt $attempt/$max_attempts...${NC}\r"
        sleep 2
        ((attempt++))
    done

    echo -e "${RED}   ✗ $name failed health check${NC}"
    return 1
}

# Kill existing processes
cleanup_existing() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"

    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "redis-server" 2>/dev/null || true

    rm -f "$PID_DIR"/*.pid
    echo -e "${GREEN}✓ Cleanup complete${NC}"
    echo ""
}

# Start Redis (optional, for job queue)
start_redis() {
    show_progress "Redis Queue" "start"

    if command -v redis-server > /dev/null 2>&1; then
        redis-server --daemonize yes \
            --port 6379 \
            --logfile "$LOG_DIR/redis.log" \
            --pidfile "$PID_DIR/redis.pid" \
            --save 60 1

        sleep 2
        if redis-cli ping > /dev/null 2>&1; then
            show_progress "Redis Queue" "done"
            echo "$!" > "$PID_DIR/redis.pid"
            return 0
        fi
    else
        echo -e "${YELLOW}   ⚠ Redis not installed - running without queue${NC}"
    fi
    return 0
}

# Start Forge API Backend
start_forge_api() {
    show_progress "Forge API Backend" "start"

    cd "$FORGE_DIR/apps/api"

    # Install dependencies if needed
    if [ ! -f "$PID_DIR/api_deps_installed" ]; then
        echo -e "${CYAN}   Installing Python dependencies...${NC}"
        pip install -q fastapi uvicorn python-multipart aiofiles pydantic python-jose passlib || true
        touch "$PID_DIR/api_deps_installed"
    fi

    # Start API server
    nohup python3 -m uvicorn main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 2 \
        > "$LOG_DIR/forge-api.log" 2>&1 &

    echo $! > "$PID_DIR/forge-api.pid"

    if wait_for_service "Forge API" "http://localhost:8000/"; then
        show_progress "Forge API Backend" "done"
        return 0
    else
        show_progress "Forge API Backend" "fail"
        return 1
    fi
}

# Start Forge Web GUI
start_forge_web() {
    show_progress "Forge Web GUI" "start"

    cd "$FORGE_DIR/apps/web"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${CYAN}   Installing Node dependencies (this may take a minute)...${NC}"
        npm install --silent
    fi

    # Start web server
    nohup npm run dev \
        > "$LOG_DIR/forge-web.log" 2>&1 &

    echo $! > "$PID_DIR/forge-web.pid"

    if wait_for_service "Forge Web" "http://localhost:3000/"; then
        show_progress "Forge Web GUI" "done"
        return 0
    else
        show_progress "Forge Web GUI" "fail"
        return 1
    fi
}

# Start POD Service (if exists)
start_pod_service() {
    if [ -d "$POD_DIR" ]; then
        show_progress "POD Service" "start"

        cd "$POD_DIR"

        # Check if POD has its own startup script
        if [ -f "deploy.sh" ]; then
            nohup bash deploy.sh > "$LOG_DIR/pod-service.log" 2>&1 &
            echo $! > "$PID_DIR/pod-service.pid"
            show_progress "POD Service" "done"
        else
            echo -e "${YELLOW}   ⚠ POD service not configured${NC}"
        fi
    fi
}

# Display service URLs
show_service_urls() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ All services are running!${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${CYAN}📡 Service URLs:${NC}"
    echo ""

    # Get RunPod ID from hostname
    POD_ID=$(hostname)

    echo -e "${PURPLE}Forge Web GUI:${NC}"
    echo -e "   Local:  ${GREEN}http://localhost:3000${NC}"
    echo -e "   Public: ${GREEN}https://$POD_ID-3000.proxy.runpod.net${NC}"
    echo ""

    echo -e "${PURPLE}Forge API:${NC}"
    echo -e "   Local:  ${GREEN}http://localhost:8000${NC}"
    echo -e "   Public: ${GREEN}https://$POD_ID-8000.proxy.runpod.net${NC}"
    echo -e "   Docs:   ${GREEN}https://$POD_ID-8000.proxy.runpod.net/docs${NC}"
    echo ""

    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${PURPLE}Redis Queue:${NC}"
        echo -e "   Local:  ${GREEN}localhost:6379${NC}"
        echo ""
    fi

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${CYAN}📊 Service Status:${NC}"
    echo -e "   PID files: ${YELLOW}$PID_DIR${NC}"
    echo -e "   Log files: ${YELLOW}$LOG_DIR${NC}"
    echo ""
    echo -e "${CYAN}🛠  Management Commands:${NC}"
    echo -e "   View logs:    ${YELLOW}tail -f $LOG_DIR/*.log${NC}"
    echo -e "   Stop all:     ${YELLOW}$0 stop${NC}"
    echo -e "   Restart all:  ${YELLOW}$0 restart${NC}"
    echo -e "   Status check: ${YELLOW}$0 status${NC}"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Stop all services
stop_all_services() {
    echo -e "${YELLOW}🛑 Stopping all services...${NC}"

    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            service=$(basename "$pid_file" .pid)
            kill "$pid" 2>/dev/null || true
            rm "$pid_file"
            echo -e "${GREEN}✓ Stopped $service${NC}"
        fi
    done

    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    redis-cli shutdown 2>/dev/null || true

    echo -e "${GREEN}✅ All services stopped${NC}"
}

# Show status
show_status() {
    echo -e "${CYAN}📊 Service Status:${NC}"
    echo ""

    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            service=$(basename "$pid_file" .pid)
            if ps -p "$pid" > /dev/null 2>&1; then
                echo -e "   ${GREEN}●${NC} $service (PID: $pid) - ${GREEN}Running${NC}"
            else
                echo -e "   ${RED}●${NC} $service (PID: $pid) - ${RED}Dead${NC}"
            fi
        fi
    done
    echo ""
}

# Main execution
main() {
    case "${1:-start}" in
        start)
            cleanup_existing
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${CYAN}🚀 Starting all services...${NC}"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""

            start_redis
            echo ""
            start_forge_api
            echo ""
            start_forge_web
            echo ""
            # start_pod_service  # Uncomment if you want POD service

            show_service_urls

            echo -e "${GREEN}🎉 StaticWaves Forge is ready!${NC}"
            echo ""
            ;;

        stop)
            stop_all_services
            ;;

        restart)
            stop_all_services
            sleep 2
            $0 start
            ;;

        status)
            show_status
            ;;

        logs)
            tail -f "$LOG_DIR"/*.log
            ;;

        *)
            echo "Usage: $0 {start|stop|restart|status|logs}"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

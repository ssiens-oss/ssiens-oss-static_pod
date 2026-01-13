#!/bin/bash

# Production POD Engine Stop Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

MODE=${1:-all}

case $MODE in
    docker)
        log_info "Stopping Docker Compose services..."
        cd production
        docker-compose down
        log_success "Services stopped"
        ;;

    docker-clean)
        log_info "Stopping and removing all Docker resources..."
        cd production
        docker-compose down -v --remove-orphans
        log_success "Services stopped and volumes removed"
        ;;

    all|*)
        log_info "Stopping Production POD Engine processes..."

        # Find and kill Node.js processes running the engine
        PIDS=$(ps aux | grep -E 'node.*production/(examples|scripts)' | grep -v grep | awk '{print $2}')

        if [ -z "$PIDS" ]; then
            log_info "No running engine processes found"
        else
            echo "$PIDS" | while read -r PID; do
                log_info "Stopping process $PID"
                kill -TERM "$PID" 2>/dev/null || true
            done

            # Wait for graceful shutdown
            sleep 2

            # Force kill if still running
            REMAINING=$(ps aux | grep -E 'node.*production/(examples|scripts)' | grep -v grep | awk '{print $2}')
            if [ ! -z "$REMAINING" ]; then
                echo "$REMAINING" | while read -r PID; do
                    log_info "Force stopping process $PID"
                    kill -KILL "$PID" 2>/dev/null || true
                done
            fi

            log_success "All processes stopped"
        fi

        # Stop Docker if running
        if [ -f "production/docker-compose.yml" ]; then
            if docker-compose -f production/docker-compose.yml ps | grep -q "Up"; then
                log_info "Stopping Docker Compose services..."
                cd production
                docker-compose down
            fi
        fi
        ;;
esac

log_success "Shutdown complete"

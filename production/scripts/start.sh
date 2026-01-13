#!/bin/bash

# Production POD Engine Startup Script

set -e

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
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load environment variables
if [ -f "production/.env" ]; then
    export $(cat production/.env | grep -v '^#' | xargs)
    log_success "Loaded environment from production/.env"
else
    log_error "production/.env not found. Run ./production/scripts/deploy.sh first"
    exit 1
fi

# Check required variables
if [ -z "$CLAUDE_API_KEY" ] || [ "$CLAUDE_API_KEY" = "sk-ant-your-api-key-here" ]; then
    log_error "CLAUDE_API_KEY not configured in production/.env"
    exit 1
fi

# Set defaults
export NODE_ENV=${NODE_ENV:-production}
export API_PORT=${API_PORT:-3000}
export WORKER_COUNT=${WORKER_COUNT:-3}

# Mode selection
MODE=${1:-api}

case $MODE in
    api|pool)
        log_info "Starting Production POD Engine in Worker Pool mode"
        log_info "Workers: $WORKER_COUNT"
        log_info "API Port: $API_PORT"
        echo ""

        # Use ts-node if available, otherwise use node
        if command -v ts-node >/dev/null 2>&1; then
            ts-node production/examples/worker-pool-api.ts
        else
            node production/examples/worker-pool-api.ts
        fi
        ;;

    worker|single)
        log_info "Starting Production POD Engine in Single Worker mode"
        echo ""

        if command -v ts-node >/dev/null 2>&1; then
            ts-node production/examples/simple-worker.ts
        else
            node production/examples/simple-worker.ts
        fi
        ;;

    docker)
        log_info "Starting Production POD Engine with Docker Compose"
        cd production
        docker-compose up -d
        log_success "Services started"
        echo ""
        log_info "Check status: docker-compose ps"
        log_info "View logs: docker-compose logs -f pod-engine"
        log_info "API: http://localhost:$API_PORT"
        ;;

    docker-build)
        log_info "Building and starting with Docker Compose"
        cd production
        docker-compose up -d --build
        log_success "Services built and started"
        ;;

    *)
        echo "Usage: $0 [MODE]"
        echo ""
        echo "Modes:"
        echo "  api, pool        - Start worker pool with API (default)"
        echo "  worker, single   - Start single worker"
        echo "  docker           - Start with Docker Compose"
        echo "  docker-build     - Build and start with Docker Compose"
        echo ""
        echo "Examples:"
        echo "  $0                  # Start worker pool with API"
        echo "  $0 api              # Start worker pool with API"
        echo "  $0 worker           # Start single worker"
        echo "  $0 docker           # Start with Docker"
        exit 1
        ;;
esac

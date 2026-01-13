#!/bin/bash
# POD Gateway Control Script
# Easy management interface for POD Gateway service

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVICE_NAME="pod-gateway"

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running as systemd service or Docker
detect_deployment() {
    if systemctl list-units --full -all | grep -Fq "$SERVICE_NAME.service"; then
        echo "systemd"
    elif docker ps -a | grep -q "pod-gateway"; then
        echo "docker"
    else
        echo "none"
    fi
}

# Systemd commands
systemd_start() {
    log_info "Starting POD Gateway service..."
    sudo systemctl start "$SERVICE_NAME"
    log_success "Service started"
}

systemd_stop() {
    log_info "Stopping POD Gateway service..."
    sudo systemctl stop "$SERVICE_NAME"
    log_success "Service stopped"
}

systemd_restart() {
    log_info "Restarting POD Gateway service..."
    sudo systemctl restart "$SERVICE_NAME"
    log_success "Service restarted"
}

systemd_status() {
    sudo systemctl status "$SERVICE_NAME" --no-pager
}

systemd_logs() {
    sudo journalctl -u "$SERVICE_NAME" -f
}

# Docker commands
docker_start() {
    log_info "Starting POD Gateway container..."
    docker-compose up -d
    log_success "Container started"
}

docker_stop() {
    log_info "Stopping POD Gateway container..."
    docker-compose down
    log_success "Container stopped"
}

docker_restart() {
    log_info "Restarting POD Gateway container..."
    docker-compose restart
    log_success "Container restarted"
}

docker_status() {
    docker-compose ps
    echo ""
    docker-compose logs --tail=50
}

docker_logs() {
    docker-compose logs -f
}

# Health check
health_check() {
    log_info "Checking POD Gateway health..."

    if curl -s -f http://localhost:5000/health > /dev/null 2>&1; then
        log_success "Service is healthy"
        curl -s http://localhost:5000/health | python3 -m json.tool
    else
        log_error "Service is not responding"
        exit 1
    fi
}

# Show usage
show_usage() {
    cat << EOF
POD Gateway Control Script

Usage: $(basename "$0") {start|stop|restart|status|logs|health}

Commands:
    start     - Start the POD Gateway service
    stop      - Stop the POD Gateway service
    restart   - Restart the POD Gateway service
    status    - Show service status
    logs      - Show and follow logs
    health    - Check service health

Examples:
    $(basename "$0") start
    $(basename "$0") logs
    $(basename "$0") health
EOF
}

# Main
main() {
    if [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi

    DEPLOYMENT=$(detect_deployment)

    if [ "$DEPLOYMENT" == "none" ]; then
        log_error "POD Gateway is not installed as a service or container"
        echo ""
        echo "Install options:"
        echo "  Systemd service: sudo ./install_standalone.sh"
        echo "  Docker:          docker-compose up -d"
        exit 1
    fi

    COMMAND=$1

    case "$COMMAND" in
        start)
            if [ "$DEPLOYMENT" == "systemd" ]; then
                systemd_start
            else
                docker_start
            fi
            ;;
        stop)
            if [ "$DEPLOYMENT" == "systemd" ]; then
                systemd_stop
            else
                docker_stop
            fi
            ;;
        restart)
            if [ "$DEPLOYMENT" == "systemd" ]; then
                systemd_restart
            else
                docker_restart
            fi
            ;;
        status)
            if [ "$DEPLOYMENT" == "systemd" ]; then
                systemd_status
            else
                docker_status
            fi
            ;;
        logs)
            if [ "$DEPLOYMENT" == "systemd" ]; then
                systemd_logs
            else
                docker_logs
            fi
            ;;
        health)
            health_check
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

main "$@"

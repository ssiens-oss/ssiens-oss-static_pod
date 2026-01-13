#!/bin/bash
# POD Gateway Standalone Installation Script
# Installs POD Gateway as a standalone service

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/pod-gateway"
SERVICE_NAME="pod-gateway"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

install_dependencies() {
    log_info "Installing system dependencies..."

    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y python3 python3-pip python3-venv curl
    elif command -v yum &> /dev/null; then
        yum install -y python3 python3-pip curl
    else
        log_error "Unsupported package manager"
        exit 1
    fi

    log_success "System dependencies installed"
}

create_install_directory() {
    log_info "Creating installation directory..."

    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/data/images"
    mkdir -p "$INSTALL_DIR/data/state"
    mkdir -p "$INSTALL_DIR/data/archive"
    mkdir -p /var/log/pod-gateway

    log_success "Installation directory created: $INSTALL_DIR"
}

copy_files() {
    log_info "Copying application files..."

    # Copy application
    cp -r app "$INSTALL_DIR/"
    cp -r templates "$INSTALL_DIR/"
    cp requirements.txt "$INSTALL_DIR/"
    cp daemon.py "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/daemon.py"

    # Copy .env if it doesn't exist
    if [ -f .env ]; then
        cp .env "$INSTALL_DIR/.env"
    elif [ -f .env.example ]; then
        cp .env.example "$INSTALL_DIR/.env"
        log_warning "Copied .env.example to .env - Please configure!"
    fi

    log_success "Files copied"
}

setup_virtualenv() {
    log_info "Setting up Python virtual environment..."

    cd "$INSTALL_DIR"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate

    log_success "Virtual environment created"
}

create_systemd_service() {
    log_info "Creating systemd service..."

    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=POD Gateway - Human-in-the-loop approval system
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/app/main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/pod-gateway/output.log
StandardError=append:/var/log/pod-gateway/error.log
SyslogIdentifier=pod-gateway

# Security hardening
NoNewPrivileges=true
PrivateTmp=true

# Resource limits
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

    chmod 644 "$SERVICE_FILE"
    log_success "Systemd service created"
}

enable_and_start_service() {
    log_info "Enabling and starting service..."

    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    systemctl start "$SERVICE_NAME"

    # Wait a moment for service to start
    sleep 2

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Service started successfully"
    else
        log_error "Service failed to start. Check logs with: journalctl -u $SERVICE_NAME -f"
        exit 1
    fi
}

show_status() {
    echo ""
    echo "=============================================="
    echo "POD Gateway Installation Complete!"
    echo "=============================================="
    echo ""
    echo "Service Status:"
    systemctl status "$SERVICE_NAME" --no-pager || true
    echo ""
    echo "Useful Commands:"
    echo "  Start:   systemctl start $SERVICE_NAME"
    echo "  Stop:    systemctl stop $SERVICE_NAME"
    echo "  Restart: systemctl restart $SERVICE_NAME"
    echo "  Status:  systemctl status $SERVICE_NAME"
    echo "  Logs:    journalctl -u $SERVICE_NAME -f"
    echo ""
    echo "Configuration:"
    echo "  Location: $INSTALL_DIR"
    echo "  Config:   $INSTALL_DIR/.env"
    echo "  Images:   $INSTALL_DIR/data/images"
    echo "  State:    $INSTALL_DIR/data/state"
    echo "  Logs:     /var/log/pod-gateway/"
    echo ""
    echo "Web Interface: http://localhost:5000"
    echo ""

    # Check if .env needs configuration
    if grep -q "your-printify-api-key" "$INSTALL_DIR/.env" 2>/dev/null; then
        log_warning "Don't forget to configure $INSTALL_DIR/.env with your Printify credentials!"
    fi
}

uninstall() {
    log_info "Uninstalling POD Gateway..."

    # Stop and disable service
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        systemctl stop "$SERVICE_NAME"
    fi

    if systemctl is-enabled --quiet "$SERVICE_NAME"; then
        systemctl disable "$SERVICE_NAME"
    fi

    # Remove service file
    rm -f "$SERVICE_FILE"
    systemctl daemon-reload

    # Ask before removing data
    read -p "Remove installation directory ($INSTALL_DIR)? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        log_success "Installation directory removed"
    fi

    log_success "POD Gateway uninstalled"
}

# Main
main() {
    echo ""
    echo "╔══════════════════════════════════════════╗"
    echo "║  POD Gateway Standalone Installation    ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""

    if [ "$1" == "uninstall" ]; then
        check_root
        uninstall
        exit 0
    fi

    check_root
    install_dependencies
    create_install_directory
    copy_files
    setup_virtualenv
    create_systemd_service
    enable_and_start_service
    show_status
}

# Run
main "$@"

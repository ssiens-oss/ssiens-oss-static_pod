#!/bin/bash
###############################################################################
# StaticWaves POD Gateway - Fresh Linux Installation Script
#
# This script performs a complete fresh installation on a new Linux system:
# - Installs system dependencies
# - Clones the repository
# - Sets up Python virtual environment
# - Installs Python dependencies
# - Configures the POD Gateway
# - Starts the service
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/ssiens-oss/ssiens-oss-static_pod/main/fresh-linux-install.sh | bash
#
# Or clone first then run:
#   git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
#   cd ssiens-oss-static_pod
#   ./fresh-linux-install.sh
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/ssiens-oss/ssiens-oss-static_pod.git"
INSTALL_DIR="$HOME/staticwaves-pod"
BRANCH="main"

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

print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════╗"
    echo "║   StaticWaves POD Gateway - Fresh Installation    ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
}

check_system() {
    log_info "Checking system requirements..."

    # Detect OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
        log_info "Detected: $PRETTY_NAME"
    else
        log_error "Cannot detect OS. Unsupported system."
        exit 1
    fi

    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        log_warning "Running as root. Will install system-wide."
        SUDO=""
    else
        SUDO="sudo"
    fi

    log_success "System check complete"
}

install_dependencies() {
    log_info "Installing system dependencies..."

    case "$OS" in
        ubuntu|debian)
            $SUDO apt-get update -qq
            $SUDO apt-get install -y -qq \
                python3 \
                python3-pip \
                python3-venv \
                git \
                curl \
                wget \
                ca-certificates
            ;;
        centos|rhel|fedora)
            $SUDO yum install -y -q \
                python3 \
                python3-pip \
                python3-virtualenv \
                git \
                curl \
                wget \
                ca-certificates
            ;;
        arch|manjaro)
            $SUDO pacman -Sy --noconfirm \
                python \
                python-pip \
                python-virtualenv \
                git \
                curl \
                wget \
                ca-certificates
            ;;
        *)
            log_warning "Unsupported OS. Please install manually: python3, pip3, git, curl"
            ;;
    esac

    # Verify Python 3
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    log_success "Python $PYTHON_VERSION installed"
}

clone_repository() {
    log_info "Cloning repository..."

    if [ -d "$INSTALL_DIR" ]; then
        log_warning "Directory $INSTALL_DIR already exists"
        read -p "Remove and re-clone? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
        else
            log_info "Using existing directory"
            cd "$INSTALL_DIR"
            git pull origin $BRANCH
            return
        fi
    fi

    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"

    log_success "Repository cloned to $INSTALL_DIR"
}

setup_gateway() {
    log_info "Setting up POD Gateway..."

    cd "$INSTALL_DIR/gateway"

    # Create virtual environment
    if [ ! -d ".venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv .venv
        log_success "Virtual environment created"
    fi

    # Install Python dependencies
    log_info "Installing Python dependencies..."
    .venv/bin/pip install -q --upgrade pip
    .venv/bin/pip install -q \
        flask==3.0.2 \
        requests==2.31.0 \
        Pillow==10.2.0 \
        python-dotenv==1.0.1

    log_success "Python dependencies installed"

    # Create data directories
    mkdir -p data/images data/state data/archive
    log_success "Data directories created"

    # Configure environment
    if [ ! -f ".env" ]; then
        log_info "Creating configuration file..."
        cp .env.example .env

        # Update paths
        GATEWAY_DIR="$INSTALL_DIR/gateway"
        sed -i "s|POD_IMAGE_DIR=.*|POD_IMAGE_DIR=$GATEWAY_DIR/data/images|g" .env
        sed -i "s|POD_STATE_FILE=.*|POD_STATE_FILE=$GATEWAY_DIR/data/state.json|g" .env
        sed -i "s|POD_ARCHIVE_DIR=.*|POD_ARCHIVE_DIR=$GATEWAY_DIR/data/archive|g" .env

        # Set placeholder values
        sed -i "s|PRINTIFY_API_KEY=.*|PRINTIFY_API_KEY=your_api_key_here|g" .env
        sed -i "s|PRINTIFY_SHOP_ID=.*|PRINTIFY_SHOP_ID=12345|g" .env

        log_success "Configuration file created"
        log_warning "You MUST update API keys in: $GATEWAY_DIR/.env"
    else
        log_info ".env already exists, skipping"
    fi
}

test_installation() {
    log_info "Testing installation..."

    cd "$INSTALL_DIR/gateway"

    # Test imports
    if .venv/bin/python -c "import sys; sys.path.insert(0, '$INSTALL_DIR/gateway'); from app.main import app; print('OK')" &> /dev/null; then
        log_success "Installation test passed"
        return 0
    else
        log_error "Installation test failed"
        return 1
    fi
}

create_start_script() {
    log_info "Creating start script..."

    cat > "$INSTALL_DIR/start-gateway.sh" << 'EOF'
#!/bin/bash
# Quick start script for POD Gateway

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/gateway"

echo "🚀 Starting POD Gateway..."
echo "📁 Working directory: $(pwd)"
echo ""

# Check if .env is configured
if grep -q "your_api_key_here" .env 2>/dev/null; then
    echo "⚠️  WARNING: Please configure your Printify API keys in:"
    echo "   $SCRIPT_DIR/gateway/.env"
    echo ""
    echo "Press Enter to continue anyway, or Ctrl+C to exit..."
    read
fi

# Start the server
export PYTHONPATH="$SCRIPT_DIR/gateway"
.venv/bin/python app/main.py
EOF

    chmod +x "$INSTALL_DIR/start-gateway.sh"
    log_success "Start script created: $INSTALL_DIR/start-gateway.sh"
}

print_next_steps() {
    echo ""
    echo "╔════════════════════════════════════════════════════╗"
    echo "║            Installation Complete! 🎉               ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
    echo "Installation directory: $INSTALL_DIR"
    echo ""
    echo "📋 Next Steps:"
    echo ""
    echo "1. Configure your Printify API keys:"
    echo "   nano $INSTALL_DIR/gateway/.env"
    echo ""
    echo "   Update these lines:"
    echo "   PRINTIFY_API_KEY=your_actual_api_key"
    echo "   PRINTIFY_SHOP_ID=your_actual_shop_id"
    echo ""
    echo "2. Start the POD Gateway:"
    echo "   $INSTALL_DIR/start-gateway.sh"
    echo ""
    echo "   Or manually:"
    echo "   cd $INSTALL_DIR/gateway"
    echo "   .venv/bin/python app/main.py"
    echo ""
    echo "3. Open your browser:"
    echo "   http://localhost:5000"
    echo ""
    echo "📚 Documentation:"
    echo "   - Quick Start: $INSTALL_DIR/LINUX_QUICKSTART.md"
    echo "   - Gateway README: $INSTALL_DIR/gateway/README.md"
    echo "   - Setup Guide: $INSTALL_DIR/SETUP_GUIDE.md"
    echo ""
    echo "🔑 Get Printify API Keys:"
    echo "   1. Go to: https://printify.com"
    echo "   2. Navigate to: Settings → API"
    echo "   3. Generate an API token"
    echo "   4. Copy your API Key and Shop ID"
    echo ""
    echo "✅ You're all set! Happy designing! 🚀"
    echo ""
}

# Main installation flow
main() {
    print_header

    check_system
    install_dependencies
    clone_repository
    setup_gateway

    if test_installation; then
        create_start_script
        print_next_steps
    else
        log_error "Installation failed. Please check the errors above."
        exit 1
    fi
}

# Run main installation
main

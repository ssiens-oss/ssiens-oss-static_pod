#!/bin/bash
# Local Free Deployment Setup Script
# Sets up the POD pipeline for local development (no cloud costs)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${MAGENTA}▶ $1${NC}"
}

print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║         🆓 FREE Local POD Pipeline Setup 🆓                ║"
    echo "║         No Cloud Costs • Run Locally • Full Control       ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

check_prerequisites() {
    log_step "Checking prerequisites..."

    local has_error=0

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        echo "Install from: https://docs.docker.com/get-docker/"
        has_error=1
    else
        log_success "Docker installed"
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        echo "Install from: https://docs.docker.com/compose/install/"
        has_error=1
    else
        log_success "Docker Compose installed"
    fi

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        echo "Please start Docker Desktop or Docker daemon"
        has_error=1
    else
        log_success "Docker daemon running"
    fi

    # Check for GPU (optional)
    if command -v nvidia-smi &> /dev/null; then
        log_success "NVIDIA GPU detected (ComfyUI will use GPU acceleration)"
    else
        log_warning "No NVIDIA GPU detected (ComfyUI will run on CPU - slower)"
        log_info "For GPU support, install: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    fi

    if [ $has_error -eq 1 ]; then
        echo ""
        log_error "Prerequisites check failed. Please install missing components."
        exit 1
    fi

    echo ""
}

setup_environment() {
    log_step "Setting up environment configuration..."

    if [ ! -f .env ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env

        # Set local defaults
        sed -i 's|COMFYUI_API_URL=.*|COMFYUI_API_URL=http://localhost:8188|g' .env
        sed -i 's|STORAGE_TYPE=.*|STORAGE_TYPE=local|g' .env
        sed -i 's|STORAGE_PATH=.*|STORAGE_PATH=./data/designs|g' .env
        sed -i 's|VITE_MUSIC_API_URL=.*|VITE_MUSIC_API_URL=http://localhost:8000|g' .env

        log_success ".env file created"
        echo ""
        log_warning "IMPORTANT: Edit .env and add your API keys:"
        echo "  - ANTHROPIC_API_KEY (required for AI prompts)"
        echo "  - PRINTIFY_API_KEY (required for product creation)"
        echo ""
        read -p "Press Enter to open .env in editor, or Ctrl+C to edit later..."
        ${EDITOR:-nano} .env
    else
        log_success ".env file already exists"
    fi

    echo ""
}

create_directories() {
    log_step "Creating data directories..."

    mkdir -p data/designs
    mkdir -p data/chrome-profile
    mkdir -p comfyui-data/models/checkpoints
    mkdir -p comfyui-data/output
    mkdir -p comfyui-data/input
    mkdir -p comfyui-data/custom_nodes

    log_success "Directories created"
    echo ""
}

download_models() {
    log_step "Checking AI models..."

    if [ ! -f comfyui-data/models/checkpoints/sd_xl_base_1.0.safetensors ]; then
        log_info "SDXL model not found"
        echo ""
        echo "You need to download the SDXL model for image generation."
        echo "Options:"
        echo "  1. Download manually from: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0"
        echo "  2. Skip for now (download later when needed)"
        echo "  3. Auto-download (requires ~7GB, may take 10-30 minutes)"
        echo ""
        read -p "Choose option (1/2/3): " choice

        case $choice in
            1)
                log_info "Please download manually and place in: comfyui-data/models/checkpoints/"
                ;;
            2)
                log_info "Skipping model download. You'll need to download it later."
                ;;
            3)
                log_info "Downloading SDXL model... (this will take a while)"
                wget -O comfyui-data/models/checkpoints/sd_xl_base_1.0.safetensors \
                    https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
                log_success "Model downloaded"
                ;;
            *)
                log_warning "Invalid choice. Skipping model download."
                ;;
        esac
    else
        log_success "SDXL model found"
    fi

    echo ""
}

setup_docker_compose() {
    log_step "Setting up Docker Compose services..."

    # Check if GPU is available
    if ! command -v nvidia-smi &> /dev/null; then
        log_info "Configuring for CPU mode (no GPU)"
        # Remove GPU requirements from docker-compose.yml
        if command -v yq &> /dev/null; then
            yq eval 'del(.services.comfyui.deploy)' -i docker-compose.yml
        else
            log_warning "Cannot auto-configure CPU mode. Edit docker-compose.yml to remove GPU requirements."
        fi
    fi

    log_success "Docker Compose configured"
    echo ""
}

start_services() {
    log_step "Starting services..."

    echo ""
    log_info "This will start:"
    echo "  • Frontend Web UI (http://localhost:5173)"
    echo "  • ComfyUI API (http://localhost:8188)"
    echo "  • Redis (for music generation)"
    echo ""

    read -p "Start services now? (y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Starting Docker containers..."
        docker-compose up -d

        log_success "Services started!"
        echo ""

        log_info "Waiting for services to be ready..."
        sleep 5

        # Check if services are running
        if docker-compose ps | grep -q "Up"; then
            log_success "All services are running"
            echo ""
            print_access_info
        else
            log_error "Some services failed to start"
            echo ""
            echo "Check logs with: docker-compose logs"
            exit 1
        fi
    else
        log_info "Skipping service start. You can start later with:"
        echo "  docker-compose up -d"
    fi
}

print_access_info() {
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                   🎉 Setup Complete! 🎉                     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 Access your services:"
    echo ""
    echo "  🌐 Web UI:       http://localhost:5173"
    echo "  🎨 ComfyUI:      http://localhost:8188"
    echo "  🔴 Redis:        localhost:6379"
    echo ""
    echo "📝 Useful commands:"
    echo ""
    echo "  View logs:       docker-compose logs -f"
    echo "  Stop services:   docker-compose down"
    echo "  Restart:         docker-compose restart"
    echo "  Check status:    docker-compose ps"
    echo ""
    echo "🔧 Configuration:"
    echo ""
    echo "  Edit settings:   nano .env"
    echo "  Validate env:    ./scripts/validate-env.sh"
    echo ""
    echo "📚 Documentation:"
    echo ""
    echo "  FREE_DEPLOYMENT.md - Complete free deployment guide"
    echo "  README.md - Project overview"
    echo ""
    echo "💡 Next steps:"
    echo ""
    echo "  1. Open http://localhost:5173 in your browser"
    echo "  2. Configure your API keys in .env"
    echo "  3. Run a test design generation"
    echo ""
    echo "🆓 Running 100% locally - No cloud costs!"
    echo ""
}

print_troubleshooting() {
    echo "❓ Troubleshooting:"
    echo ""
    echo "  Port already in use:"
    echo "    docker-compose down"
    echo "    # Change ports in docker-compose.yml"
    echo ""
    echo "  Services not starting:"
    echo "    docker-compose logs"
    echo ""
    echo "  ComfyUI slow/not working:"
    echo "    # Install NVIDIA GPU support for faster generation"
    echo "    # Or use CPU mode (slower but works)"
    echo ""
}

# Main execution
main() {
    print_header

    check_prerequisites
    setup_environment
    create_directories
    download_models
    setup_docker_compose
    start_services

    echo ""
    print_troubleshooting
}

# Run
main

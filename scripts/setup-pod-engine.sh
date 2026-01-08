#!/bin/bash
# Setup Pod Engine - Complete installation for local development
# Installs ComfyUI, models, Python dependencies, and configures everything

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "\n${PURPLE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Banner
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗  ██████╗ ██████╗     ███████╗███╗   ██╗ ██████╗   ║
║   ██╔══██╗██╔═══██╗██╔══██╗    ██╔════╝████╗  ██║██╔════╝   ║
║   ██████╔╝██║   ██║██║  ██║    █████╗  ██╔██╗ ██║██║  ███╗  ║
║   ██╔═══╝ ██║   ██║██║  ██║    ██╔══╝  ██║╚██╗██║██║   ██║  ║
║   ██║     ╚██████╔╝██████╔╝    ███████╗██║ ╚████║╚██████╔╝  ║
║   ╚═╝      ╚═════╝ ╚═════╝     ╚══════╝╚═╝  ╚═══╝ ╚═════╝   ║
║                                                               ║
║           Complete Pod Engine Setup & Installation           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "${CYAN}"
echo "This will install:"
echo "  • ComfyUI with SDXL models"
echo "  • Music Generation Engine (MusicGen + DDSP)"
echo "  • Redis Queue System"
echo "  • All Python dependencies"
echo "  • Web UI dependencies"
echo ""
echo "Requirements:"
echo "  • Python 3.10+"
echo "  • CUDA 12.1+ (for GPU acceleration)"
echo "  • Redis"
echo "  • Node.js 20+"
echo -e "${NC}"

read -p "Press Enter to continue or Ctrl+C to cancel..."

# Configuration
COMFYUI_DIR="${COMFYUI_DIR:-./ComfyUI}"
MODELS_DIR="${COMFYUI_DIR}/models"
DATA_DIR="./data"

# Step 1: Check prerequisites
print_header "Step 1/8: Checking Prerequisites"

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

check_command python3 || exit 1
check_command pip3 || exit 1
check_command git || exit 1
check_command redis-server || print_warning "Redis not found, will need to install"
check_command node || print_warning "Node.js not found"
check_command npm || print_warning "npm not found"

# Check Python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_step "Python version: $PYTHON_VERSION"

# Step 2: Create directory structure
print_header "Step 2/8: Creating Directory Structure"

mkdir -p "$DATA_DIR/output"
mkdir -p "$DATA_DIR/designs"
mkdir -p "$DATA_DIR/models"
mkdir -p "logs"

print_success "Directories created"

# Step 3: Install Node.js dependencies
print_header "Step 3/8: Installing Node.js Dependencies"

if [ -f package.json ]; then
    print_step "Installing npm packages..."
    npm install
    print_success "Node.js dependencies installed"
else
    print_warning "package.json not found, skipping npm install"
fi

# Step 4: Clone and setup ComfyUI
print_header "Step 4/8: Setting up ComfyUI"

if [ ! -d "$COMFYUI_DIR" ]; then
    print_step "Cloning ComfyUI repository..."
    git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFYUI_DIR"
    print_success "ComfyUI cloned"
else
    print_warning "ComfyUI directory already exists"
fi

# Step 5: Create and activate virtual environment
print_header "Step 5/8: Setting up Python Virtual Environment"

if [ ! -d ".venv" ]; then
    print_step "Creating virtual environment..."
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

print_step "Activating virtual environment..."
source .venv/bin/activate
print_success "Virtual environment activated"

# Step 6: Install PyTorch with CUDA support
print_header "Step 6/8: Installing PyTorch with CUDA"

print_step "Installing PyTorch 2.x with CUDA 12.1 support..."
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

print_success "PyTorch installed"

# Step 7: Install ComfyUI dependencies
print_header "Step 7/8: Installing ComfyUI Dependencies"

if [ -f "$COMFYUI_DIR/requirements.txt" ]; then
    print_step "Installing ComfyUI requirements..."
    pip install -r "$COMFYUI_DIR/requirements.txt"
    print_success "ComfyUI dependencies installed"
fi

# Step 8: Install Pod Engine dependencies
print_header "Step 8/8: Installing Pod Engine Dependencies"

print_step "Installing complete pod engine requirements..."
pip install -r pod-requirements.txt

print_success "Pod Engine dependencies installed"

# Step 9: Download models
print_header "Step 9/9: Downloading AI Models"

# Create models directory structure
mkdir -p "${MODELS_DIR}/checkpoints"
mkdir -p "${MODELS_DIR}/vae"
mkdir -p "${MODELS_DIR}/loras"
mkdir -p "${MODELS_DIR}/embeddings"

# Download SDXL model
SDXL_MODEL="${MODELS_DIR}/checkpoints/sd_xl_base_1.0.safetensors"
if [ ! -f "$SDXL_MODEL" ]; then
    print_step "Downloading SDXL model (6.94 GB - this will take a while)..."
    wget -O "$SDXL_MODEL" \
        "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
        --progress=bar:force:noscroll

    print_success "SDXL model downloaded"
else
    print_success "SDXL model already exists"
fi

# Download SDXL VAE (optional but recommended)
SDXL_VAE="${MODELS_DIR}/vae/sdxl_vae.safetensors"
if [ ! -f "$SDXL_VAE" ]; then
    print_step "Downloading SDXL VAE..."
    wget -O "$SDXL_VAE" \
        "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors" \
        --progress=bar:force:noscroll

    print_success "SDXL VAE downloaded"
else
    print_success "SDXL VAE already exists"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_step "Creating .env file from example..."
    cp .env.example .env
    print_success ".env file created"
    print_warning "Please edit .env and add your API keys"
else
    print_success ".env file already exists"
fi

# Installation complete
print_header "Installation Complete! 🎉"

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║                  Setup Complete! 🚀                           ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo ""
echo "1. Edit your .env file with API keys:"
echo "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. Start all services:"
echo "   ${YELLOW}./scripts/start-pod-engine.sh${NC}"
echo ""
echo "3. Start the web UI:"
echo "   ${YELLOW}npm run dev${NC}          # POD Pipeline UI"
echo "   ${YELLOW}npm run dev:music${NC}    # Music Studio UI"
echo ""
echo "4. Access the services:"
echo "   - ComfyUI:     http://localhost:8188"
echo "   - Music API:   http://localhost:8000"
echo "   - Web UI:      http://localhost:5173"
echo ""
echo "5. Stop all services when done:"
echo "   ${YELLOW}./scripts/stop-pod-engine.sh${NC}"
echo ""

print_success "Ready to create! 🎨🎵"

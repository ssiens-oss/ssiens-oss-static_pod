#!/bin/bash

#############################################
# StaticWaves Music Studio - Full Installer
# One-command setup for the complete system
#############################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print functions
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

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Banner
clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███████╗████████╗ █████╗ ████████╗██╗ ██████╗             ║
║   ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██║██╔════╝             ║
║   ███████╗   ██║   ███████║   ██║   ██║██║                  ║
║   ╚════██║   ██║   ██╔══██║   ██║   ██║██║                  ║
║   ███████║   ██║   ██║  ██║   ██║   ██║╚██████╗             ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝             ║
║                                                               ║
║           WAVES - AI Music Generation Studio                 ║
║                    Full Installer v2.0                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "${CYAN}"
echo "This installer will set up:"
echo "  • Music API (FastAPI)"
echo "  • GPU Worker (MusicGen + DDSP)"
echo "  • Redis Queue"
echo "  • Beautiful Web GUI"
echo "  • All dependencies"
echo -e "${NC}"

read -p "Press Enter to continue or Ctrl+C to cancel..."

# Detect OS
print_header "Detecting System"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    print_success "Detected: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    print_success "Detected: macOS"
else
    OS="unknown"
    print_error "Unsupported OS: $OSTYPE"
    exit 1
fi

# Check for required commands
print_header "Checking Prerequisites"

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_warning "$1 is not installed"
        return 1
    fi
}

MISSING_DEPS=()

if ! check_command node; then
    MISSING_DEPS+=("node")
fi

if ! check_command npm; then
    MISSING_DEPS+=("npm")
fi

if ! check_command python3; then
    MISSING_DEPS+=("python3")
fi

if ! check_command pip3; then
    MISSING_DEPS+=("pip3")
fi

if ! check_command docker; then
    MISSING_DEPS+=("docker")
fi

if ! check_command docker-compose; then
    MISSING_DEPS+=("docker-compose")
fi

if ! check_command git; then
    MISSING_DEPS+=("git")
fi

# Install missing dependencies
if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    print_header "Installing Missing Dependencies"

    for dep in "${MISSING_DEPS[@]}"; do
        print_step "Installing $dep..."

        if [[ "$OS" == "linux" ]]; then
            case $dep in
                node|npm)
                    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                    sudo apt-get install -y nodejs
                    ;;
                python3)
                    sudo apt-get update
                    sudo apt-get install -y python3 python3-pip
                    ;;
                pip3)
                    sudo apt-get install -y python3-pip
                    ;;
                docker)
                    curl -fsSL https://get.docker.com -o get-docker.sh
                    sudo sh get-docker.sh
                    sudo usermod -aG docker $USER
                    ;;
                docker-compose)
                    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                    sudo chmod +x /usr/local/bin/docker-compose
                    ;;
                git)
                    sudo apt-get install -y git
                    ;;
            esac
        elif [[ "$OS" == "mac" ]]; then
            if ! command -v brew &> /dev/null; then
                print_error "Homebrew not found. Please install Homebrew first:"
                echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi

            case $dep in
                node|npm)
                    brew install node
                    ;;
                python3|pip3)
                    brew install python3
                    ;;
                docker|docker-compose)
                    print_warning "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
                    read -p "Press Enter after installing Docker Desktop..."
                    ;;
                git)
                    brew install git
                    ;;
            esac
        fi
    done

    print_success "Dependencies installed!"
else
    print_success "All prerequisites are installed!"
fi

# Get directory
INSTALL_DIR=$(pwd)
print_info "Installation directory: $INSTALL_DIR"

# Install Node dependencies
print_header "Installing Node.js Dependencies"

print_step "Installing npm packages..."
npm install

print_success "Node.js dependencies installed!"

# Install Python dependencies
print_header "Installing Python Dependencies"

print_step "Installing API dependencies..."
pip3 install -r music-engine/requirements-api.txt

print_step "Installing Worker dependencies (this may take a while)..."
pip3 install -r music-engine/requirements-worker.txt

print_success "Python dependencies installed!"

# Create .env file
print_header "Configuring Environment"

if [ ! -f .env ]; then
    print_step "Creating .env file..."
    cp .env.example .env
    print_success ".env file created"

    print_warning "Please edit .env and add your API keys:"
    echo "  - ANTHROPIC_API_KEY (for AI lyrics, optional)"
    echo "  - STRIPE_API_KEY (for billing, optional)"

    read -p "Press Enter to continue..."
else
    print_info ".env file already exists"
fi

# Setup music engine
print_header "Setting Up Music Engine"

cd music-engine

print_step "Creating output directories..."
mkdir -p /tmp/staticwaves/output
print_success "Output directories created"

cd ..

# Docker setup
print_header "Docker Setup"

print_step "Checking Docker daemon..."
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running!"
    print_info "Please start Docker Desktop or run: sudo systemctl start docker"
    exit 1
fi
print_success "Docker is running"

print_step "Building Docker images (this may take 10-15 minutes)..."
cd music-engine
docker-compose build

print_success "Docker images built successfully!"

# Start services
print_header "Starting Services"

print_step "Starting Redis, Music API, and Worker..."
docker-compose up -d

print_success "Services started!"

# Wait for services to be ready
print_step "Waiting for services to initialize..."
sleep 5

# Health check
print_header "Health Check"

check_service() {
    local name=$1
    local url=$2
    local max_attempts=10
    local attempt=1

    print_step "Checking $name..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" &> /dev/null; then
            print_success "$name is healthy"
            return 0
        fi

        echo -n "."
        sleep 2
        ((attempt++))
    done

    print_error "$name failed to start"
    return 1
}

check_service "Music API" "http://localhost:8000/health"

cd ..

# Create startup scripts
print_header "Creating Startup Scripts"

# Start script
cat > start-music-studio.sh << 'STARTSCRIPT'
#!/bin/bash

echo "🎵 Starting StaticWaves Music Studio..."

# Start backend services
echo "Starting Music API..."
cd music-engine
docker-compose up -d
cd ..

# Wait for API
sleep 3

# Start frontend
echo "Starting GUI..."
npm run dev:music &

sleep 3

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🎉 StaticWaves Music Studio is running!                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "  🌐 Music Studio GUI:  http://localhost:5174"
echo "  🔧 Music API:         http://localhost:8000"
echo "  📚 API Docs:          http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

wait
STARTSCRIPT

chmod +x start-music-studio.sh
print_success "Created start-music-studio.sh"

# Stop script
cat > stop-music-studio.sh << 'STOPSCRIPT'
#!/bin/bash

echo "🛑 Stopping StaticWaves Music Studio..."

# Stop frontend
pkill -f "vite.*music"

# Stop backend
cd music-engine
docker-compose down
cd ..

echo "✓ Music Studio stopped"
STOPSCRIPT

chmod +x stop-music-studio.sh
print_success "Created stop-music-studio.sh"

# Test script
cat > test-music-generation.sh << 'TESTSCRIPT'
#!/bin/bash

echo "🧪 Testing Music Generation..."

API_URL="http://localhost:8000"

echo ""
echo "1. Health Check..."
curl -s "$API_URL/health" | python3 -m json.tool

echo ""
echo "2. Listing Genres..."
curl -s "$API_URL/genres" | python3 -m json.tool | head -20

echo ""
echo "3. Generating Random Song..."
RESPONSE=$(curl -s -X POST "$API_URL/generate/auto?duration=10")
echo $RESPONSE | python3 -m json.tool

JOB_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")

echo ""
echo "4. Checking Status..."
sleep 2
curl -s "$API_URL/status/$JOB_ID" | python3 -m json.tool

echo ""
echo "✓ Test complete! Job ID: $JOB_ID"
echo "  Monitor at: $API_URL/status/$JOB_ID"
TESTSCRIPT

chmod +x test-music-generation.sh
print_success "Created test-music-generation.sh"

# Desktop launcher (Linux)
if [[ "$OS" == "linux" ]]; then
    DESKTOP_FILE="$HOME/.local/share/applications/staticwaves-music-studio.desktop"

    cat > "$DESKTOP_FILE" << DESKTOPFILE
[Desktop Entry]
Version=1.0
Type=Application
Name=StaticWaves Music Studio
Comment=AI Music Generation Studio
Exec=$INSTALL_DIR/start-music-studio.sh
Icon=$INSTALL_DIR/music-engine/icon.png
Terminal=true
Categories=AudioVideo;Audio;
DESKTOPFILE

    chmod +x "$DESKTOP_FILE"
    print_success "Created desktop launcher"
fi

# Installation complete!
print_header "Installation Complete! 🎉"

echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║            🎉 StaticWaves Music Studio is ready! 🎉           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  Quick Start:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${PURPLE}1. Start everything:${NC}"
echo -e "     ${BLUE}./start-music-studio.sh${NC}"
echo ""
echo -e "  ${PURPLE}2. Open your browser:${NC}"
echo -e "     ${BLUE}http://localhost:5174${NC}"
echo ""
echo -e "  ${PURPLE}3. Generate music:${NC}"
echo -e "     ${BLUE}Click Auto tab → Generate Random Song${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  Useful Commands:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Start:     ${GREEN}./start-music-studio.sh${NC}"
echo -e "  Stop:      ${RED}./stop-music-studio.sh${NC}"
echo -e "  Test:      ${YELLOW}./test-music-generation.sh${NC}"
echo ""
echo -e "  Logs:      ${BLUE}cd music-engine && docker-compose logs -f${NC}"
echo -e "  API Docs:  ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  Features Available:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ✓ Automatic song generation (one click)"
echo -e "  ✓ 15+ genres with 80+ sub-genres"
echo -e "  ✓ 8 smart presets (workout, focus, sleep, etc.)"
echo -e "  ✓ Playlist generation (up to 20 songs)"
echo -e "  ✓ AI lyrics with Claude (optional)"
echo -e "  ✓ Professional song structures"
echo -e "  ✓ Beautiful web GUI"
echo -e "  ✓ Real-time progress tracking"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  Documentation:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Quick Start:  ${BLUE}music-engine/QUICKSTART.md${NC}"
echo -e "  Features:     ${BLUE}music-engine/FEATURES.md${NC}"
echo -e "  Full Guide:   ${BLUE}MUSIC_GUIDE.md${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Ready to make music! 🎵${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

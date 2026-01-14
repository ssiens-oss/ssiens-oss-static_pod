#!/bin/bash
set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     POD Pipeline Production Setup for RunPod            ║"
echo "║     Complete end-to-end installation                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if running on RunPod
if [ -d "/workspace" ]; then
    print_success "Detected RunPod environment"
    WORKSPACE="/workspace"
else
    print_warning "Not detected as RunPod, using current directory"
    WORKSPACE="$(pwd)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 1: System Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

print_status "Updating package lists..."
apt-get update -qq

print_status "Installing system dependencies..."
apt-get install -y -qq \
    python3.10 \
    python3-pip \
    python3-venv \
    git \
    wget \
    curl \
    vim \
    htop \
    > /dev/null

print_success "System dependencies installed"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 2: ComfyUI Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

COMFYUI_PATH="$WORKSPACE/ComfyUI"

if [ -d "$COMFYUI_PATH" ]; then
    print_warning "ComfyUI already exists at $COMFYUI_PATH"
    read -p "Reinstall? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$COMFYUI_PATH"
    else
        print_status "Skipping ComfyUI installation"
    fi
fi

if [ ! -d "$COMFYUI_PATH" ]; then
    print_status "Cloning ComfyUI..."
    git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFYUI_PATH" -q

    cd "$COMFYUI_PATH"

    print_status "Installing ComfyUI dependencies..."
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 -q
    pip3 install -r requirements.txt -q

    print_success "ComfyUI installed"
else
    print_status "ComfyUI already installed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 3: POD Gateway Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

GATEWAY_PATH="$WORKSPACE/gateway"

# Check if we're in the project repo
if [ -d "./gateway" ]; then
    print_status "Found gateway in current directory, copying to $GATEWAY_PATH"
    cp -r ./gateway "$GATEWAY_PATH"
elif [ ! -d "$GATEWAY_PATH" ]; then
    print_error "Gateway directory not found!"
    print_error "Please run this script from the repository root or ensure gateway/ exists"
    exit 1
fi

cd "$GATEWAY_PATH"

print_status "Creating Python virtual environment..."
python3 -m venv .venv

print_status "Installing gateway dependencies..."
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
deactivate

print_success "POD Gateway installed"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 4: Environment Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$GATEWAY_PATH/.env" ]; then
    print_warning "Existing .env file found"
    read -p "Overwrite? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Keeping existing .env"
    else
        rm "$GATEWAY_PATH/.env"
    fi
fi

if [ ! -f "$GATEWAY_PATH/.env" ]; then
    print_status "Creating .env configuration..."

    # Prompt for required values
    echo ""
    echo "Please provide the following configuration:"
    echo ""

    read -p "Printify API Key: " PRINTIFY_API_KEY
    read -p "Printify Shop ID: " PRINTIFY_SHOP_ID

    # Optional: Claude API key
    echo ""
    print_status "Claude API (optional - for AI prompt generation):"
    read -p "Anthropic API Key (press Enter to skip): " ANTHROPIC_API_KEY

    # Create .env file
    cat > "$GATEWAY_PATH/.env" <<ENVEOF
# ComfyUI Configuration
COMFYUI_API_URL=http://localhost:8188
COMFYUI_OUTPUT_DIR=$COMFYUI_PATH/output

# POD Gateway Configuration
POD_IMAGE_DIR=$COMFYUI_PATH/output
POD_STATE_FILE=/workspace/gateway-state/state.json
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false

# Printify Configuration
PRINTIFY_API_KEY=$PRINTIFY_API_KEY
PRINTIFY_SHOP_ID=$PRINTIFY_SHOP_ID
PRINTIFY_BLUEPRINT_ID=3
PRINTIFY_PROVIDER_ID=99

# Claude API (optional)
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Storage Configuration
STORAGE_TYPE=local
STORAGE_PATH=/data/designs

# Pipeline Configuration
AUTO_PUBLISH=false
ENABLE_PLATFORMS=printify
ENVEOF

    print_success ".env file created"
else
    print_status "Using existing .env file"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 5: Creating Startup Scripts"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create unified start script
cat > "$WORKSPACE/start-pod.sh" <<'STARTEOF'
#!/bin/bash
set -e

echo "🚀 Starting POD Pipeline..."

# Start ComfyUI
echo "⚙️  Starting ComfyUI..."
cd /workspace/ComfyUI
nohup python3 main.py --listen 0.0.0.0 --port 8188 > /var/log/comfyui.log 2>&1 &
COMFYUI_PID=$!
echo "   ComfyUI PID: $COMFYUI_PID"

# Wait for ComfyUI
echo "⏳ Waiting for ComfyUI..."
for i in {1..30}; do
    if curl -sf http://localhost:8188/system_stats > /dev/null 2>&1; then
        echo "✅ ComfyUI is ready"
        break
    fi
    sleep 2
done

# Start POD Gateway
echo "🎨 Starting POD Gateway..."
cd /workspace/gateway
source .venv/bin/activate
nohup python3 app/main.py > /var/log/gateway.log 2>&1 &
GATEWAY_PID=$!
echo "   Gateway PID: $GATEWAY_PID"

echo ""
echo "✅ All services started!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 ComfyUI:     http://localhost:8188"
echo "🖼️  Gateway:     http://localhost:5000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Expose ports 8188 and 5000 in RunPod UI"
echo ""
STARTEOF

chmod +x "$WORKSPACE/start-pod.sh"

# Create stop script
cat > "$WORKSPACE/stop-pod.sh" <<'STOPEOF'
#!/bin/bash

echo "🛑 Stopping POD Pipeline..."

pkill -f "python3 main.py --listen" && echo "✓ ComfyUI stopped" || echo "ComfyUI not running"
pkill -f "python3 app/main.py" && echo "✓ Gateway stopped" || echo "Gateway not running"

echo "✅ All services stopped"
STOPEOF

chmod +x "$WORKSPACE/stop-pod.sh"

# Create status script
cat > "$WORKSPACE/status-pod.sh" <<'STATUSEOF'
#!/bin/bash

echo "📊 POD Pipeline Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ComfyUI
if pgrep -f "python3 main.py --listen" > /dev/null; then
    echo "✅ ComfyUI:  Running (PID: $(pgrep -f 'python3 main.py --listen'))"
    curl -sf http://localhost:8188/system_stats > /dev/null && echo "   API:      Responding" || echo "   API:      Not responding"
else
    echo "❌ ComfyUI:  Not running"
fi

# Gateway
if pgrep -f "python3 app/main.py" > /dev/null; then
    echo "✅ Gateway:  Running (PID: $(pgrep -f 'python3 app/main.py'))"
    curl -sf http://localhost:5000/health > /dev/null && echo "   API:      Responding" || echo "   API:      Not responding"
else
    echo "❌ Gateway:  Not running"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
STATUSEOF

chmod +x "$WORKSPACE/status-pod.sh"

print_success "Startup scripts created"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 6: Creating Necessary Directories"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p /workspace/gateway-state
mkdir -p /data/designs
mkdir -p /var/log

print_success "Directories created"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                  ✅ Setup Complete!                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "  1. Start the services:"
echo "     $WORKSPACE/start-pod.sh"
echo ""
echo "  2. Check status:"
echo "     $WORKSPACE/status-pod.sh"
echo ""
echo "  3. Expose ports in RunPod UI:"
echo "     - Port 8188 (ComfyUI)"
echo "     - Port 5000 (Gateway)"
echo ""
echo "  4. Access the gateway:"
echo "     Open the RunPod URL for port 5000"
echo ""
echo "  5. View logs:"
echo "     tail -f /var/log/comfyui.log"
echo "     tail -f /var/log/gateway.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

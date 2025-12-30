#!/bin/bash
set -e

# StaticWaves OS Master Installer
# One-command installation for complete stack

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
║                    StaticWaves OS v1.0                        ║
║          AI-Powered POD Automation Platform                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo ""
echo "🚀 Installing StaticWaves POD Engine..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo "❌ Cannot detect OS"
    exit 1
fi

echo "📊 System Info:"
echo "  OS: $OS $VER"
echo "  Architecture: $(uname -m)"
echo ""

# Check for GPU
if command -v nvidia-smi &> /dev/null; then
    echo "🎮 GPU Detected:"
    nvidia-smi --query-gpu=name --format=csv,noheader
    GPU_AVAILABLE=1
else
    echo "⚠️  No NVIDIA GPU detected (CPU mode)"
    GPU_AVAILABLE=0
fi

echo ""
read -p "Continue installation? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 1
fi

# Update package lists
echo "📦 Updating package lists..."
apt-get update -qq

# Install dependencies
echo "📦 Installing system dependencies..."
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    curl \
    wget \
    git \
    nginx \
    build-essential

# Install Python packages
echo "🐍 Installing Python dependencies..."
pip3 install --upgrade pip -q
pip3 install -q \
    flask \
    flask-cors \
    requests \
    pillow \
    python-dotenv

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p /opt/staticwaves-pod
mkdir -p /opt/staticwaves-pod/data/{queue/{pending,processing,done,failed},designs,logs}

# Download or copy files
if [ -d "./api" ]; then
    # Installing from local directory
    echo "📦 Installing from local directory..."
    cp -r api /opt/staticwaves-pod/
    cp -r workers /opt/staticwaves-pod/
    cp -r config /opt/staticwaves-pod/
    cp -r systemd /opt/staticwaves-pod/
else
    # Clone from repository
    echo "📦 Cloning from GitHub..."
    git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git /tmp/staticwaves-install
    cp -r /tmp/staticwaves-install/api /opt/staticwaves-pod/
    cp -r /tmp/staticwaves-install/workers /opt/staticwaves-pod/
    cp -r /tmp/staticwaves-install/config /opt/staticwaves-pod/
    cp -r /tmp/staticwaves-install/systemd /opt/staticwaves-pod/
    rm -rf /tmp/staticwaves-install
fi

# Set permissions
chmod -R 755 /opt/staticwaves-pod
chmod -R 777 /opt/staticwaves-pod/data

# Install systemd services
echo "⚙️  Installing systemd services..."
cp /opt/staticwaves-pod/systemd/*.service /usr/lib/systemd/system/
systemctl daemon-reload

# Enable and start API service
echo "🚀 Starting services..."
systemctl enable staticwaves-pod-api.service
systemctl start staticwaves-pod-api.service

# Configure environment
if [ ! -f /opt/staticwaves-pod/config/.env ]; then
    echo "📝 Creating environment configuration..."
    cp /opt/staticwaves-pod/config/env.example /opt/staticwaves-pod/config/.env
fi

# Install ComfyUI (if GPU available and requested)
if [ $GPU_AVAILABLE -eq 1 ]; then
    echo ""
    read -p "Install ComfyUI for GPU image generation? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🎨 Installing ComfyUI..."
        if [ ! -d /opt/ComfyUI ]; then
            git clone https://github.com/comfyanonymous/ComfyUI.git /opt/ComfyUI
            pip3 install -r /opt/ComfyUI/requirements.txt -q
            systemctl enable staticwaves-comfyui.service
            systemctl start staticwaves-comfyui.service
        fi
    fi
fi

# Setup complete
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║              ✅ Installation Complete! ✅                     ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 System Status:"
systemctl status staticwaves-pod-api.service --no-pager -l | head -5
echo ""
echo "🌐 API Server: http://localhost:5000"
echo "📖 Health Check: http://localhost:5000/health"
echo ""
echo "⚙️  NEXT STEPS:"
echo ""
echo "1. Configure API Keys:"
echo "   sudo nano /opt/staticwaves-pod/config/.env"
echo ""
echo "2. Start the worker:"
echo "   sudo systemctl start staticwaves-pod-worker.service"
echo ""
echo "3. Check logs:"
echo "   sudo journalctl -u staticwaves-pod-api -f"
echo ""
echo "📚 Documentation:"
echo "   https://github.com/ssiens-oss/ssiens-oss-static_pod"
echo ""
echo "🆘 Support:"
echo "   https://github.com/ssiens-oss/ssiens-oss-static_pod/issues"
echo ""

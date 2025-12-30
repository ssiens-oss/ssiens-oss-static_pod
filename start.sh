#!/bin/bash
# Quick Start Script for StaticWaves POD

set -e

echo "🚀 StaticWaves POD - Quick Start"
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python $(python3 --version | cut -d' ' -f2) found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install --quiet --break-system-packages flask flask-cors requests pillow python-dotenv 2>/dev/null || \
pip3 install --quiet flask flask-cors requests pillow python-dotenv

echo "✅ Dependencies installed"

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p data/{queue/{pending,processing,done,failed},designs,logs,agents}
mkdir -p config

echo "✅ Directories created"

# Create .env if it doesn't exist
if [ ! -f config/.env ]; then
    echo ""
    echo "📝 Creating config/.env..."
    cp config/env.example config/.env 2>/dev/null || cat > config/.env <<EOF
# StaticWaves POD Configuration
PORT=5000
STATICWAVES_DEV_MODE=true
STATICWAVES_TELEMETRY=false
EOF
    echo "✅ Config created (dev mode enabled)"
fi

# Start API server
echo ""
echo "🌐 Starting API server on http://localhost:5000"
echo ""

python3 api/app.py

#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  POD Gateway Installer (RunPod Safe)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Detect directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo

# Check requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    echo "Aborting installation"
    exit 1
fi

echo "✓ requirements.txt found"
echo

# Create venv
echo "🐍 Creating Python virtual environment..."
python3 -m venv .venv
echo "✓ Virtual environment created"
echo

# Activate and install
echo "📦 Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo

# Create state directory
mkdir -p /workspace/gateway
echo "✓ State directory created"
echo

# Check for .env
if [ ! -f ".env" ]; then
    echo "⚠ No .env file found"
    echo "Copy .env.example to .env and configure"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Installation Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "▶ Start gateway with:"
echo "  source .venv/bin/activate && python app/main.py"
echo
echo "▶ Expose port 5000 in RunPod UI"
echo

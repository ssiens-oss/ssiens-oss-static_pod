#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  POD Dashboard Installer (RunPod Safe)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

echo "✓ requirements.txt found"
echo

echo "🐍 Creating Python virtual environment..."
python3 -m venv .venv
echo "✓ Virtual environment created"
echo

echo "📦 Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo

mkdir -p /workspace/dashboard /workspace/prompts
echo "✓ Directories created"
echo

if [ ! -f ".env" ]; then
    echo "⚠ No .env file found"
    echo "Copy .env.example to .env and configure"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Installation Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "▶ Start dashboard with:"
echo "  source .venv/bin/activate && python app/main.py"
echo
echo "▶ Access at http://localhost:5000"
echo

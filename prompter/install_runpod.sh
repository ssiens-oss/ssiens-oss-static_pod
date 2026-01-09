#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AI Auto-Prompter Installer (RunPod Safe)"
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

# Create output directory
mkdir -p /workspace/prompts
echo "✓ Output directory created"
echo

# Check for .env
if [ ! -f ".env" ]; then
    echo "⚠ No .env file found"
    echo "Copy .env.example to .env and add ANTHROPIC_API_KEY"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Installation Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "▶ Start prompter with:"
echo "  source .venv/bin/activate && python app/main.py"
echo
echo "▶ Expose port 5001 in RunPod UI"
echo

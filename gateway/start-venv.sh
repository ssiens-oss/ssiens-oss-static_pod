#!/bin/bash
# POD Gateway Startup Script with Virtual Environment
# Handles venv creation and activation automatically

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"

cd "$SCRIPT_DIR"

echo "🚀 Starting POD Gateway..."
echo "📁 Working directory: $(pwd)"
echo ""

# Load .env if it exists
if [ -f "../.env" ]; then
    echo "📋 Loading environment from ../.env"
    set -a
    source ../.env
    set +a
fi

# Create or verify virtual environment
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check and install dependencies
echo "🔍 Checking dependencies..."
python -c "import flask, requests, PIL" 2>/dev/null || {
    echo "⚠️  Missing dependencies. Installing..."
    pip install -q flask requests pillow python-dotenv
    echo "✅ Dependencies installed"
}

# Print configuration
echo ""
echo "⚙️  Configuration:"
echo "   Blueprint ID: ${PRINTIFY_BLUEPRINT_ID:-77} (Gildan 18500 Hoodie)"
echo "   Provider ID:  ${PRINTIFY_PROVIDER_ID:-39} (SwiftPOD)"
echo "   Default Price: \$$(python -c "print(${PRINTIFY_DEFAULT_PRICE_CENTS:-3499}/100)" 2>/dev/null || echo "34.99")"
echo "   Port: ${FLASK_PORT:-5000}"
echo "   Python: $(which python)"
echo ""

# Start the server
echo "🌐 Starting Flask server..."
echo "   Access at: http://0.0.0.0:${FLASK_PORT:-5000}"
echo "   Press Ctrl+C to stop"
echo ""

# Set PYTHONPATH to include the gateway directory
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

python app/main.py

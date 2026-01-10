#!/bin/bash
# Start AIM Proofing Engine Monitoring Service
# This script starts the AIM engine to monitor directories for new images

set -e

echo "🚀 Starting AIM Proofing Engine..."
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "    AI analysis will be disabled without ANTHROPIC_API_KEY"
    echo ""
fi

# Check if config exists
if [ ! -f "aim_config.json" ]; then
    echo "❌ Error: aim_config.json not found"
    echo "    Please create aim_config.json with your watch directories"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "✓ Activating virtual environment..."
    source .venv/bin/activate
fi

# Check dependencies
echo "✓ Checking dependencies..."
python3 -c "import flask, PIL, anthropic, watchdog" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

# Test configuration
echo "✓ Testing configuration..."
python3 aim_cli.py test-config aim_config.json

echo ""
echo "✓ Starting monitoring service..."
echo "  Press Ctrl+C to stop"
echo ""

# Start monitoring with gateway integration
python3 aim_cli.py monitor --config aim_config.json --gateway-integration

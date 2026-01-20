#!/bin/bash
set -e

# Get the actual directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting POD Gateway..."
echo "Working directory: $SCRIPT_DIR"

# Set IMAGE_DIR to gateway/images within the project
export POD_IMAGE_DIR="$SCRIPT_DIR/gateway/images"
mkdir -p "$POD_IMAGE_DIR"

echo "Image directory: $POD_IMAGE_DIR"

# Activate venv
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "Virtual environment activated"
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "WARNING: No virtual environment found"
fi

# Start the gateway
cd gateway
PYTHONPATH=$(pwd) python -m app.main

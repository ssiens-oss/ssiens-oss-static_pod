#!/bin/bash
# POD Gateway Start Script
# Usage: ./run-gateway.sh

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONPATH="$SCRIPT_DIR"

echo "🚀 Starting POD Gateway..."
echo "📁 Directory: $(pwd)"
echo "🌐 Web UI: http://localhost:5000"
echo ""

.venv/bin/python app/main.py

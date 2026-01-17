#!/bin/bash
# POD Gateway Start Script
# Usage: ./run-gateway.sh

cd ~/ssiens-oss-static_pod/gateway
export PYTHONPATH=~/ssiens-oss-static_pod/gateway

echo "🚀 Starting POD Gateway..."
echo "📁 Directory: $(pwd)"
echo "🌐 Web UI: http://localhost:5000"
echo ""

.venv/bin/python app/main.py

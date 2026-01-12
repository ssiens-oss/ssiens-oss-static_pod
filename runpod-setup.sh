#!/bin/bash

###############################################################################
# RunPod Complete Setup - Install Node.js and Deploy POD Engine
###############################################################################

set -e

echo "=========================================="
echo "  Installing Node.js on RunPod"
echo "=========================================="

# Install Node.js 20.x (LTS)
echo "▶ Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

echo "✓ Node.js installed:"
node --version
npm --version

echo ""
echo "=========================================="
echo "  Deploying POD Engine"
echo "=========================================="

# Run deployment
./deploy-pod-engine.sh runpod

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Configure API keys: nano .env"
echo "  2. Start services: ./start-pod-engine.sh"
echo ""

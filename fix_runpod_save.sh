#!/bin/bash
set -e

# Kill gateway
pkill -f "gateway/app/main.py" || true
sleep 2

# Create gateway/images directory
mkdir -p /home/user/ssiens-oss-static_pod/gateway/images

# Set IMAGE_DIR environment variable
export POD_IMAGE_DIR="/home/user/ssiens-oss-static_pod/gateway/images"

# Inject into start script if not already there
if ! grep -q "POD_IMAGE_DIR" start-gateway-runpod.sh; then
    sed -i '2 i export POD_IMAGE_DIR="/home/user/ssiens-oss-static_pod/gateway/images"' start-gateway-runpod.sh
fi

echo "✓ IMAGE_DIR set to: $POD_IMAGE_DIR"
echo "✓ Directory exists: $(ls -ld /home/user/ssiens-oss-static_pod/gateway/images)"
echo "✓ Restarting gateway with proper config..."

# Restart gateway
./start-gateway-runpod.sh

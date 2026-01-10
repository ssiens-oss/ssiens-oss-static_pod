#!/bin/bash
# RunPod Container Setup Script
# This ensures the POD pipeline runs correctly on RunPod containers

set -e

echo "🚀 Setting up POD Pipeline for RunPod"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Determine the actual repo location
if [ -d "/home/user/ssiens-oss-static_pod/.git" ]; then
    REPO_DIR="/home/user/ssiens-oss-static_pod"
    echo "✓ Found git repo at: $REPO_DIR"
elif [ -d "/workspace/ssiens-oss-static_pod/.git" ]; then
    REPO_DIR="/workspace/ssiens-oss-static_pod"
    echo "✓ Found git repo at: $REPO_DIR"
else
    echo "❌ No git repository found"
    echo "   Please clone the repo first:"
    echo "   cd /workspace && git clone <repo-url> ssiens-oss-static_pod"
    exit 1
fi

cd "$REPO_DIR"

echo ""
echo "1. Cleaning old workspace directory..."
if [ -d "/workspace/ssiens-oss-static_pod" ] && [ "$REPO_DIR" != "/workspace/ssiens-oss-static_pod" ]; then
    echo "   Removing old files from /workspace/ssiens-oss-static_pod"
    rm -rf /workspace/ssiens-oss-static_pod
fi

echo ""
echo "2. Installing pod command..."
sudo ln -sf "$REPO_DIR/pod" /usr/local/bin/pod
echo "   ✓ Installed to /usr/local/bin/pod"

echo ""
echo "3. Updating pod script to use correct path..."
sudo sed -i "s|REPO_ROOT=.*|REPO_ROOT=\"$REPO_DIR\"|" /usr/local/bin/pod
echo "   ✓ Updated REPO_ROOT to $REPO_DIR"

echo ""
echo "4. Checking dependencies..."
pip list | grep -q fastapi || pip install -q fastapi uvicorn
echo "   ✓ FastAPI installed"

echo ""
echo "5. Creating output directory..."
mkdir -p "$REPO_DIR/output"
mkdir -p "$REPO_DIR/ComfyUI/output" 2>/dev/null || true
echo "   ✓ Output directories ready"

echo ""
echo "6. Stopping any running services..."
pkill -f "uvicorn gallery.server" 2>/dev/null || true
pkill -f "http.server 8088" 2>/dev/null || true
sleep 1

echo ""
echo "7. Starting POD Pipeline..."
cd "$REPO_DIR"
./run-pod-pipeline.sh

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Setup Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Repository: $REPO_DIR"
echo ""
echo "Next steps:"
echo "  pod status     - Check pipeline status"
echo "  pod logs       - View logs"
echo ""
echo "Access:"
echo "  Web Gallery: http://localhost:8088/view-gallery.html"
echo "  API Docs:    http://localhost:8099"
echo ""

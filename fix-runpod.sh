#!/bin/bash
# Quick fix for RunPod container setup

echo "🔧 Fixing RunPod Container Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Find the actual repository location
if [ -d "/workspace/ssiens-oss-static_pod/.git" ]; then
    REPO_DIR="/workspace/ssiens-oss-static_pod"
elif [ -d "/home/user/ssiens-oss-static_pod/.git" ]; then
    REPO_DIR="/home/user/ssiens-oss-static_pod"
else
    echo "❌ No git repository found"
    exit 1
fi

echo "✓ Found repository at: $REPO_DIR"
cd "$REPO_DIR"

echo ""
echo "1. Fixing git merge conflict..."
rm -f gallery/__init__.py
git checkout gallery/__init__.py 2>/dev/null || git pull origin claude/setup-pod-pipeline-KYYxL
echo "   ✓ Merge conflict resolved"

echo ""
echo "2. Pulling latest changes..."
git pull origin claude/setup-pod-pipeline-KYYxL
echo "   ✓ Repository updated"

echo ""
echo "3. Updating pod command to use correct path..."
sudo sed -i "s|REPO_ROOT=.*|REPO_ROOT=\"$REPO_DIR\"|" /usr/local/bin/pod
echo "   ✓ Pod command updated"

echo ""
echo "4. Restarting services..."
"$REPO_DIR"/stop-pod-pipeline.sh 2>/dev/null || pkill -f "uvicorn gallery.server"
sleep 2
"$REPO_DIR"/run-pod-pipeline.sh

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Setup Fixed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Access:"
echo "  Dashboard: http://localhost:8099"
echo "  ComfyUI:   http://localhost:8188"
echo ""
echo "Commands:"
echo "  pod status  - Check status"
echo "  pod stop    - Stop services"
echo "  pod start   - Start services"
echo ""

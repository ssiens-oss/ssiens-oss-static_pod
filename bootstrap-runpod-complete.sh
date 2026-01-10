#!/bin/bash
# Complete RunPod Container Bootstrap
# This will clean up the old workspace files and set everything to use the correct git repo

set -e

echo "🔧 RunPod Container Complete Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Find the git repository
if [ -d "/home/user/ssiens-oss-static_pod/.git" ]; then
    REPO_DIR="/home/user/ssiens-oss-static_pod"
    echo "✓ Found git repository at: $REPO_DIR"
elif [ -d "/workspace/ssiens-oss-static_pod/.git" ]; then
    REPO_DIR="/workspace/ssiens-oss-static_pod"
    echo "✓ Found git repository at: $REPO_DIR"
else
    echo "❌ No git repository found!"
    echo "   Please clone first: git clone <repo-url> /home/user/ssiens-oss-static_pod"
    exit 1
fi

echo ""
echo "Step 1: Cleaning old workspace files..."
if [ -d "/workspace/ssiens-oss-static_pod" ] && [ ! -d "/workspace/ssiens-oss-static_pod/.git" ]; then
    echo "   Found old non-git directory at /workspace/ssiens-oss-static_pod"
    rm -rf /workspace/ssiens-oss-static_pod
    echo "   ✓ Removed old files"
fi

echo ""
echo "Step 2: Pulling latest code..."
cd "$REPO_DIR"
git fetch origin claude/setup-pod-pipeline-KYYxL

# Fix any merge conflicts
if [ -f "gallery/__init__.py" ] && [ ! -d ".git" ]; then
    rm -f gallery/__init__.py
fi

git reset --hard origin/claude/setup-pod-pipeline-KYYxL
echo "   ✓ Repository updated to latest"

echo ""
echo "Step 3: Verifying gallery module..."
if [ -f "$REPO_DIR/gallery/server.py" ]; then
    echo "   ✓ Gallery server found"
    if [ -f "$REPO_DIR/gallery/__init__.py" ]; then
        echo "   ✓ Gallery __init__.py found"
    else
        echo "   ✗ Creating gallery/__init__.py"
        touch "$REPO_DIR/gallery/__init__.py"
    fi
else
    echo "   ❌ Gallery server not found!"
    exit 1
fi

echo ""
echo "Step 4: Installing dependencies..."
pip install -q fastapi uvicorn 2>/dev/null || pip install fastapi uvicorn
echo "   ✓ Dependencies installed"

echo ""
echo "Step 5: Updating pod command..."
if [ -f "/usr/local/bin/pod" ]; then
    sudo sed -i "s|REPO_ROOT=.*|REPO_ROOT=\"$REPO_DIR\"|" /usr/local/bin/pod
    echo "   ✓ Pod command updated"
else
    sudo ln -sf "$REPO_DIR/pod" /usr/local/bin/pod
    sudo sed -i "s|REPO_ROOT=.*|REPO_ROOT=\"$REPO_DIR\"|" /usr/local/bin/pod
    echo "   ✓ Pod command installed"
fi

echo ""
echo "Step 6: Creating output directory..."
mkdir -p "$REPO_DIR/output"
mkdir -p "$REPO_DIR/ComfyUI/output" 2>/dev/null || true
echo "   ✓ Output directories ready"

echo ""
echo "Step 7: Stopping old services..."
pkill -f "ComfyUI/main.py" 2>/dev/null || true
pkill -f "uvicorn gallery.server" 2>/dev/null || true
pkill -f "http.server 8088" 2>/dev/null || true
sleep 2

echo ""
echo "Step 8: Starting POD Pipeline..."
cd "$REPO_DIR"
"$REPO_DIR/run-pod-pipeline.sh"

sleep 3

echo ""
echo "Step 9: Verifying services..."
if curl -s http://localhost:8099/ | grep -q "POD Gallery Dashboard"; then
    echo "   ✓ Gallery dashboard is running"
else
    echo "   ⚠ Gallery might not be running, checking logs..."
    tail -10 "$REPO_DIR/gallery.log"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Bootstrap Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Repository: $REPO_DIR"
echo ""
echo "Access:"
echo "  Dashboard: http://localhost:8099"
echo "  ComfyUI:   http://localhost:8188"
echo ""
echo "Commands:"
echo "  pod status  - Check services"
echo "  pod stop    - Stop services"
echo "  pod start   - Start services"
echo "  pod logs    - View gallery logs"
echo ""

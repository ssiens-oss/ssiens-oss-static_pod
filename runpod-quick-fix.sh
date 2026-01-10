#!/bin/bash
# One-command fix for RunPod container
# This completely resets everything to use the correct git repository

set -e

echo "🔧 RunPod Container Quick Fix"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Step 1: Stop all services
echo "1. Stopping all services..."
pkill -f "ComfyUI" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "http.server" 2>/dev/null || true
sleep 1

# Step 2: Remove old workspace directory (not a git repo)
if [ -d "/workspace/ssiens-oss-static_pod" ] && [ ! -d "/workspace/ssiens-oss-static_pod/.git" ]; then
    echo "2. Removing old non-git workspace directory..."
    rm -rf /workspace/ssiens-oss-static_pod
    echo "   ✓ Removed"
else
    echo "2. Workspace directory OK"
fi

# Step 3: Determine repository location
if [ -d "/home/user/ssiens-oss-static_pod/.git" ]; then
    REPO_DIR="/home/user/ssiens-oss-static_pod"
    echo "3. Using repository at: $REPO_DIR"
else
    echo "3. Cloning repository to /home/user/ssiens-oss-static_pod..."
    cd /home/user
    git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
    cd ssiens-oss-static_pod
    git checkout claude/setup-pod-pipeline-KYYxL
    REPO_DIR="/home/user/ssiens-oss-static_pod"
fi

cd "$REPO_DIR"

# Step 4: Pull latest changes
echo "4. Updating to latest code..."
git fetch origin claude/setup-pod-pipeline-KYYxL
git reset --hard origin/claude/setup-pod-pipeline-KYYxL
echo "   ✓ Updated"

# Step 5: Install dependencies
echo "5. Installing dependencies..."
pip install -q fastapi uvicorn 2>/dev/null || pip install fastapi uvicorn
echo "   ✓ Installed"

# Step 6: Create output directory
echo "6. Creating output directory..."
mkdir -p "$REPO_DIR/output"
echo "   ✓ Ready"

# Step 7: Install pod command
echo "7. Installing pod command..."
sudo ln -sf "$REPO_DIR/pod" /usr/local/bin/pod
sudo sed -i "s|REPO_ROOT=.*|REPO_ROOT=\"$REPO_DIR\"|" /usr/local/bin/pod
echo "   ✓ Installed"

# Step 8: Start services (WITHOUT ComfyUI)
echo "8. Starting POD Pipeline (Gallery only)..."
cd "$REPO_DIR"

# Start Gallery Bridge
nohup python3 -m uvicorn gallery.server:app --host 0.0.0.0 --port 8099 >> "$REPO_DIR/gallery.log" 2>&1 &
GALLERY_PID=$!

# Start Web UI
nohup python3 -m http.server 8088 >> "$REPO_DIR/webui.log" 2>&1 &
WEBUI_PID=$!

sleep 3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ POD Pipeline Running (Gallery Only)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Access:"
echo "  Dashboard:  http://localhost:8099"
echo "  Old UI:     http://localhost:8088/view-gallery.html"
echo ""
echo "Commands:"
echo "  pod status  - Check services"
echo "  pod stop    - Stop services"
echo "  pod start   - Start services"
echo ""
echo "Note: ComfyUI not installed."
echo "To install ComfyUI, run:"
echo "  cd $REPO_DIR"
echo "  git clone https://github.com/comfyanonymous/ComfyUI.git"
echo "  cd ComfyUI && pip install -r requirements.txt"
echo ""

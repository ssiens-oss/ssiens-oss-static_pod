#!/bin/bash
#
# StaticWaves POD Engine - Fresh RunPod Deployment
# One-command setup for new RunPod instances
#

set -e

echo "╔════════════════════════════════════════╗"
echo "║  StaticWaves POD Engine - Fresh Deploy ║"
echo "║  For New RunPod Instances              ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Detect if we're already in the repo
if [ -f "deploy-runpod.sh" ]; then
    echo -e "${YELLOW}⚠${NC}  Already in ssiens-oss-static_pod directory"
    echo "Running existing deployment..."
    exec ./deploy-runpod.sh
fi

echo -e "${BLUE}→${NC} Checking prerequisites..."
echo ""

# Check for required tools
command -v git >/dev/null 2>&1 || { echo -e "${RED}✗${NC} git is required but not installed. Aborting."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}✗${NC} python3 is required but not installed. Aborting."; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "${RED}✗${NC} node is required but not installed. Aborting."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo -e "${RED}✗${NC} npm is required but not installed. Aborting."; exit 1; }

echo -e "${GREEN}✓${NC} All prerequisites found"
echo ""

# Step 1: Clone repository
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📥 Step 1: Cloning Repository"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

REPO_DIR="$HOME/ssiens-oss-static_pod"

if [ -d "$REPO_DIR" ]; then
    echo -e "${YELLOW}⚠${NC}  Repository already exists at $REPO_DIR"
    read -p "Remove and re-clone? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$REPO_DIR"
        echo -e "${GREEN}✓${NC} Removed existing directory"
    else
        echo "Using existing repository..."
        cd "$REPO_DIR"
    fi
else
    echo "Cloning from GitHub..."
    git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git "$REPO_DIR"
    cd "$REPO_DIR"
    echo -e "${GREEN}✓${NC} Repository cloned"
fi

echo ""

# Step 2: Checkout deployment branch
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌿 Step 2: Checking Out Deployment Branch"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

git fetch origin
git checkout claude/push-images-printify-JLjuQ
git pull origin claude/push-images-printify-JLjuQ

echo -e "${GREEN}✓${NC} On deployment branch"
echo ""

# Step 3: Get RunPod pod ID
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏷️  Step 3: RunPod Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Try to detect pod ID from hostname or SSH connection
POD_ID=$(hostname 2>/dev/null || echo "unknown")
if [ "$POD_ID" = "unknown" ] || [ -z "$POD_ID" ]; then
    POD_ID=$(echo $SSH_CONNECTION | awk '{print $3}' | cut -d'-' -f1 2>/dev/null || echo "unknown")
fi

echo "Detected Pod ID: $POD_ID"
echo ""

# Step 4: Run deployment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Step 4: Running Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Make scripts executable
chmod +x deploy-runpod.sh stop-pod-engine.sh test-run.sh

# Run the main deployment script
./deploy-runpod.sh

# Success
echo ""
echo "╔════════════════════════════════════════╗"
echo "║        🎉 Deployment Complete! 🎉      ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓${NC} POD Engine deployed successfully!"
echo ""
echo "📍 Location: $REPO_DIR"
echo ""
echo "🌐 Access via RunPod Dashboard:"
echo "   1. Go to your RunPod dashboard"
echo "   2. Find pod: $POD_ID"
echo "   3. Click: ${BLUE}Port 5174 → HTTP Service${NC} (Main App)"
echo "   4. Click: ${BLUE}Port 8188 → HTTP Service${NC} (API Docs)"
echo ""
echo "📚 Quick Commands:"
echo "   cd $REPO_DIR"
echo "   ./test-run.sh           # Quick start"
echo "   ./stop-pod-engine.sh    # Stop services"
echo "   tail -f logs/*.log      # View logs"
echo ""
echo "📖 Documentation:"
echo "   RUNPOD_FRESH_DEPLOY.md  # This deployment guide"
echo "   README_FULLSTACK_APP.md # Complete app guide"
echo "   AI_GENERATION_GUIDE.md  # AI features guide"
echo ""

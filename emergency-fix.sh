#!/bin/bash
# Emergency fix for merge conflicts
# This will reset your repository to a clean state and pull the working version

set -e

echo "🔧 Fixing merge conflicts in your repository..."
echo ""

cd ~/ssiens-oss-static_pod

# Show current status
echo "📊 Current status:"
git status --short
echo ""

# Abort any merge
echo "⏹️  Aborting any in-progress merge..."
git merge --abort 2>/dev/null || echo "  No merge in progress"

# Reset to HEAD
echo "🔄 Resetting to clean state..."
git reset --hard HEAD

# Fetch latest from remote
echo "📡 Fetching from remote..."
git fetch origin claude/review-changes-mkljilavyj0p92rc-yIHnQ

# Force checkout from remote
echo "📥 Checking out clean version from remote..."
git checkout origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- gateway/app/main.py
git checkout origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- gateway/app/runpod_adapter.py
git checkout origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- gateway/app/config.py
git checkout origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- RUNPOD_SETUP.md

# Verify no syntax errors
echo "🔍 Verifying Python syntax..."
python3 -m py_compile gateway/app/main.py && echo "  ✅ main.py syntax OK" || echo "  ❌ main.py has syntax errors"
python3 -m py_compile gateway/app/runpod_adapter.py && echo "  ✅ runpod_adapter.py syntax OK" || echo "  ❌ runpod_adapter.py has syntax errors"

echo ""
echo "✅ Files restored from remote!"
echo ""
echo "📋 Next: Configure .env with your RunPod credentials:"
echo "   See .env.runpod-config for your specific credentials"
echo ""
echo "   Or run the all-in-one script:"
echo "   bash start-gateway-runpod.sh"

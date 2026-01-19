#!/bin/bash
# Ultimate fix script for merge conflicts
# This will completely reset your repository to a working state

echo "🔧 EMERGENCY FIX - Resolving merge conflicts"
echo "=============================================="
echo ""

# Navigate to repo root
cd ~/ssiens-oss-static_pod || { echo "❌ Can't find repository"; exit 1; }

echo "1️⃣  Resetting repository state..."

# Remove merge state files
rm -f .git/MERGE_HEAD .git/MERGE_MODE .git/MERGE_MSG 2>/dev/null

# Reset to last good commit
git reset --hard origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ 2>/dev/null || {
    echo "   Fetching latest from remote..."
    git fetch origin claude/review-changes-mkljilavyj0p92rc-yIHnQ
    git reset --hard origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ
}

echo "   ✅ Repository reset to clean state"
echo ""

echo "2️⃣  Verifying files..."

# Verify no conflict markers remain
if grep -r "<<<<<<< \|>>>>>>> \|=======" gateway/app/*.py 2>/dev/null; then
    echo "   ❌ Still found conflict markers, forcing clean checkout..."
    git checkout --force origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- gateway/app/
    git checkout --force origin/claude/review-changes-mkljilavyj0p92rc-yIHnQ -- RUNPOD_SETUP.md
fi

# Test Python syntax
echo "   Testing Python syntax..."
if python3 -m py_compile gateway/app/main.py 2>/dev/null; then
    echo "   ✅ main.py syntax OK"
else
    echo "   ❌ main.py still has errors"
    exit 1
fi

if python3 -m py_compile gateway/app/runpod_adapter.py 2>/dev/null; then
    echo "   ✅ runpod_adapter.py syntax OK"
else
    echo "   ❌ runpod_adapter.py still has errors"
    exit 1
fi

echo ""
echo "✅ Repository is clean!"
echo ""
echo "📋 Next steps:"
echo ""
echo "Configure .env with RunPod credentials:"
echo "  (Check .env.runpod-config for your specific credentials)"
echo ""
echo "Then start gateway:"
echo "  cd gateway && PYTHONPATH=\$(pwd) python3 -m app.main"
echo ""

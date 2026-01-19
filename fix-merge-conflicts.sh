#!/bin/bash
# Fix merge conflicts by using remote version

echo "🔧 Fixing merge conflicts..."
echo ""

# Abort any ongoing merge
git merge --abort 2>/dev/null || true

# Reset to current HEAD
git reset --hard HEAD

# Pull fresh from remote
echo "📥 Pulling latest from remote..."
git pull origin claude/review-changes-mkljilavyj0p92rc-yIHnQ

echo ""
echo "✅ Repository cleaned and updated!"
echo ""
echo "📋 Next steps:"
echo "1. Configure .env with RunPod credentials"
echo "2. Start gateway:"
echo "   cd gateway"
echo "   PYTHONPATH=\$(pwd) python3 -m app.main"

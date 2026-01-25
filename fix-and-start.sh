#!/bin/bash
# Fix gateway and start it

cd ~/ssiens-oss-static_pod

echo "🔧 Fixing gateway..."

# Reset gateway files to remote version
git fetch origin claude/fix-pod-pipeline-gateway-40qt9
git checkout origin/claude/fix-pod-pipeline-gateway-40qt9 -- gateway/app/main.py
git checkout origin/claude/fix-pod-pipeline-gateway-40qt9 -- gateway/app/config.py

# Clear Python cache
cd gateway
rm -rf app/__pycache__
find . -name "*.pyc" -delete 2>/dev/null

echo "✅ Files reset and cache cleared"
echo ""
echo "🚀 Starting gateway..."

source ../.venv/bin/activate
PYTHONPATH=$(pwd) python app/main.py

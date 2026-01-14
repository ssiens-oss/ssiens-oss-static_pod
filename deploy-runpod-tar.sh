#!/bin/bash
set -e

# Check for required environment variables
if [ -z "$RUNPOD_HOST" ]; then
    echo "❌ Error: RUNPOD_HOST not set"
    echo "Example: export RUNPOD_HOST='your-pod-id@ssh.runpod.io'"
    exit 1
fi

RUNPOD_KEY="${RUNPOD_KEY:-$HOME/.ssh/id_ed25519}"

echo "╔════════════════════════════════════════════════════╗"
echo "║  Deploying to RunPod (tar over SSH)               ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "🎯 Target: $RUNPOD_HOST"
echo "🔑 SSH Key: $RUNPOD_KEY"
echo ""

# Check if .env exists locally
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: No .env file found locally"
    echo "   You'll need to configure environment variables on RunPod"
    echo ""
fi

echo "📁 Creating remote directory..."
ssh -T -i "$RUNPOD_KEY" -o StrictHostKeyChecking=no "$RUNPOD_HOST" "mkdir -p /workspace/app" 2>&1 | grep -v "RUNPOD" || true

echo "📦 Transferring files via tar over SSH..."
tar czf - --exclude='node_modules' --exclude='.git' --exclude='dist' --exclude='*.log' . | \
  ssh -T -i "$RUNPOD_KEY" -o StrictHostKeyChecking=no "$RUNPOD_HOST" "cd /workspace/app && tar xzf -" 2>&1 | grep -v "RUNPOD" || true

echo "✓ Files transferred!"
echo ""

# Only transfer .env if it exists and user confirms
if [ -f ".env" ]; then
    echo "📋 Local .env file found."
    read -p "Transfer .env to RunPod? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔐 Transferring .env file..."
        scp -i "$RUNPOD_KEY" -o StrictHostKeyChecking=no .env "$RUNPOD_HOST:/workspace/app/.env" 2>&1 | grep -v "RUNPOD" || true
        echo "✓ .env transferred!"
    else
        echo "⚠️  Skipped .env transfer. You'll need to configure manually."
    fi
else
    echo "⚠️  No .env file to transfer."
    echo "   Copy .env.example and configure on RunPod:"
    echo "   cp .env.example .env && nano .env"
fi

echo ""
echo "📦 Installing dependencies..."
ssh -T -i "$RUNPOD_KEY" -o StrictHostKeyChecking=no "$RUNPOD_HOST" "cd /workspace/app && npm install" 2>&1 | grep -v "RUNPOD" || true

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║  ✅ Deployment Complete!                          ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. SSH into RunPod:"
echo "     ssh -i $RUNPOD_KEY $RUNPOD_HOST"
echo ""
echo "  2. Configure environment (if not transferred):"
echo "     cd /workspace/app"
echo "     cp .env.example .env"
echo "     nano .env"
echo ""
echo "  3. Test the pipeline:"
echo "     npm run pipeline:single -- --help"

#!/bin/bash
# RunPod Auto-Start Script
# Place this in /workspace and it will run on pod boot

set -e

echo "🚀 RunPod Boot - Initializing StaticWaves Forge..."

# Wait for system to be ready
sleep 5

# Clone/update repository if needed
REPO_DIR="/workspace/ssiens-oss-static_pod"
if [ ! -d "$REPO_DIR" ]; then
    echo "📥 Cloning StaticWaves Forge repository..."
    cd /workspace
    git clone -b claude/ai-3d-asset-engine-Q6XOw \
        https://github.com/ssiens-oss/ssiens-oss-static_pod.git
fi

# Find the start script
SCRIPT_PATH="$REPO_DIR/staticwaves-forge/start-unified.sh"
if [ -f "$SCRIPT_PATH" ]; then
    echo "▶️  Launching unified boot system..."
    bash "$SCRIPT_PATH" start
else
    echo "❌ Startup script not found at: $SCRIPT_PATH"
    echo "Available files:"
    ls -la "$REPO_DIR/staticwaves-forge/" || true
    exit 1
fi

echo "✅ StaticWaves Forge auto-start complete!"

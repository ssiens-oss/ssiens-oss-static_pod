#!/bin/bash
# RunPod Auto-Start Script
# Place this in /workspace and it will run on pod boot

set -e

echo "🚀 RunPod Boot - Initializing StaticWaves Forge..."

# Wait for system to be ready
sleep 5

# Clone/update repository if needed
if [ ! -d "/workspace/staticwaves-forge" ]; then
    echo "📥 Cloning StaticWaves Forge repository..."
    cd /workspace
    git clone -b claude/ai-3d-asset-engine-Q6XOw \
        https://github.com/ssiens-oss/ssiens-oss-static_pod.git \
        staticwaves-forge
fi

# Run the unified startup script
if [ -f "/workspace/staticwaves-forge/staticwaves-forge/start-unified.sh" ]; then
    echo "▶️  Launching unified boot system..."
    bash /workspace/staticwaves-forge/staticwaves-forge/start-unified.sh start
else
    echo "❌ Startup script not found!"
    echo "Run: git pull to update the repository"
    exit 1
fi

echo "✅ StaticWaves Forge auto-start complete!"

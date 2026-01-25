#!/bin/bash
# Install Claude Code CLI on RunPod pod
# Usage: ./scripts/install-claude-code.sh [pod-id]
# Example: ./scripts/install-claude-code.sh p43f

set -e

POD_ID="${1:-p43f}"
RUNPOD_HOST="${POD_ID}@ssh.runpod.io"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519}"

echo "=============================================="
echo "  Installing Claude Code on RunPod Pod: $POD_ID"
echo "=============================================="
echo ""

# Check if we're running locally on the pod or remotely via SSH
if [ -z "$1" ] && [ -d "/workspace" ]; then
    echo "Running locally on RunPod pod..."
    LOCAL_MODE=true
else
    LOCAL_MODE=false
    echo "Target: $RUNPOD_HOST"
    echo "SSH Key: $SSH_KEY"
    echo ""
fi

# Installation commands to run on the pod
INSTALL_COMMANDS='
set -e
echo ">>> Checking Node.js version..."
node --version || { echo "Node.js not found, installing..."; apt-get update && apt-get install -y nodejs npm; }

echo ">>> Installing Claude Code CLI globally..."
npm install -g @anthropic-ai/claude-code

echo ">>> Verifying installation..."
which claude && claude --version

echo ""
echo "=============================================="
echo "  Claude Code installed successfully!"
echo "=============================================="
echo ""
echo "To use Claude Code, you need to authenticate:"
echo "  1. Run: claude"
echo "  2. Follow the authentication prompts"
echo ""
echo "Or set your API key:"
echo "  export ANTHROPIC_API_KEY=your-api-key"
echo "  claude"
echo ""
'

if [ "$LOCAL_MODE" = true ]; then
    # Run commands locally
    bash -c "$INSTALL_COMMANDS"
else
    # Check SSH key
    if [ ! -f "$SSH_KEY" ]; then
        echo "ERROR: SSH key not found at $SSH_KEY"
        echo ""
        echo "Alternative: Run this script directly on the pod via RunPod Web Terminal:"
        echo "  curl -sSL https://raw.githubusercontent.com/ssiens-oss/ssiens-oss-static_pod/main/scripts/install-claude-code.sh | bash"
        echo ""
        echo "Or manually install on the pod:"
        echo "  npm install -g @anthropic-ai/claude-code"
        exit 1
    fi

    # Check for SSH command
    if ! command -v ssh &> /dev/null; then
        echo "ERROR: SSH command not available"
        echo ""
        echo "Alternative: Run these commands directly on pod $POD_ID via RunPod Web Terminal:"
        echo ""
        echo "  npm install -g @anthropic-ai/claude-code"
        echo "  claude --version"
        echo ""
        exit 1
    fi

    # Run installation via SSH
    echo "Connecting to pod and installing..."
    ssh -T -i "$SSH_KEY" -o StrictHostKeyChecking=no "$RUNPOD_HOST" "$INSTALL_COMMANDS"
fi

echo "Done!"

#!/bin/bash
# Bootstrap script for new container sessions
# Run this once when starting a new RunPod container

echo "🚀 Bootstrapping POD Pipeline..."

# Navigate to repo
cd /home/user/ssiens-oss-static_pod || {
    echo "❌ Repository not found at /home/user/ssiens-oss-static_pod"
    exit 1
}

# Install pod command globally
ln -sf /home/user/ssiens-oss-static_pod/pod /usr/local/bin/pod
echo "✓ Installed 'pod' command"

# Start the pipeline
./run-pod-pipeline.sh

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Bootstrap Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "You can now use 'pod' from any directory:"
echo "  pod status    # Check pipeline"
echo "  pod stop      # Stop pipeline"
echo "  pod start     # Start pipeline"
echo "  pod logs      # View logs"
echo ""

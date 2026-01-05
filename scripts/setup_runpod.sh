#!/bin/bash
#
# Quick setup script to copy the Printify uploader to RunPod
#

RUNPOD_HOST="tleofuk3ify4lk-64410e97@ssh.runpod.io"
SSH_KEY="$HOME/.ssh/id_ed25519"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================"
echo "Setting up Printify Image Uploader on RunPod"
echo "================================================"

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "Error: SSH key not found at $SSH_KEY"
    exit 1
fi

# Copy script to RunPod
echo ""
echo "Copying script to RunPod..."
scp -i "$SSH_KEY" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$SCRIPT_DIR/runpod_push_to_printify.py" \
    "$RUNPOD_HOST:/workspace/"

if [ $? -eq 0 ]; then
    echo "✓ Script copied successfully"
else
    echo "✗ Failed to copy script"
    exit 1
fi

# Make it executable
echo ""
echo "Making script executable..."
ssh -i "$SSH_KEY" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$RUNPOD_HOST" \
    "chmod +x /workspace/runpod_push_to_printify.py"

echo ""
echo "================================================"
echo "Setup complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. SSH into RunPod:"
echo "   ssh $RUNPOD_HOST -i $SSH_KEY"
echo ""
echo "2. Set your Printify credentials:"
echo "   export PRINTIFY_API_KEY='your-api-key'"
echo "   export PRINTIFY_SHOP_ID='your-shop-id'"
echo ""
echo "3. Install requests if needed:"
echo "   pip install requests"
echo ""
echo "4. Run the script:"
echo "   cd /workspace"
echo "   ./runpod_push_to_printify.py"
echo ""

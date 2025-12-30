#!/bin/bash
# One-time download of all images from RunPod
# Run this on YOUR LOCAL MACHINE

# Configuration
RUNPOD_SSH_HOST="${RUNPOD_SSH_HOST:-}"
RUNPOD_SSH_KEY="${RUNPOD_SSH_KEY:-$HOME/.ssh/id_ed25519}"
REMOTE_PATH="${REMOTE_PATH:-/data/designs}"
LOCAL_PATH="${LOCAL_PATH:-$HOME/POD-Designs}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}POD Studio - Image Downloader${NC}"
echo ""

# Check if RunPod SSH host is set
if [ -z "$RUNPOD_SSH_HOST" ]; then
    echo -e "${YELLOW}Enter your RunPod SSH connection:${NC}"
    echo "Example: nfre49elqpt6su-64d11157@ssh.runpod.io"
    read -p "RunPod SSH: " ssh_host
    export RUNPOD_SSH_HOST="$ssh_host"
fi

# Create local directory
mkdir -p "$LOCAL_PATH"

echo -e "${GREEN}Downloading images...${NC}"
echo -e "From: ${BLUE}$RUNPOD_SSH_HOST:$REMOTE_PATH${NC}"
echo -e "To:   ${BLUE}$LOCAL_PATH${NC}"
echo ""

# Download using rsync
rsync -avz --progress \
    -e "ssh -i $RUNPOD_SSH_KEY -o StrictHostKeyChecking=no" \
    "$RUNPOD_SSH_HOST:$REMOTE_PATH/" \
    "$LOCAL_PATH/"

if [ $? -eq 0 ]; then
    # Count files
    file_count=$(find "$LOCAL_PATH" -type f | wc -l)
    echo ""
    echo -e "${GREEN}✓ Download complete!${NC}"
    echo -e "Total files: ${BLUE}$file_count${NC}"
    echo -e "Location: ${BLUE}$LOCAL_PATH${NC}"
else
    echo ""
    echo -e "${RED}✗ Download failed${NC}"
    exit 1
fi

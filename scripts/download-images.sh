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

# Download using tar over SSH (most reliable with RunPod)
echo -e "${YELLOW}Downloading via tar stream (this works around RunPod limitations)...${NC}"
echo -e "${YELLOW}This may take a few minutes for 301 files (~540MB)...${NC}"
echo ""

# Use uncompressed tar over SSH (gzip can be confused by RunPod banner)
# Redirect stderr to filter out RunPod banner messages
ssh -i "$RUNPOD_SSH_KEY" -o StrictHostKeyChecking=no -o LogLevel=ERROR "$RUNPOD_SSH_HOST" \
    "cd $REMOTE_PATH 2>/dev/null && tar cf - *.png 2>/dev/null" 2>/dev/null | \
    tar xf - -C "$LOCAL_PATH/" 2>&1 | grep -v "RUNPOD" | grep -v "Enjoy"

if [ ${PIPESTATUS[1]} -eq 0 ]; then
    # Count files
    file_count=$(find "$LOCAL_PATH" -type f -name "*.png" | wc -l)
    total_size=$(du -sh "$LOCAL_PATH" | cut -f1)
    echo ""
    echo -e "${GREEN}✓ Download complete!${NC}"
    echo -e "Total files: ${BLUE}$file_count PNG images${NC}"
    echo -e "Total size:  ${BLUE}$total_size${NC}"
    echo -e "Location:    ${BLUE}$LOCAL_PATH${NC}"
else
    echo ""
    echo -e "${RED}✗ Download failed${NC}"
    echo -e "${YELLOW}Trying alternative method...${NC}"

    # Fallback: Download files one by one using a loop over SSH
    echo -e "${YELLOW}Downloading files individually (slower but more reliable)...${NC}"
    ssh -i "$RUNPOD_SSH_KEY" -o StrictHostKeyChecking=no "$RUNPOD_SSH_HOST" \
        "cd $REMOTE_PATH && ls *.png" 2>/dev/null | while read filename; do
        if [ ! -z "$filename" ]; then
            ssh -i "$RUNPOD_SSH_KEY" -o StrictHostKeyChecking=no "$RUNPOD_SSH_HOST" \
                "cat $REMOTE_PATH/$filename" > "$LOCAL_PATH/$filename" 2>/dev/null
            echo -n "."
        fi
    done

    echo ""
    file_count=$(find "$LOCAL_PATH" -type f -name "*.png" | wc -l)
    echo -e "${GREEN}✓ Downloaded $file_count files${NC}"
fi

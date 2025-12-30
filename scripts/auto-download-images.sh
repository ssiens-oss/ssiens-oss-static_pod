#!/bin/bash
# Auto-download images from RunPod to local machine
# This script runs on YOUR LOCAL MACHINE and syncs images from the pod

# Configuration
RUNPOD_SSH_HOST="${RUNPOD_SSH_HOST:-}"  # e.g., nfre49elqpt6su-64d11157@ssh.runpod.io
RUNPOD_SSH_KEY="${RUNPOD_SSH_KEY:-$HOME/.ssh/id_ed25519}"
REMOTE_PATH="${REMOTE_PATH:-/data/designs}"
LOCAL_PATH="${LOCAL_PATH:-$HOME/POD-Designs}"
SYNC_INTERVAL="${SYNC_INTERVAL:-60}"  # seconds between syncs

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  POD Studio - Auto Image Downloader              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if RunPod SSH host is set
if [ -z "$RUNPOD_SSH_HOST" ]; then
    echo -e "${YELLOW}⚠ RUNPOD_SSH_HOST not set!${NC}"
    echo ""
    echo "Please set your RunPod SSH connection:"
    echo ""
    read -p "Enter your RunPod SSH (e.g., podid-xxx@ssh.runpod.io): " ssh_host
    export RUNPOD_SSH_HOST="$ssh_host"
fi

# Create local directory if it doesn't exist
mkdir -p "$LOCAL_PATH"

echo -e "${GREEN}✓ Configuration:${NC}"
echo -e "  Remote: ${BLUE}$RUNPOD_SSH_HOST:$REMOTE_PATH${NC}"
echo -e "  Local:  ${BLUE}$LOCAL_PATH${NC}"
echo -e "  Sync:   ${BLUE}Every $SYNC_INTERVAL seconds${NC}"
echo ""

# Test SSH connection
echo -e "${YELLOW}Testing SSH connection...${NC}"
if ssh -i "$RUNPOD_SSH_KEY" -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$RUNPOD_SSH_HOST" "echo 'Connection successful'" &>/dev/null; then
    echo -e "${GREEN}✓ SSH connection successful${NC}"
else
    echo -e "${RED}✗ SSH connection failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Make sure your RunPod is running"
    echo "2. Check your SSH key: $RUNPOD_SSH_KEY"
    echo "3. Verify RunPod SSH host: $RUNPOD_SSH_HOST"
    exit 1
fi

echo ""
echo -e "${GREEN}🚀 Starting auto-sync... (Press Ctrl+C to stop)${NC}"
echo ""

# Counter for new files
total_downloaded=0

# Sync loop
while true; do
    # Get current timestamp
    timestamp=$(date "+%Y-%m-%d %H:%M:%S")

    # Create temp file to track new downloads
    temp_before="/tmp/pod_images_before_$$"
    temp_after="/tmp/pod_images_after_$$"

    # List local files before sync
    find "$LOCAL_PATH" -type f 2>/dev/null | sort > "$temp_before"

    # Perform sync using SCP (works better with RunPod)
    echo -e "${BLUE}[$timestamp]${NC} Syncing..."

    scp -i "$RUNPOD_SSH_KEY" -o StrictHostKeyChecking=no -o LogLevel=QUIET -r \
        "$RUNPOD_SSH_HOST:$REMOTE_PATH/*" \
        "$LOCAL_PATH/" 2>&1 | grep -v "RUNPOD.IO" | grep -v "Enjoy your Pod" > /dev/null

    rsync_exit=${PIPESTATUS[0]}

    if [ $rsync_exit -eq 0 ]; then
        # List local files after sync
        find "$LOCAL_PATH" -type f 2>/dev/null | sort > "$temp_after"

        # Count new files
        new_files=$(comm -13 "$temp_before" "$temp_after" | wc -l)

        if [ "$new_files" -gt 0 ]; then
            total_downloaded=$((total_downloaded + new_files))
            echo -e "${GREEN}✓ Downloaded $new_files new image(s)${NC} [Total: $total_downloaded]"

            # Show new files
            comm -13 "$temp_before" "$temp_after" | while read -r file; do
                filename=$(basename "$file")
                echo -e "  ${BLUE}→${NC} $filename"
            done
        else
            echo -e "${YELLOW}○ No new images${NC}"
        fi
    else
        echo -e "${RED}✗ Sync failed (exit code: $rsync_exit)${NC}"
    fi

    # Clean up temp files
    rm -f "$temp_before" "$temp_after"

    # Wait before next sync
    sleep "$SYNC_INTERVAL"
done

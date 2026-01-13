#!/bin/bash
# Download images from RunPod ComfyUI to local POD Gateway
# Usage: ./download-runpod-images.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
RUNPOD_POD_ID="${RUNPOD_POD_ID:-}"
RUNPOD_SSH_KEY="${RUNPOD_SSH_KEY:-$HOME/.ssh/id_rsa}"
RUNPOD_HOST="${RUNPOD_HOST:-}"
RUNPOD_PORT="${RUNPOD_PORT:-22}"
RUNPOD_USER="${RUNPOD_USER:-root}"
REMOTE_COMFY_DIR="${REMOTE_COMFY_DIR:-/workspace/ComfyUI/output}"
LOCAL_IMAGE_DIR="${LOCAL_IMAGE_DIR:-/opt/pod-gateway/data/images}"

# Functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

check_config() {
    if [ -z "$RUNPOD_HOST" ]; then
        log_error "RUNPOD_HOST not set"
        echo ""
        echo "Usage:"
        echo "  export RUNPOD_HOST='pod-id-ssh.runpod.io'"
        echo "  export RUNPOD_PORT='12345'"
        echo "  ./download-runpod-images.sh"
        echo ""
        echo "Or edit this script and set the variables at the top"
        exit 1
    fi

    if [ ! -f "$RUNPOD_SSH_KEY" ]; then
        log_error "SSH key not found: $RUNPOD_SSH_KEY"
        exit 1
    fi
}

test_connection() {
    log_info "Testing connection to RunPod..."

    if ssh -i "$RUNPOD_SSH_KEY" -p "$RUNPOD_PORT" -o ConnectTimeout=10 -o StrictHostKeyChecking=no \
        "$RUNPOD_USER@$RUNPOD_HOST" "echo 'Connected'" &>/dev/null; then
        log_success "Connection successful"
        return 0
    else
        log_error "Cannot connect to RunPod"
        log_info "Check your RUNPOD_HOST, RUNPOD_PORT, and SSH key"
        exit 1
    fi
}

check_remote_directory() {
    log_info "Checking remote ComfyUI output directory..."

    if ssh -i "$RUNPOD_SSH_KEY" -p "$RUNPOD_PORT" -o StrictHostKeyChecking=no \
        "$RUNPOD_USER@$RUNPOD_HOST" "[ -d '$REMOTE_COMFY_DIR' ]" &>/dev/null; then
        log_success "Remote directory exists: $REMOTE_COMFY_DIR"
        return 0
    else
        log_error "Remote directory not found: $REMOTE_COMFY_DIR"
        exit 1
    fi
}

count_remote_images() {
    local count=$(ssh -i "$RUNPOD_SSH_KEY" -p "$RUNPOD_PORT" -o StrictHostKeyChecking=no \
        "$RUNPOD_USER@$RUNPOD_HOST" \
        "find '$REMOTE_COMFY_DIR' -maxdepth 1 -type f \( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' \) | wc -l" 2>/dev/null)
    echo "$count"
}

download_images() {
    log_info "Downloading images from RunPod..."

    local count=$(count_remote_images)

    if [ "$count" -eq 0 ]; then
        log_warning "No images found on RunPod"
        return 0
    fi

    log_info "Found $count images on RunPod"

    # Create local directory if it doesn't exist
    sudo mkdir -p "$LOCAL_IMAGE_DIR"

    # Use rsync to download only new/changed files
    if command -v rsync &>/dev/null; then
        log_info "Using rsync for efficient transfer..."
        rsync -avz --progress \
            -e "ssh -i $RUNPOD_SSH_KEY -p $RUNPOD_PORT -o StrictHostKeyChecking=no" \
            --include='*.png' --include='*.jpg' --include='*.jpeg' \
            --exclude='*' \
            "$RUNPOD_USER@$RUNPOD_HOST:$REMOTE_COMFY_DIR/" \
            "$LOCAL_IMAGE_DIR/" 2>/dev/null || {
            log_error "Rsync failed, trying scp..."
            download_with_scp
        }
    else
        download_with_scp
    fi

    # Fix permissions
    sudo chown -R root:root "$LOCAL_IMAGE_DIR"
    sudo chmod 644 "$LOCAL_IMAGE_DIR"/*.{png,jpg,jpeg} 2>/dev/null || true

    local downloaded=$(ls -1 "$LOCAL_IMAGE_DIR"/*.{png,jpg,jpeg} 2>/dev/null | wc -l)
    log_success "Downloaded $downloaded images to $LOCAL_IMAGE_DIR"
}

download_with_scp() {
    log_info "Using scp for transfer..."

    # Get list of files
    local files=$(ssh -i "$RUNPOD_SSH_KEY" -p "$RUNPOD_PORT" -o StrictHostKeyChecking=no \
        "$RUNPOD_USER@$RUNPOD_HOST" \
        "find '$REMOTE_COMFY_DIR' -maxdepth 1 -type f \( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' \)")

    if [ -z "$files" ]; then
        log_warning "No image files to download"
        return 0
    fi

    # Download each file
    while IFS= read -r file; do
        local basename=$(basename "$file")
        if [ ! -f "$LOCAL_IMAGE_DIR/$basename" ]; then
            log_info "Downloading: $basename"
            scp -i "$RUNPOD_SSH_KEY" -P "$RUNPOD_PORT" -o StrictHostKeyChecking=no \
                "$RUNPOD_USER@$RUNPOD_HOST:$file" \
                "$LOCAL_IMAGE_DIR/" 2>/dev/null || {
                log_warning "Failed to download: $basename"
            }
        fi
    done <<< "$files"
}

delete_remote_images() {
    if [ "$DELETE_AFTER_DOWNLOAD" = "true" ]; then
        log_warning "Deleting remote images..."
        ssh -i "$RUNPOD_SSH_KEY" -p "$RUNPOD_PORT" -o StrictHostKeyChecking=no \
            "$RUNPOD_USER@$RUNPOD_HOST" \
            "rm -f '$REMOTE_COMFY_DIR'/*.{png,jpg,jpeg}" 2>/dev/null || true
        log_success "Remote images deleted"
    fi
}

show_summary() {
    echo ""
    echo "=============================================="
    echo "Download Summary"
    echo "=============================================="
    echo "Remote host:      $RUNPOD_HOST:$RUNPOD_PORT"
    echo "Remote directory: $REMOTE_COMFY_DIR"
    echo "Local directory:  $LOCAL_IMAGE_DIR"
    echo ""
    echo "Local images:     $(ls -1 "$LOCAL_IMAGE_DIR"/*.{png,jpg,jpeg} 2>/dev/null | wc -l)"
    echo ""
    echo "View in POD Gateway: http://localhost:5000"
    echo "=============================================="
}

# Main
main() {
    echo ""
    echo "╔══════════════════════════════════════════╗"
    echo "║  RunPod ComfyUI Image Downloader         ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""

    check_config
    test_connection
    check_remote_directory
    download_images
    delete_remote_images
    show_summary
}

# Run
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

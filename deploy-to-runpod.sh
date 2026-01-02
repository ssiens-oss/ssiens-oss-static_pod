#!/bin/bash
# Local script to deploy to RunPod via SSH
# Run this from your LOCAL machine, not on RunPod

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 StaticWaves POD Studio - RunPod Deployment${NC}"
echo "=============================================="
echo ""

# Configuration
RUNPOD_USER="${RUNPOD_USER:-root}"
RUNPOD_HOST="${RUNPOD_HOST:-}"
RUNPOD_KEY="${RUNPOD_KEY:-$HOME/.ssh/id_ed25519}"
REPO_URL="${REPO_URL:-}"
BRANCH="${BRANCH:-claude/repo-analysis-g6UHk}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            RUNPOD_HOST="$2"
            shift 2
            ;;
        --user)
            RUNPOD_USER="$2"
            shift 2
            ;;
        --key)
            RUNPOD_KEY="$2"
            shift 2
            ;;
        --repo)
            REPO_URL="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --host HOST      RunPod SSH host (e.g., nfre49elqpt6su-64411157@ssh.runpod.io)"
            echo "  --user USER      SSH user (default: root)"
            echo "  --key PATH       SSH key path (default: ~/.ssh/id_ed25519)"
            echo "  --repo URL       Git repository URL"
            echo "  --branch BRANCH  Git branch (default: claude/repo-analysis-g6UHk)"
            echo "  --help           Show this help"
            echo ""
            echo "Example:"
            echo "  $0 --host nfre49elqpt6su-64411157@ssh.runpod.io"
            echo ""
            echo "Or set environment variables:"
            echo "  export RUNPOD_HOST=nfre49elqpt6su-64411157@ssh.runpod.io"
            echo "  $0"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Run with --help for usage"
            exit 1
            ;;
    esac
done

# Validate inputs
if [ -z "$RUNPOD_HOST" ]; then
    echo -e "${YELLOW}⚠${NC} RunPod host not specified"
    echo ""
    read -p "Enter RunPod SSH host (e.g., nfre49elqpt6su-64411157@ssh.runpod.io): " RUNPOD_HOST
fi

if [ -z "$RUNPOD_HOST" ]; then
    echo "Error: RunPod host is required"
    exit 1
fi

if [ ! -f "$RUNPOD_KEY" ]; then
    echo -e "${YELLOW}⚠${NC} SSH key not found at $RUNPOD_KEY"
    read -p "Enter SSH key path: " RUNPOD_KEY
fi

if [ ! -f "$RUNPOD_KEY" ]; then
    echo "Error: SSH key not found at $RUNPOD_KEY"
    exit 1
fi

echo -e "${GREEN}✓${NC} Configuration:"
echo "  Host: $RUNPOD_HOST"
echo "  User: $RUNPOD_USER"
echo "  Key:  $RUNPOD_KEY"
echo "  Branch: $BRANCH"
echo ""

# Test SSH connection
echo -e "${BLUE}ℹ${NC} Testing SSH connection..."
if ssh -i "$RUNPOD_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$RUNPOD_HOST" "echo 'Connection successful'" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} SSH connection successful"
else
    echo -e "${YELLOW}⚠${NC} SSH connection failed"
    echo "Please check your credentials and try again"
    exit 1
fi

echo ""
echo -e "${BLUE}ℹ${NC} Deploying to RunPod..."
echo ""

# Create deployment script
DEPLOY_SCRIPT=$(cat <<'SCRIPT_END'
#!/bin/bash
set -e

echo "📦 Cloning/updating repository..."
cd ~

if [ -d ssiens-oss-static_pod ]; then
    echo "Repository exists, updating..."
    cd ssiens-oss-static_pod
    git fetch origin
    git checkout BRANCH_PLACEHOLDER
    git pull origin BRANCH_PLACEHOLDER
else
    echo "Cloning repository..."
    if [ -n "REPO_URL_PLACEHOLDER" ]; then
        git clone REPO_URL_PLACEHOLDER ssiens-oss-static_pod
        cd ssiens-oss-static_pod
        git checkout BRANCH_PLACEHOLDER
    else
        echo "Error: Repository URL not provided"
        echo "Please clone manually or provide --repo argument"
        exit 1
    fi
fi

echo ""
echo "🚀 Running complete setup script..."
bash setup-runpod-complete.sh

SCRIPT_END
)

# Replace placeholders
DEPLOY_SCRIPT="${DEPLOY_SCRIPT//BRANCH_PLACEHOLDER/$BRANCH}"
DEPLOY_SCRIPT="${DEPLOY_SCRIPT//REPO_URL_PLACEHOLDER/$REPO_URL}"

# Execute deployment
ssh -i "$RUNPOD_KEY" -o StrictHostKeyChecking=no "$RUNPOD_HOST" "bash -s" <<< "$DEPLOY_SCRIPT"

echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""

# Extract RunPod ID from host
RUNPOD_ID=$(echo "$RUNPOD_HOST" | cut -d'-' -f1 | cut -d'@' -f2)

echo "🌐 Access your POD Studio:"
echo "  Dashboard: https://${RUNPOD_ID}-3001.proxy.runpod.net"
echo ""
echo "📝 SSH into RunPod:"
echo "  ssh -i $RUNPOD_KEY $RUNPOD_HOST"
echo ""
echo "Ready to create POD products! 🚀"

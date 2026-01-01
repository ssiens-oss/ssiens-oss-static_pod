#!/bin/bash
set -e

echo "🚀 StaticWaves POD Studio - RunPod Bootstrap"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Check Node.js version
echo "📦 Checking Node.js version..."
NODE_VERSION=$(node -v 2>/dev/null || echo "none")
if [[ "$NODE_VERSION" == "none" ]] || [[ ! "$NODE_VERSION" =~ ^v2[0-9] ]]; then
    print_warning "Node.js 20+ not found. Installing..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    print_status "Node.js installed: $(node -v)"
else
    print_status "Node.js version: $NODE_VERSION"
fi

# 2. Check for required tools
echo ""
echo "🔧 Checking required tools..."
MISSING_TOOLS=""

command -v git >/dev/null 2>&1 || MISSING_TOOLS="$MISSING_TOOLS git"
command -v curl >/dev/null 2>&1 || MISSING_TOOLS="$MISSING_TOOLS curl"
command -v npm >/dev/null 2>&1 || MISSING_TOOLS="$MISSING_TOOLS npm"
command -v pm2 >/dev/null 2>&1 || MISSING_TOOLS="$MISSING_TOOLS pm2"

if [ ! -z "$MISSING_TOOLS" ]; then
    print_warning "Installing missing tools:$MISSING_TOOLS"
    apt-get update -qq
    [ -z "${MISSING_TOOLS##*git*}" ] && apt-get install -y git
    [ -z "${MISSING_TOOLS##*curl*}" ] && apt-get install -y curl
    [ -z "${MISSING_TOOLS##*npm*}" ] && apt-get install -y npm
    [ -z "${MISSING_TOOLS##*pm2*}" ] && npm install -g pm2
fi
print_status "All required tools installed"

# 3. Navigate to project directory
echo ""
echo "📁 Setting up project directory..."
cd ~/ssiens-oss-static_pod || {
    print_error "Project directory not found. Cloning repository..."
    cd ~
    git clone <repository-url> ssiens-oss-static_pod
    cd ssiens-oss-static_pod
}
print_status "In project directory: $(pwd)"

# 4. Pull latest code
echo ""
echo "📥 Pulling latest code..."
git fetch origin claude/repo-analysis-g6UHk
git checkout claude/repo-analysis-g6UHk
git pull origin claude/repo-analysis-g6UHk
print_status "Code updated to latest version"

# 5. Check .env file
echo ""
echo "🔐 Checking environment configuration..."
if [ ! -f .env ]; then
    print_error ".env file not found!"
    echo "Please create a .env file with the following variables:"
    echo "  ANTHROPIC_API_KEY=your_key"
    echo "  PRINTIFY_API_KEY=your_key"
    echo "  PRINTIFY_SHOP_ID=your_shop_id"
    echo "  SHOPIFY_STORE_URL=your_store.myshopify.com"
    echo "  SHOPIFY_ACCESS_TOKEN=your_token"
    exit 1
else
    print_status ".env file found"

    # Check for required variables
    source .env
    [ -z "$ANTHROPIC_API_KEY" ] && print_warning "ANTHROPIC_API_KEY not set"
    [ -z "$PRINTIFY_API_KEY" ] && print_warning "PRINTIFY_API_KEY not set"
    [ -n "$ANTHROPIC_API_KEY" ] && print_status "Claude API configured"
    [ -n "$PRINTIFY_API_KEY" ] && print_status "Printify API configured"
fi

# 6. Install dependencies
echo ""
echo "📦 Installing npm dependencies..."
npm install --quiet
print_status "Dependencies installed"

# 7. Build frontend
echo ""
echo "🏗️  Building frontend..."
npm run build
print_status "Frontend built successfully"

# 8. Stop any existing processes
echo ""
echo "🛑 Stopping existing processes..."
pm2 delete all 2>/dev/null || true
pkill -f "node.*server" 2>/dev/null || true
pkill -f "tsx.*server" 2>/dev/null || true
sleep 2
print_status "Cleaned up existing processes"

# 9. Start the server
echo ""
echo "🚀 Starting POD Studio API Server..."
pm2 start "npm run dev:server" --name pod-studio-api
pm2 save
print_status "API Server started on port 3001"

# 10. Wait for server to be ready
echo ""
echo "⏳ Waiting for server to be ready..."
sleep 3

# Test the server
MAX_RETRIES=10
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:3001/health > /dev/null; then
        print_status "Server is ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Attempt $RETRY_COUNT/$MAX_RETRIES..."
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_error "Server failed to start"
    echo ""
    echo "Logs:"
    pm2 logs pod-studio-api --lines 20 --nostream
    exit 1
fi

# 11. Run health checks
echo ""
echo "🏥 Running health checks..."
HEALTH=$(curl -s http://localhost:3001/health)
echo "$HEALTH" | grep -q '"status":"ok"' && print_status "Health check passed"

CONFIG_TEST=$(curl -s http://localhost:3001/api/config/test)
echo "$CONFIG_TEST" | grep -q '"claude":true' && print_status "Claude API: Connected"
echo "$CONFIG_TEST" | grep -q '"printify":true' && print_status "Printify API: Connected"
echo "$CONFIG_TEST" | grep -q '"shopify":true' && print_status "Shopify API: Connected" || print_warning "Shopify API: Not connected"
echo "$CONFIG_TEST" | grep -q '"comfyui":true' && print_status "ComfyUI: Connected" || print_warning "ComfyUI: Not available (using placeholders)"

# 12. Display access information
echo ""
echo "=============================================="
echo -e "${GREEN}🎉 POD Studio is ready!${NC}"
echo "=============================================="
echo ""
echo "📊 Server Status:"
pm2 list
echo ""
echo "🌐 Access URLs:"
echo "   Dashboard:  https://$(hostname | cut -d'-' -f1)-3001.proxy.runpod.net"
echo "   API Health: https://$(hostname | cut -d'-' -f1)-3001.proxy.runpod.net/health"
echo "   Local API:  http://localhost:3001"
echo ""
echo "📝 Useful Commands:"
echo "   View logs:    pm2 logs pod-studio-api"
echo "   Restart:      pm2 restart pod-studio-api"
echo "   Stop:         pm2 stop pod-studio-api"
echo "   Test API:     curl http://localhost:3001/health"
echo ""
echo "🧪 Test Production Run:"
echo "   npx tsx test-printify.ts"
echo ""
echo "Ready to create POD products! 🚀"

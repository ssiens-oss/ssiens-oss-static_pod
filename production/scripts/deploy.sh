#!/bin/bash

# Production POD Engine Deployment Script
# Sets up and configures the production environment

set -e

echo "=================================="
echo "Production POD Engine Deployment"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Check prerequisites
log_info "Checking prerequisites..."

if ! command_exists node; then
    log_error "Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    log_error "Node.js version 18 or higher is required. Current version: $(node -v)"
    exit 1
fi
log_success "Node.js $(node -v) found"

if ! command_exists npm; then
    log_error "npm is not installed"
    exit 1
fi
log_success "npm $(npm -v) found"

# Step 2: Install dependencies
log_info "Installing dependencies..."
npm install
log_success "Dependencies installed"

# Step 3: Setup configuration
log_info "Setting up configuration..."

if [ ! -f "production/.env" ]; then
    if [ -f "production/.env.example" ]; then
        cp production/.env.example production/.env
        log_warning "Created production/.env from template"
        log_warning "Please edit production/.env with your API keys and settings"
    else
        log_error "production/.env.example not found"
        exit 1
    fi
else
    log_success "production/.env already exists"
fi

if [ ! -f "production/config.json" ]; then
    if [ -f "production/config.example.json" ]; then
        cp production/config.example.json production/config.json
        log_warning "Created production/config.json from template"
        log_warning "Please edit production/config.json with your settings"
    else
        log_error "production/config.example.json not found"
        exit 1
    fi
else
    log_success "production/config.json already exists"
fi

# Step 4: Check required environment variables
log_info "Checking environment variables..."

if [ -f "production/.env" ]; then
    source production/.env

    if [ -z "$CLAUDE_API_KEY" ] || [ "$CLAUDE_API_KEY" = "sk-ant-your-api-key-here" ]; then
        log_error "CLAUDE_API_KEY not set in production/.env"
        log_error "Please set your Claude API key before deployment"
        exit 1
    fi
    log_success "CLAUDE_API_KEY is set"

    if [ -z "$COMFYUI_API_URL" ]; then
        log_warning "COMFYUI_API_URL not set, using default: http://127.0.0.1:8188"
    else
        log_success "COMFYUI_API_URL is set: $COMFYUI_API_URL"
    fi
fi

# Step 5: Create required directories
log_info "Creating required directories..."

mkdir -p storage
mkdir -p comfyui_output
mkdir -p logs

log_success "Directories created"

# Step 6: Check database (optional)
if [ "$DATABASE_TYPE" = "postgres" ]; then
    log_info "PostgreSQL mode detected"

    if command_exists psql; then
        log_success "PostgreSQL client found"
        log_info "To initialize database, run: psql -U <user> -d <database> -f production/schema.sql"
    else
        log_warning "PostgreSQL client not found. Install it to use PostgreSQL"
        log_warning "Falling back to in-memory mode"
    fi
else
    log_info "Using in-memory database (development mode)"
fi

# Step 7: Check ComfyUI
log_info "Checking ComfyUI availability..."

COMFYUI_URL="${COMFYUI_API_URL:-http://127.0.0.1:8188}"

if curl -f -s "$COMFYUI_URL/system_stats" > /dev/null 2>&1; then
    log_success "ComfyUI is running at $COMFYUI_URL"
else
    log_warning "ComfyUI is not reachable at $COMFYUI_URL"
    log_warning "Make sure ComfyUI is running before starting the engine"
fi

# Step 8: Build TypeScript (if needed)
if [ -f "tsconfig.json" ]; then
    log_info "Building TypeScript..."
    npm run build 2>/dev/null || log_warning "Build failed or no build script"
fi

# Step 9: Summary
echo ""
echo "=================================="
log_success "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Edit production/.env with your API keys"
echo "  2. Edit production/config.json with your settings"
echo "  3. Ensure ComfyUI is running"
echo "  4. Start the engine:"
echo ""
echo "     Development (single worker):"
echo "     $ npm run production:worker"
echo ""
echo "     Production (worker pool with API):"
echo "     $ npm run production:api"
echo ""
echo "     Docker:"
echo "     $ cd production && docker-compose up -d"
echo ""
echo "  5. Check status:"
echo "     $ curl http://localhost:3000/health"
echo ""

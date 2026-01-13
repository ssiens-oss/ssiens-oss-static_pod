#!/bin/bash

# Production POD Engine Environment Validation

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

ERRORS=0
WARNINGS=0

echo "=================================="
echo "Environment Validation"
echo "=================================="
echo ""

# Check Node.js
log_info "Checking Node.js..."
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node -v)
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'v' -f2 | cut -d'.' -f1)

    if [ "$NODE_MAJOR" -ge 18 ]; then
        log_success "Node.js $NODE_VERSION (OK)"
    else
        log_error "Node.js $NODE_VERSION (Need v18 or higher)"
        ERRORS=$((ERRORS + 1))
    fi
else
    log_error "Node.js not found"
    ERRORS=$((ERRORS + 1))
fi

# Check npm
log_info "Checking npm..."
if command -v npm >/dev/null 2>&1; then
    NPM_VERSION=$(npm -v)
    log_success "npm $NPM_VERSION"
else
    log_error "npm not found"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# Check configuration files
log_info "Checking configuration files..."

if [ -f "production/.env" ]; then
    log_success "production/.env exists"

    # Load and validate
    source production/.env

    # Check required variables
    if [ -z "$CLAUDE_API_KEY" ] || [ "$CLAUDE_API_KEY" = "sk-ant-your-api-key-here" ]; then
        log_error "CLAUDE_API_KEY not configured"
        ERRORS=$((ERRORS + 1))
    else
        log_success "CLAUDE_API_KEY is set"
    fi

    if [ -z "$COMFYUI_API_URL" ]; then
        log_warning "COMFYUI_API_URL not set (will use default)"
        WARNINGS=$((WARNINGS + 1))
    else
        log_success "COMFYUI_API_URL: $COMFYUI_API_URL"
    fi
else
    log_error "production/.env not found"
    log_error "Run: cp production/.env.example production/.env"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "production/config.json" ]; then
    log_success "production/config.json exists"

    # Validate JSON
    if command -v jq >/dev/null 2>&1; then
        if jq empty production/config.json 2>/dev/null; then
            log_success "config.json is valid JSON"
        else
            log_error "config.json is invalid JSON"
            ERRORS=$((ERRORS + 1))
        fi
    fi
else
    log_error "production/config.json not found"
    log_error "Run: cp production/config.example.json production/config.json"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# Check directories
log_info "Checking directories..."

for DIR in storage comfyui_output logs; do
    if [ -d "$DIR" ]; then
        log_success "$DIR/ exists"
    else
        log_warning "$DIR/ does not exist (will be created)"
        WARNINGS=$((WARNINGS + 1))
    fi
done

echo ""

# Check dependencies
log_info "Checking Node.js dependencies..."

if [ -d "node_modules" ]; then
    log_success "node_modules/ exists"
else
    log_warning "node_modules/ not found"
    log_warning "Run: npm install"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# Check services
log_info "Checking external services..."

# ComfyUI
COMFYUI_URL=${COMFYUI_API_URL:-http://127.0.0.1:8188}
if curl -f -s -m 5 "$COMFYUI_URL/system_stats" > /dev/null 2>&1; then
    log_success "ComfyUI is reachable at $COMFYUI_URL"
else
    log_warning "ComfyUI is not reachable at $COMFYUI_URL"
    log_warning "Make sure ComfyUI is running before starting the engine"
    WARNINGS=$((WARNINGS + 1))
fi

# Database
if [ "$DATABASE_TYPE" = "postgres" ]; then
    if command -v psql >/dev/null 2>&1; then
        log_success "PostgreSQL client installed"

        if [ ! -z "$DATABASE_URL" ]; then
            if psql "$DATABASE_URL" -c "SELECT 1" >/dev/null 2>&1; then
                log_success "Database is accessible"
            else
                log_warning "Database is not accessible"
                WARNINGS=$((WARNINGS + 1))
            fi
        fi
    else
        log_warning "PostgreSQL client not installed"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    log_info "Using in-memory database (development mode)"
fi

echo ""

# Summary
echo "=================================="
echo "Validation Summary"
echo "=================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    log_success "All checks passed! Ready to deploy."
    echo ""
    echo "Start the engine:"
    echo "  npm run production:api"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    log_warning "$WARNINGS warning(s) found"
    echo ""
    echo "You can proceed, but some features may not work correctly."
    echo ""
    exit 0
else
    log_error "$ERRORS error(s) and $WARNINGS warning(s) found"
    echo ""
    echo "Please fix the errors before deploying."
    echo ""
    exit 1
fi

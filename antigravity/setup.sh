#!/bin/bash

# Antigravity POD Orchestration System - Setup Script

set -e  # Exit on error

echo "=========================================="
echo "  Antigravity Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python 3.10+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}! Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install requirements
echo ""
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}Error: requirements.txt not found${NC}"
    exit 1
fi

# Install Playwright browsers
echo ""
echo "Installing Playwright browsers..."
playwright install chromium
echo -e "${GREEN}✓ Playwright browsers installed${NC}"

# Check for .env file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env created${NC}"
        echo -e "${YELLOW}! Please edit .env and add your API keys${NC}"
    else
        echo -e "${RED}Error: .env.example not found${NC}"
    fi
else
    echo -e "${YELLOW}! .env already exists (not overwriting)${NC}"
fi

# Create necessary directories
echo ""
echo "Creating data directories..."
mkdir -p /tmp/antigravity/memory
mkdir -p /tmp/antigravity/screenshots
echo -e "${GREEN}✓ Directories created${NC}"

# Run a test
echo ""
echo "Running installation test..."
python3 -c "
from antigravity.types import SubTask, ModelResponse, Role
from antigravity.router import select_model
print('✓ Core modules loaded successfully')
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Installation test passed${NC}"
else
    echo -e "${RED}✗ Installation test failed${NC}"
    exit 1
fi

# Check for API keys
echo ""
echo "Checking configuration..."

if [ -f ".env" ]; then
    source .env

    MISSING_KEYS=()

    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-..." ]; then
        MISSING_KEYS+=("OPENAI_API_KEY")
    fi

    if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-..." ]; then
        MISSING_KEYS+=("ANTHROPIC_API_KEY")
    fi

    if [ ${#MISSING_KEYS[@]} -eq 0 ]; then
        echo -e "${GREEN}✓ Required API keys configured${NC}"
    else
        echo -e "${YELLOW}! Missing API keys:${NC}"
        for key in "${MISSING_KEYS[@]}"; do
            echo "  - $key"
        done
        echo -e "${YELLOW}! Add these to .env before running${NC}"
    fi

    # Check optional configs
    if [ -z "$SLACK_WEBHOOK_URL" ]; then
        echo -e "${YELLOW}! Optional: SLACK_WEBHOOK_URL not configured${NC}"
    fi
else
    echo -e "${RED}! .env file not found${NC}"
fi

# Print next steps
echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure API keys:"
echo "   nano .env"
echo ""
echo "2. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Test with a design:"
echo "   python -m antigravity.main design path/to/design.png --dry-run"
echo ""
echo "4. Start watching directory:"
echo "   python -m antigravity.main watch --watch-dir /data/comfyui/output"
echo ""
echo "5. Read the documentation:"
echo "   cat README.md"
echo ""
echo "=========================================="

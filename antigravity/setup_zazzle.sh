#!/bin/bash

# Zazzle API Setup Script
# This script helps you configure Zazzle integration for Antigravity POD

set -e  # Exit on error

echo "=========================================="
echo "  Zazzle API Setup"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}! No .env file found. Creating from template...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env created${NC}"
    else
        echo -e "${RED}✗ .env.example not found${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}Zazzle API Configuration Guide${NC}"
echo ""
echo "Zazzle offers two ways to integrate:"
echo ""
echo "1. ${GREEN}Associate Program${NC} (Recommended for starting)"
echo "   - Free to join"
echo "   - Earn commissions on sales"
echo "   - Limited API access"
echo "   - Best for: Getting started, testing"
echo ""
echo "2. ${GREEN}Zazzle API${NC} (Full access)"
echo "   - Requires application approval"
echo "   - Full product management"
echo "   - Direct store integration"
echo "   - Best for: Production, scale"
echo ""

# Function to get Zazzle Associate ID
setup_associate() {
    echo ""
    echo -e "${BLUE}Setting up Zazzle Associate Program${NC}"
    echo ""
    echo "Steps to get your Associate ID:"
    echo "1. Go to: https://www.zazzle.com/sell/associates"
    echo "2. Sign up for the Associate program (it's free)"
    echo "3. Once approved, find your Associate ID in your dashboard"
    echo "4. Your Associate ID looks like: '238123456789012345'"
    echo ""

    read -p "Do you have your Zazzle Associate ID? (y/n): " has_id

    if [ "$has_id" = "y" ] || [ "$has_id" = "Y" ]; then
        read -p "Enter your Zazzle Associate ID: " associate_id

        # Update .env
        if grep -q "^ZAZZLE_ASSOCIATE_ID=" .env; then
            sed -i "s/^ZAZZLE_ASSOCIATE_ID=.*/ZAZZLE_ASSOCIATE_ID=$associate_id/" .env
        else
            echo "ZAZZLE_ASSOCIATE_ID=$associate_id" >> .env
        fi

        echo -e "${GREEN}✓ Associate ID saved to .env${NC}"
    else
        echo -e "${YELLOW}! Please sign up at https://www.zazzle.com/sell/associates${NC}"
        echo -e "${YELLOW}! Then run this script again${NC}"
    fi
}

# Function to get Zazzle API Key
setup_api() {
    echo ""
    echo -e "${BLUE}Setting up Zazzle API${NC}"
    echo ""
    echo "Steps to get your API Key:"
    echo "1. Go to: https://www.zazzle.com/sell/developers"
    echo "2. Apply for API access"
    echo "3. Wait for approval (can take a few days)"
    echo "4. Once approved, generate your API key"
    echo ""

    read -p "Do you have your Zazzle API Key? (y/n): " has_key

    if [ "$has_key" = "y" ] || [ "$has_key" = "Y" ]; then
        read -p "Enter your Zazzle API Key: " api_key

        # Update .env
        if grep -q "^ZAZZLE_API_KEY=" .env; then
            sed -i "s/^ZAZZLE_API_KEY=.*/ZAZZLE_API_KEY=$api_key/" .env
        else
            echo "ZAZZLE_API_KEY=$api_key" >> .env
        fi

        echo -e "${GREEN}✓ API Key saved to .env${NC}"
    else
        echo -e "${YELLOW}! Please apply at https://www.zazzle.com/sell/developers${NC}"
        echo -e "${YELLOW}! Then run this script again${NC}"
    fi
}

# Function to get Store ID
setup_store() {
    echo ""
    echo -e "${BLUE}Setting up Zazzle Store ID${NC}"
    echo ""
    echo "Your Store ID is in your Zazzle store URL:"
    echo "Example: https://www.zazzle.com/store/your_store_name"
    echo "         Your Store ID is: 'your_store_name'"
    echo ""

    read -p "Enter your Zazzle Store ID: " store_id

    # Update .env
    if grep -q "^ZAZZLE_STORE_ID=" .env; then
        sed -i "s/^ZAZZLE_STORE_ID=.*/ZAZZLE_STORE_ID=$store_id/" .env
    else
        echo "ZAZZLE_STORE_ID=$store_id" >> .env
    fi

    echo -e "${GREEN}✓ Store ID saved to .env${NC}"
}

# Main setup flow
echo "Which setup method would you like to use?"
echo ""
echo "1) Associate Program (Quick start, recommended)"
echo "2) Full API (Production, requires approval)"
echo "3) Both (Most flexible)"
echo "4) Skip (I'll configure manually)"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        setup_associate
        setup_store
        ;;
    2)
        setup_api
        setup_store
        ;;
    3)
        setup_associate
        setup_api
        setup_store
        ;;
    4)
        echo -e "${YELLOW}! Manual configuration selected${NC}"
        echo "Edit .env and set:"
        echo "  - ZAZZLE_ASSOCIATE_ID (or ZAZZLE_API_KEY)"
        echo "  - ZAZZLE_STORE_ID"
        ;;
    *)
        echo -e "${RED}✗ Invalid choice${NC}"
        exit 1
        ;;
esac

# Set default template
echo ""
read -p "Set default product template (tshirt_basic/hoodie_basic/poster/mug) [tshirt_basic]: " template
template=${template:-tshirt_basic}

if grep -q "^ZAZZLE_DEFAULT_TEMPLATE=" .env; then
    sed -i "s/^ZAZZLE_DEFAULT_TEMPLATE=.*/ZAZZLE_DEFAULT_TEMPLATE=$template/" .env
else
    echo "ZAZZLE_DEFAULT_TEMPLATE=$template" >> .env
fi

echo -e "${GREEN}✓ Default template set to: $template${NC}"

# Enable Zazzle integration
if grep -q "^ENABLE_ZAZZLE=" .env; then
    sed -i "s/^ENABLE_ZAZZLE=.*/ENABLE_ZAZZLE=true/" .env
else
    echo "ENABLE_ZAZZLE=true" >> .env
fi

echo ""
echo -e "${GREEN}✓ Zazzle integration enabled${NC}"

# Validate configuration
echo ""
echo "=========================================="
echo "  Configuration Summary"
echo "=========================================="
echo ""

source .env 2>/dev/null || true

if [ -n "$ZAZZLE_ASSOCIATE_ID" ]; then
    echo -e "${GREEN}✓ Associate ID configured${NC}"
else
    echo -e "${YELLOW}! Associate ID not configured${NC}"
fi

if [ -n "$ZAZZLE_API_KEY" ]; then
    echo -e "${GREEN}✓ API Key configured${NC}"
else
    echo -e "${YELLOW}! API Key not configured${NC}"
fi

if [ -n "$ZAZZLE_STORE_ID" ]; then
    echo -e "${GREEN}✓ Store ID configured${NC}"
else
    echo -e "${YELLOW}! Store ID not configured${NC}"
fi

if [ -n "$ZAZZLE_DEFAULT_TEMPLATE" ]; then
    echo -e "${GREEN}✓ Default template: $ZAZZLE_DEFAULT_TEMPLATE${NC}"
fi

# Test connection
echo ""
echo "=========================================="
echo "  Testing Zazzle Connection"
echo "=========================================="
echo ""

if [ -n "$ZAZZLE_ASSOCIATE_ID" ] || [ -n "$ZAZZLE_API_KEY" ]; then
    echo "Running connection test..."
    echo ""

    # Run Python validation script
    if command -v python3 &> /dev/null; then
        python3 - <<'PYTHON'
import os
import sys
sys.path.insert(0, '/home/user/ssiens-oss-static_pod')

try:
    from antigravity.integrations.zazzle import ZazzleClient

    print("✓ Zazzle client module loaded")

    # Try to initialize client
    try:
        client = ZazzleClient()
        print("✓ Zazzle client initialized successfully")

        # Get store URL
        store_url = client.get_store_url()
        print(f"✓ Store URL: {store_url}")

        print("\n✅ Zazzle connection test PASSED")

    except ValueError as e:
        print(f"⚠️  Configuration incomplete: {e}")
        print("   This is OK if you're still setting up credentials")

except ImportError as e:
    print(f"✗ Failed to import Zazzle client: {e}")
    print("  Run: pip install -r requirements.txt")
    sys.exit(1)
PYTHON

        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}=========================================="
            echo "  Setup Complete!"
            echo "==========================================${NC}"
            echo ""
            echo "Next steps:"
            echo ""
            echo "1. View available templates:"
            echo "   python -m antigravity.zazzle_cli --help"
            echo ""
            echo "2. Test with a design (dry run):"
            echo "   python -m antigravity.zazzle_cli design design.png --dry-run"
            echo ""
            echo "3. Try the quick start examples:"
            echo "   python examples/zazzle_quickstart.py"
            echo ""
            echo "4. Read the documentation:"
            echo "   cat ZAZZLE_INTEGRATION.md"
            echo ""
        fi
    else
        echo -e "${RED}✗ Python 3 not found${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}! No credentials configured${NC}"
    echo "Configure at least one of:"
    echo "  - ZAZZLE_ASSOCIATE_ID"
    echo "  - ZAZZLE_API_KEY"
fi

echo ""
echo "Configuration saved to: .env"
echo ""

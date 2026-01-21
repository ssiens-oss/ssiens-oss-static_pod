#!/bin/bash
# POD Pipeline Configuration Setup
# Interactive script to configure RunPod, Printify, and Claude API credentials

set -e

echo "🔧 POD Pipeline - Configuration Setup"
echo "======================================"
echo ""
echo "This script will help you configure your POD pipeline credentials."
echo ""

# Navigate to project root
cd "$(dirname "$0")"

# Backup existing .env if it exists
if [ -f ".env" ]; then
    BACKUP_FILE=".env.backup.$(date +%Y%m%d-%H%M%S)"
    echo "📋 Backing up existing .env to $BACKUP_FILE"
    cp .env "$BACKUP_FILE"
    echo ""
fi

# Function to update or add env variable
update_env_var() {
    local key="$1"
    local value="$2"
    local file="${3:-.env}"

    if grep -q "^${key}=" "$file" 2>/dev/null; then
        # Update existing
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^${key}=.*|${key}=${value}|" "$file"
        else
            sed -i "s|^${key}=.*|${key}=${value}|" "$file"
        fi
    else
        # Add new
        echo "${key}=${value}" >> "$file"
    fi
}

# Check if .env exists, create from template if not
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        touch .env
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  RunPod Serverless Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "RunPod provides serverless ComfyUI for image generation."
echo "Get your credentials from: https://www.runpod.io/console"
echo ""

read -p "Do you want to configure RunPod? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📍 Step 1: Get your RunPod API Key"
    echo "   Visit: https://www.runpod.io/console/user/settings"
    echo "   Click 'API Keys' → 'Create API Key'"
    echo ""
    read -p "Enter your RunPod API Key: " RUNPOD_KEY

    echo ""
    echo "📍 Step 2: Get your RunPod Endpoint URL"
    echo "   Visit: https://www.runpod.io/console/serverless"
    echo "   Click on your ComfyUI endpoint"
    echo "   Copy the endpoint URL (should include /runsync or /run)"
    echo ""
    echo "   Example: https://api.runpod.ai/v2/qm6ofmy96f3htl/runsync"
    echo ""
    read -p "Enter your RunPod Endpoint URL: " RUNPOD_URL

    # Validate inputs
    if [ -z "$RUNPOD_KEY" ] || [ -z "$RUNPOD_URL" ]; then
        echo "❌ Error: RunPod credentials cannot be empty"
        exit 1
    fi

    if [[ ! "$RUNPOD_URL" =~ ^https://api\.runpod\.ai ]]; then
        echo "⚠️  Warning: URL doesn't look like a RunPod URL"
        read -p "Continue anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    # Update .env
    update_env_var "RUNPOD_API_KEY" "$RUNPOD_KEY"
    update_env_var "COMFYUI_API_URL" "$RUNPOD_URL"

    echo "✅ RunPod configured successfully"
    echo ""
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Printify Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Printify handles product creation and fulfillment."
echo "Get your credentials from: https://printify.com/app/account/api"
echo ""

read -p "Do you want to configure Printify? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📍 Step 1: Get your Printify API Key"
    echo "   Visit: https://printify.com/app/account/api"
    echo "   Click 'Generate Token' or use existing token"
    echo ""
    read -p "Enter your Printify API Key: " PRINTIFY_KEY

    echo ""
    echo "📍 Step 2: Get your Printify Shop ID"
    echo "   Visit: https://printify.com/app/stores"
    echo "   Your shop ID is in the URL or API settings"
    echo ""
    read -p "Enter your Printify Shop ID: " PRINTIFY_SHOP

    # Validate inputs
    if [ -z "$PRINTIFY_KEY" ] || [ -z "$PRINTIFY_SHOP" ]; then
        echo "❌ Error: Printify credentials cannot be empty"
        exit 1
    fi

    # Update .env
    update_env_var "PRINTIFY_API_KEY" "$PRINTIFY_KEY"
    update_env_var "PRINTIFY_SHOP_ID" "$PRINTIFY_SHOP"

    echo ""
    echo "📍 Step 3: Configure product defaults (optional)"
    echo ""
    echo "Blueprint ID options:"
    echo "  77  = Gildan 18500 Heavy Blend Hoodie (recommended)"
    echo "  3   = Gildan 5000 T-Shirt"
    echo "  380 = Gildan 64000 Softstyle T-Shirt"
    echo ""
    read -p "Blueprint ID [77]: " BLUEPRINT_ID
    BLUEPRINT_ID=${BLUEPRINT_ID:-77}

    echo ""
    echo "Provider ID options:"
    echo "  39  = SwiftPOD (US-based, reliable, recommended)"
    echo "  99  = Printify Choice (global)"
    echo ""
    read -p "Provider ID [39]: " PROVIDER_ID
    PROVIDER_ID=${PROVIDER_ID:-39}

    echo ""
    read -p "Default price in cents (3499 = \$34.99) [3499]: " PRICE
    PRICE=${PRICE:-3499}

    update_env_var "PRINTIFY_BLUEPRINT_ID" "$BLUEPRINT_ID"
    update_env_var "PRINTIFY_PROVIDER_ID" "$PROVIDER_ID"
    update_env_var "PRINTIFY_DEFAULT_PRICE_CENTS" "$PRICE"

    echo ""
    echo "✅ Printify configured successfully"
    echo ""
    echo "⚠️  IMPORTANT: Connect a sales channel in Printify dashboard"
    echo "   Visit: https://printify.com/app/stores"
    echo "   Connect Shopify, Etsy, or other platform to enable publishing"
    echo ""
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Claude API Configuration (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Claude API generates automated product titles and descriptions."
echo "Get your API key from: https://console.anthropic.com/settings/keys"
echo ""

read -p "Do you want to configure Claude API? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter your Anthropic API Key: " CLAUDE_KEY

    if [ -n "$CLAUDE_KEY" ]; then
        update_env_var "ANTHROPIC_API_KEY" "$CLAUDE_KEY"
        echo "✅ Claude API configured successfully"
    else
        echo "⚠️  Skipping Claude API - will use fallback metadata generation"
    fi
    echo ""
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Configuration Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Configuration saved to: .env"
echo ""
echo "Next steps:"
echo ""
echo "1. Start the gateway:"
echo "   ./start-gateway-runpod.sh"
echo ""
echo "2. Run proof of life:"
echo "   ./run-pod-pipeline.sh"
echo ""
echo "3. Or with custom theme:"
echo "   ./run-pod-pipeline.sh --theme 'cyberpunk neon art'"
echo ""
echo "📖 Full documentation: POD_PIPELINE_GUIDE.md"
echo ""

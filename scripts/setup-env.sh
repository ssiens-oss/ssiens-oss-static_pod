#!/bin/bash
# Environment Setup Script for Production Deployment

set -e

echo "========================================="
echo "  StaticWaves POD Studio - Setup"
echo "========================================="
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
        exit 0
    fi
fi

# Create .env from example
cp .env.example .env

echo "✅ Created .env file from template"
echo ""
echo "📝 Please configure the following required variables:"
echo ""

# Function to prompt for env var
prompt_env_var() {
    local var_name=$1
    local description=$2
    local is_secret=$3

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$description"
    echo "Variable: $var_name"

    if [ "$is_secret" = "secret" ]; then
        read -sp "Enter value (hidden): " value
        echo ""
    else
        read -p "Enter value: " value
    fi

    if [ -n "$value" ]; then
        # Escape special characters for sed
        escaped_value=$(echo "$value" | sed 's/[&/\]/\\&/g')
        # Update .env file
        sed -i "s|^${var_name}=.*|${var_name}=${escaped_value}|" .env
        echo "✅ Set $var_name"
    else
        echo "⏭️  Skipped $var_name"
    fi
    echo ""
}

echo "🔑 REQUIRED CONFIGURATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Claude API (Required)
prompt_env_var "ANTHROPIC_API_KEY" "Claude API Key - Get from https://console.anthropic.com/" "secret"

# Printify (Required)
prompt_env_var "PRINTIFY_API_KEY" "Printify API Key - Get from https://printify.com/app/account/api" "secret"
prompt_env_var "PRINTIFY_SHOP_ID" "Printify Shop ID - Find in your Printify dashboard" "normal"

echo "📦 OPTIONAL INTEGRATIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Configure Shopify integration? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    prompt_env_var "SHOPIFY_STORE_URL" "Shopify Store URL (e.g., yourstore.myshopify.com)" "normal"
    prompt_env_var "SHOPIFY_ACCESS_TOKEN" "Shopify Access Token" "secret"
fi

read -p "Configure TikTok Shop integration? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    prompt_env_var "TIKTOK_APP_KEY" "TikTok App Key" "secret"
    prompt_env_var "TIKTOK_APP_SECRET" "TikTok App Secret" "secret"
    prompt_env_var "TIKTOK_SHOP_ID" "TikTok Shop ID" "normal"
    prompt_env_var "TIKTOK_ACCESS_TOKEN" "TikTok Access Token" "secret"
fi

read -p "Configure Etsy integration? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    prompt_env_var "ETSY_API_KEY" "Etsy API Key" "secret"
    prompt_env_var "ETSY_SHOP_ID" "Etsy Shop ID" "normal"
    prompt_env_var "ETSY_ACCESS_TOKEN" "Etsy OAuth Token" "secret"
fi

echo "⚙️  PIPELINE SETTINGS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Auto-publish products to stores? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sed -i 's|^AUTO_PUBLISH=.*|AUTO_PUBLISH=true|' .env
    echo "✅ Auto-publish enabled"
else
    sed -i 's|^AUTO_PUBLISH=.*|AUTO_PUBLISH=false|' .env
    echo "📝 Products will be saved as drafts"
fi
echo ""

read -p "Default T-shirt price (default: 19.99): " tshirt_price
tshirt_price=${tshirt_price:-19.99}
sed -i "s|^DEFAULT_TSHIRT_PRICE=.*|DEFAULT_TSHIRT_PRICE=${tshirt_price}|" .env

read -p "Default Hoodie price (default: 34.99): " hoodie_price
hoodie_price=${hoodie_price:-34.99}
sed -i "s|^DEFAULT_HOODIE_PRICE=.*|DEFAULT_HOODIE_PRICE=${hoodie_price}|" .env

echo ""
echo "========================================="
echo "✅ Configuration Complete!"
echo "========================================="
echo ""
echo "📄 Configuration saved to .env"
echo ""
echo "Next steps:"
echo "  1. Review .env file and adjust any settings"
echo "  2. For local testing: npm run dev:server"
echo "  3. For RunPod deployment: ./scripts/deploy-runpod.sh"
echo ""

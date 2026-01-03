#!/bin/bash

# POD Pipeline API Key Setup Script
# This script helps you configure API keys securely

set -e

echo "======================================"
echo "  POD Pipeline API Key Setup"
echo "======================================"
echo ""

ENV_FILE=".env"

# Backup existing .env if it exists
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%s)"
    echo "✓ Backed up existing .env file"
fi

# Copy from example if .env doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    cp .env.example "$ENV_FILE"
    echo "✓ Created .env from .env.example"
fi

echo ""
echo "This script will help you configure API keys."
echo "Press ENTER to skip any optional service."
echo ""

# Function to update .env value
update_env() {
    local key=$1
    local value=$2
    if [ -n "$value" ]; then
        # Escape special characters for sed
        value=$(echo "$value" | sed 's/[\/&]/\\&/g')
        sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    fi
}

# === REQUIRED SETTINGS ===
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  REQUIRED SETTINGS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ComfyUI URL
read -p "ComfyUI API URL [http://localhost:8188]: " comfyui_url
comfyui_url=${comfyui_url:-http://localhost:8188}
update_env "COMFYUI_API_URL" "$comfyui_url"

# Claude API Key
read -p "Anthropic API Key (starts with sk-ant-): " claude_key
if [ -z "$claude_key" ]; then
    echo "⚠️  WARNING: Claude API key is required for the pipeline to work!"
    read -p "Enter Claude API Key: " claude_key
fi
update_env "ANTHROPIC_API_KEY" "$claude_key"

# Storage
read -p "Storage type (local/s3/gcs) [local]: " storage_type
storage_type=${storage_type:-local}
update_env "STORAGE_TYPE" "$storage_type"

read -p "Storage path [./designs]: " storage_path
storage_path=${storage_path:-./designs}
update_env "STORAGE_PATH" "$storage_path"

# Create storage directory if local
if [ "$storage_type" == "local" ]; then
    mkdir -p "$storage_path"
    echo "✓ Created storage directory: $storage_path"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PLATFORM INTEGRATIONS (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

enabled_platforms=()

# Printify
echo ""
echo "--- Printify Configuration ---"
read -p "Configure Printify? (y/n) [n]: " setup_printify
if [[ "$setup_printify" =~ ^[Yy]$ ]]; then
    read -p "Printify API Key: " printify_key
    read -p "Printify Shop ID: " printify_shop
    update_env "PRINTIFY_API_KEY" "$printify_key"
    update_env "PRINTIFY_SHOP_ID" "$printify_shop"
    enabled_platforms+=("printify")
    echo "✓ Printify configured"
fi

# Shopify
echo ""
echo "--- Shopify Configuration ---"
read -p "Configure Shopify? (y/n) [n]: " setup_shopify
if [[ "$setup_shopify" =~ ^[Yy]$ ]]; then
    read -p "Shopify Store URL (e.g., yourstore.myshopify.com): " shopify_url
    read -p "Shopify Access Token: " shopify_token
    update_env "SHOPIFY_STORE_URL" "$shopify_url"
    update_env "SHOPIFY_ACCESS_TOKEN" "$shopify_token"
    enabled_platforms+=("shopify")
    echo "✓ Shopify configured"
fi

# Etsy
echo ""
echo "--- Etsy Configuration ---"
read -p "Configure Etsy? (y/n) [n]: " setup_etsy
if [[ "$setup_etsy" =~ ^[Yy]$ ]]; then
    read -p "Etsy API Key: " etsy_key
    read -p "Etsy Shop ID: " etsy_shop
    read -p "Etsy Access Token: " etsy_token
    update_env "ETSY_API_KEY" "$etsy_key"
    update_env "ETSY_SHOP_ID" "$etsy_shop"
    update_env "ETSY_ACCESS_TOKEN" "$etsy_token"
    enabled_platforms+=("etsy")
    echo "✓ Etsy configured"
fi

# TikTok Shop
echo ""
echo "--- TikTok Shop Configuration ---"
read -p "Configure TikTok Shop? (y/n) [n]: " setup_tiktok
if [[ "$setup_tiktok" =~ ^[Yy]$ ]]; then
    read -p "TikTok App Key: " tiktok_key
    read -p "TikTok App Secret: " tiktok_secret
    read -p "TikTok Shop ID: " tiktok_shop
    read -p "TikTok Access Token: " tiktok_token
    update_env "TIKTOK_APP_KEY" "$tiktok_key"
    update_env "TIKTOK_APP_SECRET" "$tiktok_secret"
    update_env "TIKTOK_SHOP_ID" "$tiktok_shop"
    update_env "TIKTOK_ACCESS_TOKEN" "$tiktok_token"
    enabled_platforms+=("tiktok")
    echo "✓ TikTok Shop configured"
fi

# Update enabled platforms
if [ ${#enabled_platforms[@]} -gt 0 ]; then
    platforms_str=$(IFS=,; echo "${enabled_platforms[*]}")
    update_env "ENABLE_PLATFORMS" "$platforms_str"
fi

# Pipeline options
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PIPELINE OPTIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Auto-publish products? (true/false) [false]: " auto_publish
auto_publish=${auto_publish:-false}
update_env "AUTO_PUBLISH" "$auto_publish"

read -p "T-Shirt price [$] [19.99]: " tshirt_price
tshirt_price=${tshirt_price:-19.99}
update_env "DEFAULT_TSHIRT_PRICE" "$tshirt_price"

read -p "Hoodie price [$] [34.99]: " hoodie_price
hoodie_price=${hoodie_price:-34.99}
update_env "DEFAULT_HOODIE_PRICE" "$hoodie_price"

echo ""
echo "======================================"
echo "  ✓ Configuration Complete!"
echo "======================================"
echo ""
echo "Your configuration has been saved to: $ENV_FILE"
echo "Backup saved to: $ENV_FILE.backup.*"
echo ""
echo "Next steps:"
echo "  1. Review your configuration: cat .env"
echo "  2. Start the pipeline: npm run dev"
echo "  3. Or test configuration: npm run test:config"
echo ""
echo "Configured platforms: ${enabled_platforms[*]:-none}"
echo "Auto-publish: $auto_publish"
echo ""

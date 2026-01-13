#!/bin/bash
# Environment Validation Script
# Validates that all required environment variables are properly configured

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

check_var() {
    local var_name=$1
    local var_value="${!var_name}"
    local required=$2
    local description=$3

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ -z "$var_value" ]; then
        if [ "$required" == "true" ]; then
            echo -e "${RED}❌ ${var_name}${NC} - MISSING (Required)"
            echo "   Description: $description"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        else
            echo -e "${YELLOW}⚠️  ${var_name}${NC} - Not set (Optional)"
            echo "   Description: $description"
            WARNING_CHECKS=$((WARNING_CHECKS + 1))
        fi
    else
        echo -e "${GREEN}✅ ${var_name}${NC} - Set"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    fi
}

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Environment Configuration Validator              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Load .env file if it exists
if [ -f ".env" ]; then
    echo "📄 Loading .env file..."
    set -a
    source .env
    set +a
    echo ""
else
    echo "⚠️  No .env file found. Checking system environment variables..."
    echo ""
fi

echo "🔍 Validating configuration..."
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ComfyUI Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_var "COMFYUI_API_URL" "true" "ComfyUI API endpoint URL"
check_var "COMFYUI_OUTPUT_DIR" "true" "Directory for ComfyUI output images"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Claude AI Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_var "ANTHROPIC_API_KEY" "true" "Claude API key for prompt generation"
check_var "CLAUDE_MODEL" "false" "Claude model version to use"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Storage Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_var "STORAGE_TYPE" "true" "Storage type: local, s3, or gcs"
check_var "STORAGE_PATH" "true" "Local storage path for designs"

if [ "$STORAGE_TYPE" == "s3" ]; then
    echo ""
    echo "S3 Storage Configuration:"
    check_var "AWS_S3_BUCKET" "true" "AWS S3 bucket name"
    check_var "AWS_REGION" "true" "AWS region"
    check_var "AWS_ACCESS_KEY_ID" "true" "AWS access key ID"
    check_var "AWS_SECRET_ACCESS_KEY" "true" "AWS secret access key"
fi

if [ "$STORAGE_TYPE" == "gcs" ]; then
    echo ""
    echo "GCS Storage Configuration:"
    check_var "GCS_BUCKET" "true" "Google Cloud Storage bucket name"
    check_var "GCS_PROJECT_ID" "true" "GCP project ID"
    check_var "GCS_KEY_FILENAME" "true" "Path to GCS service account key file"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Printify Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_var "PRINTIFY_API_KEY" "true" "Printify API key"
check_var "PRINTIFY_SHOP_ID" "true" "Printify shop ID"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "E-commerce Platforms (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_var "SHOPIFY_STORE_URL" "false" "Shopify store URL"
check_var "SHOPIFY_ACCESS_TOKEN" "false" "Shopify access token"
check_var "TIKTOK_APP_KEY" "false" "TikTok Shop app key"
check_var "ETSY_API_KEY" "false" "Etsy API key"
check_var "INSTAGRAM_ACCESS_TOKEN" "false" "Instagram access token"
check_var "FACEBOOK_PAGE_ID" "false" "Facebook page ID"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Pipeline Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_var "AUTO_PUBLISH" "false" "Auto-publish products after creation"
check_var "ENABLE_PLATFORMS" "false" "Comma-separated list of enabled platforms"
check_var "DEFAULT_TSHIRT_PRICE" "false" "Default T-shirt price"
check_var "DEFAULT_HOODIE_PRICE" "false" "Default hoodie price"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Music API Configuration (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_var "VITE_MUSIC_API_URL" "false" "Music API URL"
check_var "REDIS_HOST" "false" "Redis host for music job queue"
check_var "MUSICGEN_MODEL" "false" "MusicGen model to use"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Validation Summary                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Total checks:    $TOTAL_CHECKS"
echo -e "${GREEN}Passed:          $PASSED_CHECKS${NC}"
echo -e "${YELLOW}Warnings:        $WARNING_CHECKS${NC}"
echo -e "${RED}Failed:          $FAILED_CHECKS${NC}"
echo ""

if [ $FAILED_CHECKS -gt 0 ]; then
    echo -e "${RED}❌ Validation FAILED${NC}"
    echo ""
    echo "Please set the missing required variables in your .env file or environment."
    echo "Copy .env.example to .env and fill in the values:"
    echo ""
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ Validation PASSED${NC}"
    echo ""
    if [ $WARNING_CHECKS -gt 0 ]; then
        echo "Note: Some optional features are not configured."
        echo "You can enable them by setting the relevant environment variables."
    fi
    echo ""
    exit 0
fi

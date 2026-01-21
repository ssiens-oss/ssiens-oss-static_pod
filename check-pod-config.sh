#!/bin/bash
# POD Pipeline Configuration Checker
# Validates all required credentials and provides troubleshooting guidance

set -e

echo "🔍 POD Pipeline - Configuration Checker"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# Load .env if exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env file not found!"
    echo ""
    echo "Run ./setup-pod-config.sh to create configuration"
    exit 1
fi

ERRORS=0
WARNINGS=0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  RunPod Serverless Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check RUNPOD_API_KEY
if [ -z "$RUNPOD_API_KEY" ] || [ "$RUNPOD_API_KEY" = "your-runpod-api-key" ]; then
    echo "❌ RUNPOD_API_KEY: Not configured"
    echo "   Fix: Run ./setup-pod-config.sh or set in .env"
    echo "   Get key from: https://www.runpod.io/console/user/settings"
    ERRORS=$((ERRORS + 1))
else
    # Mask the key for display
    MASKED_KEY="${RUNPOD_API_KEY:0:8}...${RUNPOD_API_KEY: -4}"
    echo "✅ RUNPOD_API_KEY: Configured ($MASKED_KEY)"

    # Test RunPod API connection
    echo "   Testing RunPod connection..."
    if [ -n "$COMFYUI_API_URL" ]; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "Authorization: Bearer $RUNPOD_API_KEY" \
            "$COMFYUI_API_URL" \
            --max-time 5 || echo "000")

        if [ "$HTTP_CODE" = "401" ]; then
            echo "   ❌ Authentication failed (401) - API key may be invalid"
            ERRORS=$((ERRORS + 1))
        elif [ "$HTTP_CODE" = "404" ]; then
            echo "   ⚠️  Endpoint not found (404) - check COMFYUI_API_URL"
            WARNINGS=$((WARNINGS + 1))
        elif [ "$HTTP_CODE" = "000" ]; then
            echo "   ⚠️  Connection timeout - endpoint may be inactive"
            WARNINGS=$((WARNINGS + 1))
        else
            echo "   ✅ Connection successful (HTTP $HTTP_CODE)"
        fi
    fi
fi

# Check COMFYUI_API_URL
echo ""
if [ -z "$COMFYUI_API_URL" ] || [ "$COMFYUI_API_URL" = "http://localhost:8188" ]; then
    echo "⚠️  COMFYUI_API_URL: Using default ($COMFYUI_API_URL)"
    echo "   For RunPod serverless, set to: https://api.runpod.ai/v2/{endpoint-id}/runsync"
    WARNINGS=$((WARNINGS + 1))
else
    echo "✅ COMFYUI_API_URL: $COMFYUI_API_URL"

    if [[ "$COMFYUI_API_URL" =~ api\.runpod\.ai ]]; then
        echo "   ℹ️  Using RunPod serverless"
    else
        echo "   ℹ️  Using direct ComfyUI connection"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Printify Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check PRINTIFY_API_KEY
if [ -z "$PRINTIFY_API_KEY" ] || [ "$PRINTIFY_API_KEY" = "your-printify-api-key" ]; then
    echo "❌ PRINTIFY_API_KEY: Not configured"
    echo "   Fix: Run ./setup-pod-config.sh or set in .env"
    echo "   Get key from: https://printify.com/app/account/api"
    ERRORS=$((ERRORS + 1))
else
    MASKED_KEY="${PRINTIFY_API_KEY:0:8}...${PRINTIFY_API_KEY: -4}"
    echo "✅ PRINTIFY_API_KEY: Configured ($MASKED_KEY)"

    # Test Printify API connection
    echo "   Testing Printify connection..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $PRINTIFY_API_KEY" \
        "https://api.printify.com/v1/shops.json" \
        --max-time 5 || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        echo "   ✅ Authentication successful"
    elif [ "$HTTP_CODE" = "401" ]; then
        echo "   ❌ Authentication failed - API key may be invalid"
        ERRORS=$((ERRORS + 1))
    else
        echo "   ⚠️  Connection issue (HTTP $HTTP_CODE)"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# Check PRINTIFY_SHOP_ID
echo ""
if [ -z "$PRINTIFY_SHOP_ID" ] || [ "$PRINTIFY_SHOP_ID" = "your-shop-id" ]; then
    echo "❌ PRINTIFY_SHOP_ID: Not configured"
    echo "   Fix: Run ./setup-pod-config.sh or set in .env"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PRINTIFY_SHOP_ID: $PRINTIFY_SHOP_ID"

    # Test shop access
    if [ -n "$PRINTIFY_API_KEY" ] && [ "$PRINTIFY_API_KEY" != "your-printify-api-key" ]; then
        echo "   Testing shop access..."
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "Authorization: Bearer $PRINTIFY_API_KEY" \
            "https://api.printify.com/v1/shops/$PRINTIFY_SHOP_ID/products.json?limit=1" \
            --max-time 5 || echo "000")

        if [ "$HTTP_CODE" = "200" ]; then
            echo "   ✅ Shop access confirmed"
        elif [ "$HTTP_CODE" = "404" ]; then
            echo "   ❌ Shop not found - check PRINTIFY_SHOP_ID"
            ERRORS=$((ERRORS + 1))
        elif [ "$HTTP_CODE" = "403" ]; then
            echo "   ❌ Access forbidden - check API key permissions"
            ERRORS=$((ERRORS + 1))
        else
            echo "   ⚠️  Could not verify shop access (HTTP $HTTP_CODE)"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
fi

# Check product settings
echo ""
BLUEPRINT_ID=${PRINTIFY_BLUEPRINT_ID:-77}
PROVIDER_ID=${PRINTIFY_PROVIDER_ID:-39}
PRICE=${PRINTIFY_DEFAULT_PRICE_CENTS:-3499}

echo "✅ PRINTIFY_BLUEPRINT_ID: $BLUEPRINT_ID"
case $BLUEPRINT_ID in
    77) echo "   ℹ️  Gildan 18500 Heavy Blend Hoodie" ;;
    3) echo "   ℹ️  Gildan 5000 T-Shirt" ;;
    380) echo "   ℹ️  Gildan 64000 Softstyle T-Shirt" ;;
    *) echo "   ℹ️  Custom blueprint" ;;
esac

echo "✅ PRINTIFY_PROVIDER_ID: $PROVIDER_ID"
case $PROVIDER_ID in
    39) echo "   ℹ️  SwiftPOD (US-based)" ;;
    99) echo "   ℹ️  Printify Choice (global)" ;;
    *) echo "   ℹ️  Custom provider" ;;
esac

echo "✅ PRINTIFY_DEFAULT_PRICE_CENTS: $PRICE (\$$(echo "scale=2; $PRICE/100" | bc))"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Claude API Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check ANTHROPIC_API_KEY
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-your-api-key-here" ]; then
    echo "⚠️  ANTHROPIC_API_KEY: Not configured (optional)"
    echo "   Impact: Will use fallback metadata generation"
    echo "   Get key from: https://console.anthropic.com/settings/keys"
    WARNINGS=$((WARNINGS + 1))
else
    MASKED_KEY="${ANTHROPIC_API_KEY:0:12}...${ANTHROPIC_API_KEY: -4}"
    echo "✅ ANTHROPIC_API_KEY: Configured ($MASKED_KEY)"

    # Test Claude API
    echo "   Testing Claude API connection..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        "https://api.anthropic.com/v1/messages" \
        --max-time 5 || echo "000")

    # Claude API returns 400 for GET requests, which is expected
    if [ "$HTTP_CODE" = "400" ] || [ "$HTTP_CODE" = "405" ]; then
        echo "   ✅ API key valid (endpoint responds)"
    elif [ "$HTTP_CODE" = "401" ]; then
        echo "   ❌ Authentication failed - API key may be invalid"
        ERRORS=$((ERRORS + 1))
    elif [ "$HTTP_CODE" = "000" ]; then
        echo "   ⚠️  Connection timeout"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "   ℹ️  Response: HTTP $HTTP_CODE"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Gateway Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python 3: Not found"
    ERRORS=$((ERRORS + 1))
fi

# Check required Python packages
if python3 -c "import flask" 2>/dev/null; then
    FLASK_VERSION=$(python3 -c "import flask; print(flask.__version__)")
    echo "✅ Flask: $FLASK_VERSION"
else
    echo "❌ Flask: Not installed"
    echo "   Fix: pip install -r gateway/requirements.txt"
    ERRORS=$((ERRORS + 1))
fi

if python3 -c "import requests" 2>/dev/null; then
    echo "✅ Requests: Installed"
else
    echo "❌ Requests: Not installed"
    ERRORS=$((ERRORS + 1))
fi

if python3 -c "import PIL" 2>/dev/null; then
    echo "✅ Pillow: Installed"
else
    echo "❌ Pillow: Not installed"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ All checks passed! Configuration is complete."
    echo ""
    echo "Ready to start:"
    echo "  ./start-gateway-runpod.sh"
    EXIT_CODE=0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Configuration has $WARNINGS warning(s) but should work."
    echo ""
    echo "You can start the gateway:"
    echo "  ./start-gateway-runpod.sh"
    EXIT_CODE=0
else
    echo "❌ Configuration has $ERRORS error(s) that must be fixed."
    echo ""
    echo "Run setup script to fix:"
    echo "  ./setup-pod-config.sh"
    EXIT_CODE=1
fi

echo ""
echo "Common fixes:"
echo "  • Missing credentials: ./setup-pod-config.sh"
echo "  • Missing Python packages: pip install -r gateway/requirements.txt"
echo "  • Printify publishing fails: Connect sales channel in Printify dashboard"
echo ""

exit $EXIT_CODE

#!/bin/bash
# Batch publish POD designs with auto-generated metadata

GATEWAY_URL="${GATEWAY_URL:-http://localhost:5000}"

echo "🚀 Batch POD Publisher"
echo "======================"
echo ""

# Show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all              Publish all approved images"
    echo "  --auto-approve     Auto-approve pending images before publishing"
    echo "  --ids \"id1,id2\"   Publish specific image IDs (comma-separated)"
    echo "  --style STYLE      Art style for descriptions (default: 'abstract art')"
    echo "  --price CENTS      Price in cents (default: from config)"
    echo "  --color COLOR      Color filter (default: 'black')"
    echo "  --max-variants N   Max variants per product (default: 50)"
    echo "  --help             Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --all                                  # Publish all approved images"
    echo "  $0 --all --auto-approve                   # Auto-approve and publish all"
    echo "  $0 --ids \"img1,img2,img3\"                # Publish specific images"
    echo "  $0 --all --style \"geometric\" --price 4499 # Custom style and price"
    echo ""
}

# Parse arguments
PUBLISH_ALL=false
AUTO_APPROVE=false
IMAGE_IDS=""
STYLE="abstract art"
PRICE_CENTS=""
COLOR_FILTER=""
MAX_VARIANTS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            PUBLISH_ALL=true
            shift
            ;;
        --auto-approve)
            AUTO_APPROVE=true
            shift
            ;;
        --ids)
            IMAGE_IDS="$2"
            shift 2
            ;;
        --style)
            STYLE="$2"
            shift 2
            ;;
        --price)
            PRICE_CENTS="$2"
            shift 2
            ;;
        --color)
            COLOR_FILTER="$2"
            shift 2
            ;;
        --max-variants)
            MAX_VARIANTS="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Build JSON payload
if [ "$PUBLISH_ALL" = true ]; then
    echo "📋 Publishing all approved images..."
    JSON_PAYLOAD="{\"auto_approve\": $AUTO_APPROVE, \"style\": \"$STYLE\""
elif [ -n "$IMAGE_IDS" ]; then
    # Convert comma-separated IDs to JSON array
    IDS_ARRAY=$(echo "$IMAGE_IDS" | jq -R 'split(",") | map(select(length > 0))')
    echo "📋 Publishing specific images: $IMAGE_IDS"
    JSON_PAYLOAD="{\"image_ids\": $IDS_ARRAY, \"auto_approve\": $AUTO_APPROVE, \"style\": \"$STYLE\""
else
    echo "❌ Error: Must specify --all or --ids"
    show_help
    exit 1
fi

# Add optional parameters
if [ -n "$PRICE_CENTS" ]; then
    JSON_PAYLOAD="$JSON_PAYLOAD, \"price_cents\": $PRICE_CENTS"
fi
if [ -n "$COLOR_FILTER" ]; then
    JSON_PAYLOAD="$JSON_PAYLOAD, \"color_filter\": \"$COLOR_FILTER\""
fi
if [ -n "$MAX_VARIANTS" ]; then
    JSON_PAYLOAD="$JSON_PAYLOAD, \"max_variants\": $MAX_VARIANTS"
fi

JSON_PAYLOAD="$JSON_PAYLOAD}"

echo ""
echo "🎨 Settings:"
echo "   Style: $STYLE"
[ -n "$PRICE_CENTS" ] && echo "   Price: \$$(echo "scale=2; $PRICE_CENTS/100" | bc)"
[ -n "$COLOR_FILTER" ] && echo "   Color: $COLOR_FILTER"
[ -n "$MAX_VARIANTS" ] && echo "   Max variants: $MAX_VARIANTS"
echo ""
echo "🔄 Starting batch publish..."
echo ""

# Make API request
RESPONSE=$(curl -s -X POST "$GATEWAY_URL/api/batch_publish" \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD")

# Check if curl succeeded
if [ $? -ne 0 ]; then
    echo "❌ Failed to connect to gateway at $GATEWAY_URL"
    exit 1
fi

# Parse response
SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')

if [ "$SUCCESS" = "true" ]; then
    TOTAL=$(echo "$RESPONSE" | jq -r '.summary.total')
    SUCCEEDED=$(echo "$RESPONSE" | jq -r '.summary.succeeded')
    FAILED=$(echo "$RESPONSE" | jq -r '.summary.failed')
    SKIPPED=$(echo "$RESPONSE" | jq -r '.summary.skipped')

    echo "✅ Batch publish complete!"
    echo ""
    echo "📊 Summary:"
    echo "   Total:     $TOTAL"
    echo "   Succeeded: $SUCCEEDED"
    echo "   Failed:    $FAILED"
    echo "   Skipped:   $SKIPPED"
    echo ""

    # Show successful products
    if [ "$SUCCEEDED" -gt 0 ]; then
        echo "✅ Published products:"
        echo "$RESPONSE" | jq -r '.results.succeeded[] | "   • \(.title) (ID: \(.product_id))"'
        echo ""
    fi

    # Show failures
    if [ "$FAILED" -gt 0 ]; then
        echo "❌ Failed:"
        echo "$RESPONSE" | jq -r '.results.failed[] | "   • \(.image_id): \(.error)"'
        echo ""
    fi

    # Show skipped
    if [ "$SKIPPED" -gt 0 ]; then
        echo "⏭️  Skipped:"
        echo "$RESPONSE" | jq -r '.results.skipped[] | "   • \(.image_id): \(.reason)"'
        echo ""
    fi

    # Exit code based on results
    if [ "$FAILED" -gt 0 ]; then
        exit 2  # Partial success
    else
        exit 0  # Complete success
    fi
else
    ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
    echo "❌ Batch publish failed: $ERROR"
    exit 1
fi

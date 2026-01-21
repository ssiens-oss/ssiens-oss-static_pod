#!/bin/bash
# POD Pipeline Runner
# Convenient wrapper for running the POD automation pipeline

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_title() {
    echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
}

# Default values
THEME="vibrant abstract art"
GATEWAY_URL="http://localhost:5000"
AUTO_PUBLISH="true"
OUTPUT_FILE=""
MODE="proof-of-life"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --theme)
            THEME="$2"
            shift 2
            ;;
        --gateway-url)
            GATEWAY_URL="$2"
            shift 2
            ;;
        --no-publish)
            AUTO_PUBLISH="false"
            shift
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --mode)
            MODE="$2"
            shift 2
            ;;
        --help|-h)
            cat << EOF
POD Pipeline Runner

Usage: $(basename "$0") [OPTIONS]

Options:
    --theme THEME           Design theme/prompt (default: "vibrant abstract art")
    --gateway-url URL       Gateway URL (default: http://localhost:5000)
    --no-publish            Skip auto-publishing to Printify
    --output FILE           Save results to JSON file
    --mode MODE             Pipeline mode: proof-of-life, batch, continuous
    --help                  Show this help message

Examples:
    # Run proof-of-life with default theme
    $(basename "$0")

    # Generate with custom theme
    $(basename "$0") --theme "cyberpunk neon cityscape"

    # Generate without publishing
    $(basename "$0") --theme "nature landscape" --no-publish

    # Save results to file
    $(basename "$0") --theme "abstract geometric" --output results.json

Modes:
    proof-of-life   - Single generation with auto-publish (default)
    batch           - Generate multiple designs in sequence
    continuous      - Keep generating designs until stopped

Environment Variables:
    PROOF_OF_LIFE   - Set to "true" to auto-run on gateway startup
    ANTHROPIC_API_KEY - Claude API key for metadata generation
EOF
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Change to script directory
cd "$(dirname "$0")"

log_title "POD Pipeline Runner"
echo ""

# Check if gateway is running
log_info "Checking gateway health..."
if curl -s -f "${GATEWAY_URL}/health" > /dev/null 2>&1; then
    log_success "Gateway is healthy at ${GATEWAY_URL}"
else
    log_error "Gateway is not responding at ${GATEWAY_URL}"
    echo ""
    echo "Start the gateway first:"
    echo "  ./start-gateway-runpod.sh"
    exit 1
fi

echo ""

# Run based on mode
case $MODE in
    proof-of-life)
        log_info "Running proof-of-life pipeline..."
        log_info "Theme: ${THEME}"
        log_info "Auto-publish: ${AUTO_PUBLISH}"
        echo ""

        ARGS=(--theme "$THEME" --gateway-url "$GATEWAY_URL")

        if [ "$AUTO_PUBLISH" = "false" ]; then
            ARGS+=(--no-publish)
        fi

        if [ -n "$OUTPUT_FILE" ]; then
            ARGS+=(--output "$OUTPUT_FILE")
        fi

        python3 ./pod-pipeline.py "${ARGS[@]}"

        if [ $? -eq 0 ]; then
            echo ""
            log_success "Proof-of-life completed successfully!"

            if [ -n "$OUTPUT_FILE" ] && [ -f "$OUTPUT_FILE" ]; then
                echo ""
                log_info "Results saved to: ${OUTPUT_FILE}"

                # Extract key info from JSON
                if command -v jq &> /dev/null; then
                    TITLE=$(jq -r '.metadata.title // "N/A"' "$OUTPUT_FILE")
                    IMAGE_ID=$(jq -r '.image_id // "N/A"' "$OUTPUT_FILE")
                    PRODUCT_ID=$(jq -r '.product_id // "N/A"' "$OUTPUT_FILE")
                    DURATION=$(jq -r '.duration_seconds // "N/A"' "$OUTPUT_FILE")

                    echo ""
                    echo "📊 Summary:"
                    echo "   Title: ${TITLE}"
                    echo "   Image ID: ${IMAGE_ID}"
                    if [ "$PRODUCT_ID" != "N/A" ] && [ "$PRODUCT_ID" != "null" ]; then
                        echo "   Product ID: ${PRODUCT_ID}"
                    fi
                    echo "   Duration: ${DURATION}s"
                fi
            fi
        else
            echo ""
            log_error "Proof-of-life failed!"
            exit 1
        fi
        ;;

    batch)
        log_info "Running batch pipeline..."
        COUNT=${BATCH_COUNT:-5}
        log_info "Generating ${COUNT} designs..."
        echo ""

        for i in $(seq 1 $COUNT); do
            echo ""
            log_title "Design ${i}/${COUNT}"

            BATCH_OUTPUT="/tmp/pod-batch-${i}.json"
            python3 ./pod-pipeline.py --theme "$THEME" --gateway-url "$GATEWAY_URL" --output "$BATCH_OUTPUT"

            if [ $? -ne 0 ]; then
                log_error "Design ${i} failed"
            else
                log_success "Design ${i} completed"
            fi

            # Wait between generations
            if [ $i -lt $COUNT ]; then
                sleep 5
            fi
        done

        log_success "Batch pipeline completed!"
        ;;

    continuous)
        log_info "Running continuous pipeline..."
        log_info "Press Ctrl+C to stop"
        echo ""

        COUNT=1
        while true; do
            echo ""
            log_title "Design ${COUNT}"

            CONT_OUTPUT="/tmp/pod-continuous-${COUNT}.json"
            python3 ./pod-pipeline.py --theme "$THEME" --gateway-url "$GATEWAY_URL" --output "$CONT_OUTPUT"

            if [ $? -ne 0 ]; then
                log_error "Design ${COUNT} failed, continuing..."
            else
                log_success "Design ${COUNT} completed"
            fi

            COUNT=$((COUNT + 1))

            # Wait between generations
            sleep 10
        done
        ;;

    *)
        log_error "Unknown mode: $MODE"
        echo "Valid modes: proof-of-life, batch, continuous"
        exit 1
        ;;
esac

#!/bin/bash
# Quick template switcher for common POD products
# Usage: ./scripts/set_product_template.sh [hoodie|tshirt|premium-tee|softstyle]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/.env"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_usage() {
    echo -e "${BLUE}POD Product Template Switcher${NC}"
    echo ""
    echo "Usage: $0 [template]"
    echo ""
    echo "Available templates:"
    echo -e "  ${GREEN}hoodie${NC}       - Gildan 18500 Heavy Blend Hoodie (Blueprint 165, \$34.99) 🔥 Popular"
    echo -e "  ${GREEN}tshirt${NC}       - Gildan 5000 Heavy Cotton T-Shirt (Blueprint 3, \$15.99)"
    echo -e "  ${GREEN}premium-tee${NC}  - Bella+Canvas 3001 Unisex Jersey (Blueprint 77, \$19.99)"
    echo -e "  ${GREEN}softstyle${NC}    - Gildan 64000 Softstyle T-Shirt (Blueprint 380, \$17.99)"
    echo ""
    echo "Examples:"
    echo "  $0 hoodie          # Switch to Gildan 18500 hoodie template"
    echo "  $0 premium-tee     # Switch to Bella+Canvas 3001 t-shirt"
    echo ""
    echo "See docs/PRINTIFY_BLUEPRINTS.md for more details"
}

update_env_var() {
    local var_name=$1
    local new_value=$2

    if grep -q "^${var_name}=" "$ENV_FILE"; then
        # Update existing variable
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/^${var_name}=.*/${var_name}=${new_value}/" "$ENV_FILE"
        else
            # Linux
            sed -i "s/^${var_name}=.*/${var_name}=${new_value}/" "$ENV_FILE"
        fi
    else
        # Add new variable
        echo "${var_name}=${new_value}" >> "$ENV_FILE"
    fi
}

set_template() {
    local template=$1
    local blueprint_id=""
    local provider_id="39"  # SwiftPOD default
    local price_cents=""
    local product_name=""

    case $template in
        hoodie)
            blueprint_id="77"
            price_cents="3499"
            product_name="Gildan 18500 Heavy Blend Hoodie"
            ;;
        tshirt)
            blueprint_id="3"
            price_cents="1599"
            product_name="Gildan 5000 Heavy Cotton T-Shirt"
            ;;
        premium-tee)
            blueprint_id="6"
            price_cents="1999"
            product_name="Bella+Canvas 3001 Unisex Jersey T-Shirt"
            ;;
        softstyle)
            blueprint_id="380"
            price_cents="1799"
            product_name="Gildan 64000 Softstyle T-Shirt"
            ;;
        *)
            echo -e "${RED}Error: Unknown template '${template}'${NC}"
            echo ""
            show_usage
            exit 1
            ;;
    esac

    echo -e "${BLUE}Setting product template to: ${GREEN}${product_name}${NC}"
    echo ""
    echo "  Blueprint ID: ${blueprint_id}"
    echo "  Provider ID:  ${provider_id} (SwiftPOD)"
    echo "  Default Price: \$$(awk "BEGIN {printf \"%.2f\", ${price_cents}/100}")"
    echo ""

    # Update .env file
    update_env_var "PRINTIFY_BLUEPRINT_ID" "$blueprint_id"
    update_env_var "PRINTIFY_PROVIDER_ID" "$provider_id"
    update_env_var "PRINTIFY_DEFAULT_PRICE_CENTS" "$price_cents"

    echo -e "${GREEN}✅ Template updated successfully!${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Remember to restart the gateway for changes to take effect:${NC}"
    echo "   cd gateway && flask run"
    echo ""
    echo -e "${BLUE}💡 Tip: Verify your blueprint with:${NC}"
    echo "   python scripts/find_printify_blueprint.py --id ${blueprint_id} --providers"
}

# Main script
if [ $# -eq 0 ]; then
    show_usage
    exit 0
fi

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: .env file not found at ${ENV_FILE}${NC}"
    echo "Please create one from .env.example first:"
    echo "  cp .env.example .env"
    exit 1
fi

set_template "$1"

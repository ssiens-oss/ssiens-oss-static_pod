#!/bin/bash
# Test Script for StaticWaves POD API

API="http://localhost:5000"

echo "🧪 StaticWaves POD - API Test Suite"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"

    echo -ne "${BLUE}Testing${NC} $name... "

    if [ -n "$data" ]; then
        response=$(curl -s -X "$method" "$API$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    else
        response=$(curl -s -X "$method" "$API$endpoint" 2>&1)
    fi

    if [ $? -eq 0 ] && echo "$response" | python3 -m json.tool > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# Test Core Endpoints
echo "📡 Core API Endpoints"
echo "--------------------"
test_endpoint "Health Check" "GET" "/health"
test_endpoint "Queue Status" "GET" "/queue"
test_endpoint "Statistics" "GET" "/stats"
test_endpoint "License Status" "GET" "/license"
echo ""

# Test Agent Endpoints
echo "🤖 Agent Endpoints"
echo "------------------"
test_endpoint "Agent Status" "GET" "/agents/status"
test_endpoint "List Agents" "GET" "/agents/agents"
test_endpoint "List Workflows" "GET" "/agents/workflows"
echo ""

# Test Queue Operations
echo "📋 Queue Operations"
echo "-------------------"
test_endpoint "Add to Queue" "POST" "/queue/add" '{
    "title": "Test Product",
    "prompt": "test cosmic art",
    "type": "hoodie",
    "base_cost": 35.00,
    "inventory": 100
}'
test_endpoint "Get Pending Queue" "GET" "/queue/pending"
echo ""

# Summary
echo ""
echo "======================================"
echo "✅ API is running on http://localhost:5000"
echo ""
echo "📚 Available Endpoints:"
echo "  GET  /health                  - Health check"
echo "  GET  /queue                   - Queue status"
echo "  GET  /stats                   - Statistics"
echo "  GET  /license                 - License info"
echo "  POST /publish                 - Publish product"
echo "  POST /queue/add               - Add to queue"
echo "  GET  /agents/status           - Agent status"
echo "  GET  /agents/workflows        - List workflows"
echo "  POST /agents/quick-launch     - Quick launch"
echo ""
echo "🌐 Web UI: http://localhost:5173 (if frontend running)"
echo "📖 Docs: See POD_STACK.md and AGENTS.md"
echo ""

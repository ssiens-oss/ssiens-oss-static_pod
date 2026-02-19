#!/bin/bash
# StaticWaves Forge - System Test Script
# Tests the complete generation pipeline locally

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                        ║${NC}"
echo -e "${BLUE}║         ${GREEN}StaticWaves Forge System Test${BLUE}                ║${NC}"
echo -e "${BLUE}║                                                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
WEB_URL="${WEB_URL:-http://localhost:3000}"
REDIS_URL="${REDIS_URL:-redis://localhost:6379}"

# Test 1: Check Redis
echo -e "${YELLOW}[1/7]${NC} Testing Redis connection..."
if redis-cli -u "$REDIS_URL" ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Redis is running"
else
    echo -e "${RED}✗${NC} Redis is not running"
    echo "   Start Redis with: docker run -d -p 6379:6379 redis:7-alpine"
    exit 1
fi

# Test 2: Check API
echo -e "${YELLOW}[2/7]${NC} Testing API server..."
if curl -s "$API_URL/" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API is responding at $API_URL"
else
    echo -e "${RED}✗${NC} API is not running"
    echo "   Start API with: cd apps/api && python main.py"
    exit 1
fi

# Test 3: Check API health
echo -e "${YELLOW}[3/7]${NC} Checking API health..."
HEALTH=$(curl -s "$API_URL/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} API is healthy"
else
    echo -e "${RED}✗${NC} API health check failed"
    echo "   Response: $HEALTH"
    exit 1
fi

# Test 4: Check queue stats
echo -e "${YELLOW}[4/7]${NC} Checking queue stats..."
STATS=$(curl -s "$API_URL/api/generate/queue/stats")
echo -e "${GREEN}✓${NC} Queue stats: $STATS"

# Test 5: Create test job
echo -e "${YELLOW}[5/7]${NC} Creating test generation job..."
JOB_RESPONSE=$(curl -s -X POST "$API_URL/api/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a low-poly red cube",
    "asset_type": "prop",
    "style": "low-poly",
    "export_formats": ["glb"],
    "poly_budget": 1000
  }')

JOB_ID=$(echo "$JOB_RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$JOB_ID" ]; then
    echo -e "${GREEN}✓${NC} Job created: $JOB_ID"
else
    echo -e "${RED}✗${NC} Failed to create job"
    echo "   Response: $JOB_RESPONSE"
    exit 1
fi

# Test 6: Check job status
echo -e "${YELLOW}[6/7]${NC} Checking job status..."
sleep 2
JOB_STATUS=$(curl -s "$API_URL/api/jobs/$JOB_ID")
STATUS=$(echo "$JOB_STATUS" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
echo -e "${GREEN}✓${NC} Job status: $STATUS"

# Test 7: Check if worker is running
echo -e "${YELLOW}[7/7]${NC} Checking for active workers..."
WORKERS=$(curl -s "$API_URL/api/jobs/workers/list")
WORKER_COUNT=$(echo "$WORKERS" | grep -o '"total":[0-9]*' | cut -d':' -f2)

if [ "$WORKER_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Found $WORKER_COUNT active worker(s)"
else
    echo -e "${YELLOW}⚠${NC} No workers found"
    echo "   Job will remain queued until a worker starts"
    echo "   Start worker with: cd apps/worker && python worker.py"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ System test complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

echo "📊 Test Results:"
echo "   Job ID: $JOB_ID"
echo "   Status: $STATUS"
echo "   Workers: $WORKER_COUNT"
echo ""

echo "🔗 Service URLs:"
echo "   API:     $API_URL"
echo "   Docs:    $API_URL/docs"
echo "   Web GUI: $WEB_URL"
echo ""

echo "📝 Monitor job progress:"
echo "   curl $API_URL/api/jobs/$JOB_ID"
echo ""

echo "🎨 Next steps:"
echo "   1. Start a worker if not running: cd apps/worker && python worker.py"
echo "   2. Open Web GUI: $WEB_URL/generate"
echo "   3. Create more assets via API or Web GUI"
echo ""

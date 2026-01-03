#!/bin/bash
# Deployment Verification Script
# Run this on RunPod after ./runpod-start.sh completes

echo "╔════════════════════════════════════════════════════╗"
echo "║     POD Engine - Deployment Verification          ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS="${GREEN}✓${NC}"
FAIL="${RED}✗${NC}"
WARN="${YELLOW}⚠${NC}"

echo "Checking deployment status..."
echo ""

# Check 1: Services Running
echo "1. Services Running"
if ps aux | grep -q "[C]omfyUI"; then
    echo -e "  $PASS ComfyUI running"
else
    echo -e "  $FAIL ComfyUI not running"
fi

if ps aux | grep -q "[p]od-engine-api"; then
    echo -e "  $PASS POD Engine API running"
else
    echo -e "  $FAIL POD Engine API not running"
fi
echo ""

# Check 2: API Health
echo "2. API Health Checks"
if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo -e "  $PASS POD Engine API responding"
    curl -s http://localhost:3000/health | jq -r '"  Uptime: \(.uptime)s"' 2>/dev/null || echo "  Status: OK"
else
    echo -e "  $FAIL POD Engine API not responding"
fi

if curl -s http://localhost:8188 > /dev/null 2>&1; then
    echo -e "  $PASS ComfyUI responding"
else
    echo -e "  $FAIL ComfyUI not responding"
fi
echo ""

# Check 3: Directory Structure
echo "3. Directory Structure"
DIRS=(
    "/workspace/data/designs"
    "/workspace/data/mockups"
    "/workspace/data/mockup-templates"
    "/workspace/logs"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "  $PASS $dir"
    else
        echo -e "  $FAIL $dir"
    fi
done
echo ""

# Check 4: Mockup Templates
echo "4. Mockup Templates"
if [ -f "/workspace/data/mockup-templates/tshirt_base.png" ]; then
    SIZE=$(stat -c%s "/workspace/data/mockup-templates/tshirt_base.png" 2>/dev/null || echo "0")
    echo -e "  $PASS tshirt_base.png ($SIZE bytes)"
else
    echo -e "  $FAIL tshirt_base.png not found"
fi

if [ -f "/workspace/data/mockup-templates/hoodie_base.png" ]; then
    SIZE=$(stat -c%s "/workspace/data/mockup-templates/hoodie_base.png" 2>/dev/null || echo "0")
    echo -e "  $PASS hoodie_base.png ($SIZE bytes)"
else
    echo -e "  $FAIL hoodie_base.png not found"
fi
echo ""

# Check 5: Python Dependencies
echo "5. Python Dependencies"
PACKAGES=("torch" "transformers" "rembg" "PIL" "aiohttp")

for pkg in "${PACKAGES[@]}"; do
    if python -c "import $pkg" 2>/dev/null; then
        echo -e "  $PASS $pkg"
    else
        echo -e "  $FAIL $pkg"
    fi
done
echo ""

# Check 6: Node.js Dependencies
echo "6. Node.js Dependencies"
if [ -d "node_modules/express" ]; then
    echo -e "  $PASS express"
else
    echo -e "  $FAIL express"
fi

if [ -d "node_modules/tsx" ]; then
    echo -e "  $PASS tsx"
else
    echo -e "  $FAIL tsx"
fi
echo ""

# Check 7: AI Model
echo "7. AI Models"
MODEL_DIR="/workspace/ComfyUI/models/checkpoints"
if [ -d "$MODEL_DIR" ]; then
    MODEL_COUNT=$(ls -1 "$MODEL_DIR"/*.safetensors 2>/dev/null | wc -l)
    if [ "$MODEL_COUNT" -gt 0 ]; then
        echo -e "  $PASS $MODEL_COUNT model(s) found"
        ls -1 "$MODEL_DIR"/*.safetensors 2>/dev/null | while read model; do
            SIZE=$(stat -c%s "$model" 2>/dev/null || stat -f%z "$model" 2>/dev/null)
            SIZE_GB=$(echo "scale=2; $SIZE/1024/1024/1024" | bc 2>/dev/null || echo "?")
            echo "    - $(basename "$model") (${SIZE_GB}GB)"
        done
    else
        echo -e "  $FAIL No models found"
    fi
else
    echo -e "  $FAIL Model directory not found"
fi
echo ""

# Summary
echo "════════════════════════════════════════════════════"
echo "Deployment Status Summary"
echo "════════════════════════════════════════════════════"
echo ""

# Quick test
echo "Testing job submission..."
RESPONSE=$(curl -s -X POST http://localhost:3000/api/generate \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "Test deployment verification",
        "productTypes": ["tshirt"],
        "autoPublish": false
    }' 2>/dev/null)

if echo "$RESPONSE" | grep -q "jobId"; then
    JOB_ID=$(echo "$RESPONSE" | jq -r '.jobId' 2>/dev/null)
    echo -e "$PASS Test job submitted: $JOB_ID"
    echo ""
    echo "Check job status:"
    echo "  curl http://localhost:3000/api/jobs/$JOB_ID | jq ."
else
    echo -e "$FAIL Failed to submit test job"
fi

echo ""
echo "════════════════════════════════════════════════════"
echo "Access Points:"
echo "════════════════════════════════════════════════════"
echo ""
echo "POD Engine API:    http://localhost:3000"
echo "Monitoring GUI:    http://localhost:8080/monitor.html"
echo "ComfyUI:           http://localhost:8188"
echo ""
echo "Use SSH port forwarding to access from local machine:"
echo "  ssh -L 3000:localhost:3000 -L 8080:localhost:8080 -L 8188:localhost:8188 <runpod-connection>"
echo ""
echo "════════════════════════════════════════════════════"
echo "Deployment verification complete!"
echo "════════════════════════════════════════════════════"

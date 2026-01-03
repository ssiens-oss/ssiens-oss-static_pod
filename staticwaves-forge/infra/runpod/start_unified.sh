#!/bin/bash
# StaticWaves Unified Deployment Startup Script
# Runs both POD and Forge services on single RunPod instance

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 StaticWaves Unified Platform Starting..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Environment Check
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "📋 Environment Configuration:"
echo "   RunPod ID: ${RUNPOD_POD_ID:-local}"
echo "   GPU: ${RUNPOD_GPU_COUNT:-0} × ${CUDA_VISIBLE_DEVICES:-N/A}"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Service Ports
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export POD_WEB_PORT=3000
export POD_API_PORT=8001
export FORGE_API_PORT=8000
export FORGE_WEB_PORT=3001
export NGINX_PORT=80

echo "🌐 Port Mapping:"
echo "   ┌─────────────────────────────────────┐"
echo "   │ Service          │ Port             │"
echo "   ├─────────────────────────────────────┤"
echo "   │ Nginx (Entry)    │ :80              │"
echo "   │ POD Web          │ :3000            │"
echo "   │ POD API          │ :8001            │"
echo "   │ Forge API        │ :8000            │"
echo "   │ Forge Web        │ :3001            │"
echo "   │ Redis            │ :6379            │"
echo "   └─────────────────────────────────────┘"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# URL Structure
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔗 URL Structure:"
echo "   POD Service:"
echo "   • Web:    http://localhost/                  (root)"
echo "   • API:    http://localhost/api/pod/"
echo ""
echo "   Forge Service:"
echo "   • Web:    http://localhost/forge/"
echo "   • API:    http://localhost/api/forge/"
echo "   • Docs:   http://localhost/forge/docs"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GPU Check
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if command -v nvidia-smi &> /dev/null; then
    echo "🎮 GPU Status:"
    nvidia-smi --query-gpu=index,name,memory.total,memory.free --format=csv,noheader | \
        awk -F', ' '{printf "   GPU %s: %s (%s total, %s free)\n", $1, $2, $3, $4}'
    echo ""
else
    echo "⚠️  No GPU detected (CPU mode)"
    echo ""
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Start Services
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  Starting Services..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start with docker-compose
cd /workspace/staticwaves-forge/infra/runpod
docker-compose -f docker-compose.unified.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Health Checks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo ""
echo "🏥 Health Check:"

check_service() {
    local name=$1
    local url=$2
    if curl -sf "$url" > /dev/null 2>&1; then
        echo "   ✅ $name: Healthy"
        return 0
    else
        echo "   ❌ $name: Not responding"
        return 1
    fi
}

check_service "Nginx"      "http://localhost/health"
check_service "POD API"    "http://localhost/api/pod/health"
check_service "Forge API"  "http://localhost/api/forge/health"
check_service "Redis"      "http://localhost:6379" || echo "   ⚠️  Redis: Check manually"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ StaticWaves Platform Online!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Access your services:"
echo ""
echo "  🛍️  POD Service (Print-on-Demand):"
echo "     http://YOUR_RUNPOD_URL/"
echo ""
echo "  🎮 Forge Service (3D Asset Generation):"
echo "     http://YOUR_RUNPOD_URL/forge/"
echo "     http://YOUR_RUNPOD_URL/forge/docs (API docs)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "View logs:"
echo "  docker-compose -f docker-compose.unified.yml logs -f [service]"
echo ""
echo "Services: pod-service, forge-api, forge-web, forge-worker, redis, nginx"
echo ""

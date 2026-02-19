#!/bin/bash
# StaticWaves Forge Version Rollback Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
GITHUB_REPO="${GITHUB_REPOSITORY:-ssiens-oss/ssiens-oss-static_pod}"

echo -e "${GREEN}🔄 StaticWaves Forge Rollback Tool${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if version is provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: No version specified${NC}"
    echo ""
    echo "Usage: $0 <version>"
    echo "Example: $0 v1.0.0"
    echo ""
    echo "Available versions:"
    docker images "ghcr.io/$GITHUB_REPO/web" --format "{{.Tag}}" | grep -v latest | head -10
    exit 1
fi

VERSION=$1

echo -e "${YELLOW}📋 Rollback Summary${NC}"
echo "  Target Version: $VERSION"
echo "  Repository: $GITHUB_REPO"
echo "  Compose File: $COMPOSE_FILE"
echo ""

# Confirm rollback
read -p "Are you sure you want to rollback to $VERSION? (yes/no): " -r
echo ""
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    echo -e "${YELLOW}⚠️  Rollback cancelled${NC}"
    exit 0
fi

echo -e "${GREEN}🚀 Starting rollback...${NC}"

# Step 1: Export version
export VERSION=$VERSION
export GITHUB_REPOSITORY=$GITHUB_REPO

echo "  ✓ Environment variables set"

# Step 2: Pull images
echo ""
echo -e "${YELLOW}📥 Pulling images for version $VERSION...${NC}"
docker compose -f $COMPOSE_FILE pull
echo "  ✓ Images pulled successfully"

# Step 3: Stop current services
echo ""
echo -e "${YELLOW}🛑 Stopping current services...${NC}"
docker compose -f $COMPOSE_FILE down
echo "  ✓ Services stopped"

# Step 4: Start services with new version
echo ""
echo -e "${YELLOW}▶️  Starting services with version $VERSION...${NC}"
docker compose -f $COMPOSE_FILE up -d
echo "  ✓ Services started"

# Step 5: Wait for health checks
echo ""
echo -e "${YELLOW}🏥 Waiting for health checks...${NC}"
sleep 10

# Check service status
echo ""
echo -e "${GREEN}📊 Service Status:${NC}"
docker compose -f $COMPOSE_FILE ps

# Verify services are healthy
UNHEALTHY=$(docker compose -f $COMPOSE_FILE ps --format json | jq -r 'select(.Health != "healthy" and .Health != "") | .Name' 2>/dev/null || echo "")

if [ -n "$UNHEALTHY" ]; then
    echo ""
    echo -e "${RED}❌ Warning: Some services are unhealthy:${NC}"
    echo "$UNHEALTHY"
    echo ""
    echo "Check logs with: docker compose -f $COMPOSE_FILE logs"
else
    echo ""
    echo -e "${GREEN}✅ Rollback completed successfully!${NC}"
    echo ""
    echo "Services are now running version: $VERSION"
    echo ""
    echo "URLs:"
    echo "  Web UI:  http://localhost:3000"
    echo "  API:     http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

#!/bin/bash
# RunPod Serverless Endpoint Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
export DOCKER_USERNAME=staticwaves
export RUNPOD_API_KEY=rpa_ZLK5MWU94JE5RJLBF7J0GFTKXY6LHPPPJJGRTI0X1q8bte
export PROJECT_NAME=staticwaves-pod-pipeline
export VERSION=latest

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║    StaticWaves - RunPod Serverless Deployment             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed.${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is ready${NC}"
echo ""

# Step 1: Build the serverless image
echo -e "${BLUE}📦 Building serverless Docker image...${NC}"
echo "This may take 5-10 minutes..."
echo ""

docker build \
    -f Dockerfile.serverless \
    -t "${PROJECT_NAME}-serverless:${VERSION}" \
    .

echo ""
echo -e "${GREEN}✅ Image built successfully${NC}"
echo ""

# Step 2: Tag and push to Docker Hub
echo -e "${BLUE}🚀 Pushing to Docker Hub...${NC}"
echo ""

# Login
echo "Please enter your Docker Hub password:"
docker login -u "${DOCKER_USERNAME}"

# Tag
docker tag "${PROJECT_NAME}-serverless:${VERSION}" "${DOCKER_USERNAME}/${PROJECT_NAME}-serverless:${VERSION}"

# Push
docker push "${DOCKER_USERNAME}/${PROJECT_NAME}-serverless:${VERSION}"

echo ""
echo -e "${GREEN}✅ Image pushed to Docker Hub${NC}"
echo ""

# Step 3: Deploy to RunPod Serverless
echo -e "${BLUE}☁️  Creating serverless endpoint...${NC}"
echo ""

# Create serverless endpoint using GraphQL API
RESPONSE=$(curl -s -X POST "https://api.runpod.io/graphql?api_key=${RUNPOD_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
        \"query\": \"mutation { saveEndpoint(input: { name: \\\"${PROJECT_NAME}-serverless\\\", dockerImage: \\\"${DOCKER_USERNAME}/${PROJECT_NAME}-serverless:${VERSION}\\\", gpuIds: \\\"AMPERE_16\\\", networkVolumeId: null, scalerType: \\\"QUEUE_DELAY\\\", scalerValue: 4, workersMin: 0, workersMax: 3 }) { id name } }\"
    }")

echo "API Response:"
echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"

# Check for errors
if echo "$RESPONSE" | grep -q '"errors"'; then
    echo ""
    echo -e "${RED}❌ Deployment may have failed. Check the response above.${NC}"
    echo ""
    echo "Common issues:"
    echo "  • Endpoint might already exist - check RunPod console"
    echo "  • API key might need refresh"
    echo "  • Try deploying manually via RunPod web UI"
else
    echo ""
    echo -e "${GREEN}✅ Serverless endpoint created!${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🚀 Serverless Deployment Complete! 🚀             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Image: ${DOCKER_USERNAME}/${PROJECT_NAME}-serverless:${VERSION}"
echo ""
echo "Next steps:"
echo "  1. Go to https://runpod.io/console/serverless"
echo "  2. Find your endpoint: ${PROJECT_NAME}-serverless"
echo "  3. Get your endpoint ID and URL"
echo "  4. Test with a health check request"
echo ""
echo "Test your endpoint:"
echo "  curl -X POST https://api.runpod.ai/v2/<ENDPOINT_ID>/runsync \\"
echo "    -H 'Authorization: Bearer ${RUNPOD_API_KEY}' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"input\": {\"operation\": \"health\"}}'"
echo ""
echo "Generate a design:"
echo "  curl -X POST https://api.runpod.ai/v2/<ENDPOINT_ID>/runsync \\"
echo "    -H 'Authorization: Bearer ${RUNPOD_API_KEY}' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"input\": {"
echo "      \"operation\": \"generate\","
echo "      \"prompt\": \"Minimalist mountain landscape\","
echo "      \"style\": \"artistic\","
echo "      \"product_type\": \"tshirt\""
echo "    }}'"
echo ""
echo "Serverless Benefits:"
echo "  ✅ Auto-scales from 0 to 3 workers based on demand"
echo "  ✅ Only pay for actual execution time"
echo "  ✅ ~90% cost savings vs continuous pods"
echo "  ✅ Built-in queue management"
echo ""

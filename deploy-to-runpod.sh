#!/bin/bash
# RunPod Serverless Production Deployment Script
# Generated for staticwaves deployment

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
export DEPLOY_TARGET=both
export VERSION=latest
export PROJECT_NAME=staticwaves-pod-pipeline

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║    StaticWaves POD Pipeline - RunPod Deployment            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed.${NC}"
    echo ""
    echo "Please install Docker first:"
    echo "  • macOS: Download from https://www.docker.com/products/docker-desktop"
    echo "  • Linux: Run 'curl -fsSL https://get.docker.com | sh'"
    echo "  • Windows: Download from https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running.${NC}"
    echo "Please start Docker Desktop or run 'sudo systemctl start docker'"
    exit 1
fi

echo -e "${GREEN}✅ Docker is ready${NC}"
echo ""

# Step 1: Build the image
echo -e "${BLUE}📦 Building production Docker image...${NC}"
echo "This may take 5-10 minutes depending on your internet connection..."
echo ""

# Enable BuildKit for modern Docker features (heredoc COPY support)
export DOCKER_BUILDKIT=1

docker build \
    -f Dockerfile.runpod \
    -t "${PROJECT_NAME}:${VERSION}" \
    --build-arg NODE_ENV=production \
    .

echo ""
echo -e "${GREEN}✅ Image built successfully${NC}"
echo ""

# Step 2: Tag and push to Docker Hub
echo -e "${BLUE}🚀 Pushing to Docker Hub...${NC}"
echo "Image: docker.io/${DOCKER_USERNAME}/${PROJECT_NAME}:${VERSION}"
echo ""

# Login to Docker Hub
echo "Please enter your Docker Hub password when prompted:"
docker login -u "${DOCKER_USERNAME}"

# Tag the image
docker tag "${PROJECT_NAME}:${VERSION}" "${DOCKER_USERNAME}/${PROJECT_NAME}:${VERSION}"

# Push to Docker Hub
docker push "${DOCKER_USERNAME}/${PROJECT_NAME}:${VERSION}"

echo ""
echo -e "${GREEN}✅ Image pushed to Docker Hub${NC}"
echo ""

# Step 3: Deploy to RunPod
echo -e "${BLUE}☁️  Deploying to RunPod...${NC}"
echo ""

RESPONSE=$(curl -s -X POST "https://api.runpod.io/v2/pods" \
    -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
        \"cloudType\": \"ALL\",
        \"gpuCount\": 1,
        \"volumeInGb\": 50,
        \"containerDiskInGb\": 50,
        \"minVcpuCount\": 4,
        \"minMemoryInGb\": 16,
        \"gpuTypeId\": \"NVIDIA RTX A4000\",
        \"name\": \"${PROJECT_NAME}-prod\",
        \"imageName\": \"${DOCKER_USERNAME}/${PROJECT_NAME}:${VERSION}\",
        \"dockerArgs\": \"\",
        \"ports\": \"80/http,8188/http,5000/http\",
        \"volumeMountPath\": \"/data\",
        \"env\": []
    }")

# Check for errors
if echo "$RESPONSE" | grep -q '"error"'; then
    echo -e "${RED}❌ RunPod deployment failed${NC}"
    echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ RunPod deployment successful!${NC}"
echo ""

# Parse and display pod information
POD_ID=$(echo "$RESPONSE" | jq -r '.id' 2>/dev/null || echo "unknown")
POD_STATUS=$(echo "$RESPONSE" | jq -r '.status' 2>/dev/null || echo "unknown")

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  🎉 Deployment Complete! 🎉                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Pod Details:"
echo "  • Pod ID: ${POD_ID}"
echo "  • Status: ${POD_STATUS}"
echo "  • Image: ${DOCKER_USERNAME}/${PROJECT_NAME}:${VERSION}"
echo ""
echo "Access your deployment:"
echo "  1. Go to https://runpod.io/console/pods"
echo "  2. Find pod: ${PROJECT_NAME}-prod"
echo "  3. Wait for status to change to 'Running' (usually 2-5 minutes)"
echo "  4. Click 'Connect' to get your access URLs"
echo ""
echo "Expected URLs (once running):"
echo "  • Web UI: https://{pod-id}-80.proxy.runpod.net"
echo "  • ComfyUI: https://{pod-id}-8188.proxy.runpod.net"
echo "  • POD Gateway: https://{pod-id}-5000.proxy.runpod.net"
echo ""
echo "Full API Response:"
echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
echo ""
echo "Next Steps:"
echo "  1. Wait for pod to start (check RunPod console)"
echo "  2. Configure environment variables in the pod"
echo "  3. Upload your API keys and credentials"
echo "  4. Test the pipeline with a sample design"
echo ""
echo "Documentation:"
echo "  • README.md - General overview"
echo "  • PRODUCTION_DEPLOYMENT.md - Production guide"
echo "  • POD_GATEWAY_INTEGRATION.md - Approval workflow"
echo ""

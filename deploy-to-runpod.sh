#!/bin/bash
# Deploy POD Pipeline GUI to RunPod
# This script builds and deploys the complete POD automation stack to RunPod

set -e

echo "🚀 Deploying POD Pipeline GUI to RunPod..."
echo ""

# Configuration
DOCKER_IMAGE="${DOCKER_IMAGE:-staticwaves-pod-pipeline}"
VERSION="${VERSION:-latest}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
DOCKER_USERNAME="${DOCKER_USERNAME}"
RUNPOD_API_KEY="${RUNPOD_API_KEY}"
GPU_TYPE="${GPU_TYPE:-NVIDIA RTX A4000}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check required environment variables
if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${RED}❌ Error: DOCKER_USERNAME not set${NC}"
    echo "Usage: DOCKER_USERNAME=yourname RUNPOD_API_KEY=xxx ./deploy-to-runpod.sh"
    exit 1
fi

if [ -z "$RUNPOD_API_KEY" ]; then
    echo -e "${RED}❌ Error: RUNPOD_API_KEY not set${NC}"
    echo "Get your API key from: https://www.runpod.io/console/user/settings"
    exit 1
fi

# Check Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed${NC}"
    exit 1
fi

# Build Docker image
echo -e "${GREEN}📦 Building Docker image...${NC}"
FULL_IMAGE_NAME="${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${DOCKER_IMAGE}:${VERSION}"
echo "Image: ${FULL_IMAGE_NAME}"
echo ""

docker build -f Dockerfile.runpod -t "${DOCKER_IMAGE}:${VERSION}" .

# Tag for registry
docker tag "${DOCKER_IMAGE}:${VERSION}" "${FULL_IMAGE_NAME}"

# Login to Docker registry
echo ""
echo -e "${GREEN}🔐 Logging in to Docker registry...${NC}"
echo "Please enter your Docker Hub password:"
docker login "${DOCKER_REGISTRY}" -u "${DOCKER_USERNAME}"

# Push to registry
echo ""
echo -e "${GREEN}⬆️  Pushing image to registry...${NC}"
echo "This may take several minutes..."
docker push "${FULL_IMAGE_NAME}"

echo ""
echo -e "${GREEN}✅ Image pushed successfully!${NC}"
echo ""

# Deploy to RunPod
echo -e "${GREEN}🌐 Deploying to RunPod...${NC}"
echo ""

RESPONSE=$(curl -s -X POST "https://api.runpod.io/graphql?api_key=${RUNPOD_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "mutation { podFindAndDeployOnDemand(input: { cloudType: SECURE, gpuTypeId: \"'"${GPU_TYPE}"'\", name: \"pod-pipeline-gui\", imageName: \"'"${FULL_IMAGE_NAME}"'\", dockerArgs: \"\", ports: \"80/http,8080/http,8081/http,8188/http\", volumeInGb: 50, containerDiskInGb: 50, env: [], minVcpuCount: 4, minMemoryInGb: 16 }) { id imageName env machineId machine { podHostId } } }"
    }')

echo "$RESPONSE" | jq '.' || echo "$RESPONSE"

# Extract pod ID
POD_ID=$(echo "$RESPONSE" | jq -r '.data.podFindAndDeployOnDemand.id // empty')

if [ -n "$POD_ID" ]; then
    echo ""
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo ""
    echo "📍 Pod ID: ${POD_ID}"
    echo ""
    echo "🌐 Access your POD Pipeline:"
    echo "   1. Go to: https://www.runpod.io/console/pods"
    echo "   2. Find pod: pod-pipeline-gui"
    echo "   3. Click 'Connect' to get the public URL"
    echo ""
    echo "📱 Your applications will be available at:"
    echo "   - POD Pipeline GUI: https://[your-pod-url]:80"
    echo "   - Original POD Studio: https://[your-pod-url]:8080"
    echo "   - Music Studio: https://[your-pod-url]:8081"
    echo "   - ComfyUI API: https://[your-pod-url]:8188"
    echo ""
    echo -e "${YELLOW}⏳ Note: It may take 2-3 minutes for the pod to fully start${NC}"
else
    echo ""
    echo -e "${RED}❌ Deployment failed!${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

echo ""
echo "🎉 Done!"

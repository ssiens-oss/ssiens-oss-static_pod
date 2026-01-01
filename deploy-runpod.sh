#!/bin/bash
#
# RunPod Deployment Script for StaticWaves POD Studio
# This script builds and deploys the full POD automation system to RunPod
#

set -e

echo "🚀 StaticWaves POD Studio - RunPod Deployment"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOCKER_IMAGE="staticwaves-pod-studio"
DOCKER_TAG="latest"

echo "📋 Step 1: Checking Prerequisites"
echo "-----------------------------------"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ .env file found${NC}"

echo ""
echo "🔨 Step 2: Building Docker Image"
echo "----------------------------------"

# Build Docker image
docker build -f Dockerfile.runpod -t ${DOCKER_IMAGE}:${DOCKER_TAG} . || {
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
}

echo -e "${GREEN}✅ Docker image built successfully${NC}"
IMAGE_SIZE=$(docker images ${DOCKER_IMAGE}:${DOCKER_TAG} --format "{{.Size}}")
echo "   Image size: ${IMAGE_SIZE}"

echo ""
echo "📤 Step 3: Push to Docker Registry"
echo "-----------------------------------"
echo ""
echo "Choose deployment method:"
echo "1) Push to Docker Hub (recommended)"
echo "2) Use RunPod's container registry"
echo "3) Skip push (local testing only)"
read -p "Enter choice [1-3]: " deploy_choice

case $deploy_choice in
    1)
        read -p "Docker Hub username: " docker_user
        echo "Logging into Docker Hub..."
        docker login || exit 1

        echo "Tagging image..."
        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${docker_user}/${DOCKER_IMAGE}:${DOCKER_TAG}

        echo "Pushing to Docker Hub..."
        docker push ${docker_user}/${DOCKER_IMAGE}:${DOCKER_TAG}

        FINAL_IMAGE="${docker_user}/${DOCKER_IMAGE}:${DOCKER_TAG}"
        ;;
    2)
        echo "RunPod container registry setup..."
        read -p "RunPod registry URL: " runpod_registry
        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${runpod_registry}/${DOCKER_IMAGE}:${DOCKER_TAG}
        docker push ${runpod_registry}/${DOCKER_IMAGE}:${DOCKER_TAG}
        FINAL_IMAGE="${runpod_registry}/${DOCKER_IMAGE}:${DOCKER_TAG}"
        ;;
    3)
        echo "Skipping push - local testing mode"
        FINAL_IMAGE="${DOCKER_IMAGE}:${DOCKER_TAG}"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎯 Step 4: RunPod Deployment Instructions"
echo "------------------------------------------"
echo ""
echo "To deploy on RunPod:"
echo ""
echo "1. Go to: https://www.runpod.io/console/pods"
echo ""
echo "2. Click '+ Deploy' and choose:"
echo "   GPU: RTX A4000 (16GB VRAM) or better"
echo "   Disk: 50GB minimum"
echo ""
echo "3. Select 'Custom Docker Image' and enter:"
echo "   ${FINAL_IMAGE}"
echo ""
echo "4. Configure Environment Variables:"
echo "   Copy these from your .env file:"
echo ""

# Extract and display key env vars (without showing secrets)
echo "   ANTHROPIC_API_KEY=sk-ant-***"
echo "   PRINTIFY_API_KEY=***"
echo "   PRINTIFY_SHOP_ID=25860767"
echo "   AUTO_PUBLISH=true"
echo ""

echo "5. Exposed Ports:"
echo "   - 80 (Frontend & API)"
echo "   - 8188 (ComfyUI)"
echo ""

echo "6. Volume Mounts (optional):"
echo "   /data -> Persistent storage for designs"
echo ""

echo "7. Click 'Deploy'"
echo ""
echo "✅ Deployment preparation complete!"
echo ""
echo "📝 Next Steps:"
echo "   1. Deploy the pod on RunPod"
echo "   2. Once running, access the dashboard at: http://<pod-ip>/"
echo "   3. ComfyUI will be available at: http://<pod-ip>:8188"
echo ""
echo "💰 Estimated Cost:"
echo "   RTX A4000: ~$0.39/hour"
echo "   RTX 4090: ~$0.69/hour"
echo "   A100 80GB: ~$1.89/hour"
echo ""

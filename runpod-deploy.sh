#!/bin/bash
set -e

echo "========================================="
echo "StaticWaves POD Studio - RunPod Deploy Script"
echo "========================================="
echo ""

# Configuration
IMAGE_NAME="staticwaves-pod-studio"
TAG="beta"
DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:-your-username}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Building Docker image...${NC}"
docker build -t ${IMAGE_NAME}:${TAG} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Testing image locally...${NC}"
# Start container in background
CONTAINER_ID=$(docker run -d -p 8080:80 ${IMAGE_NAME}:${TAG})

# Wait for container to be ready
sleep 5

# Test health endpoint
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health.json)

if [ "$HEALTH_CHECK" -eq 200 ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed (HTTP ${HEALTH_CHECK})${NC}"
    docker logs $CONTAINER_ID
    docker stop $CONTAINER_ID
    docker rm $CONTAINER_ID
    exit 1
fi

# Stop test container
docker stop $CONTAINER_ID > /dev/null
docker rm $CONTAINER_ID > /dev/null

echo ""
echo -e "${YELLOW}Step 3: Tagging for Docker Hub...${NC}"

# Check if DOCKERHUB_USERNAME is set
if [ "$DOCKERHUB_USERNAME" = "your-username" ]; then
    echo -e "${RED}ERROR: Please set DOCKERHUB_USERNAME environment variable${NC}"
    echo "Usage: DOCKERHUB_USERNAME=your-username ./runpod-deploy.sh"
    exit 1
fi

docker tag ${IMAGE_NAME}:${TAG} ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}
echo -e "${GREEN}✓ Tagged as ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}${NC}"

echo ""
echo -e "${YELLOW}Step 4: Pushing to Docker Hub...${NC}"
echo "This requires Docker Hub login (docker login)"

read -p "Push to Docker Hub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Push successful${NC}"
    else
        echo -e "${RED}✗ Push failed - make sure you're logged in (docker login)${NC}"
        exit 1
    fi
else
    echo "Skipping push"
fi

echo ""
echo "========================================="
echo -e "${GREEN}Deployment Ready!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Go to RunPod Dashboard: https://runpod.io"
echo "2. Navigate to Templates → New Template"
echo "3. Set container image: ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}"
echo "4. Set exposed HTTP port: 80"
echo "5. Add environment variables from .env.example"
echo "6. Deploy your pod!"
echo ""
echo "For detailed instructions, see DEPLOYMENT.md"
echo "========================================="

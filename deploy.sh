#!/bin/bash

# StaticWaves POD Studio - Docker Build and Deploy Script
# This script builds the Docker image and optionally pushes to a registry

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="staticwaves-pod-studio"
VERSION="${1:-latest}"
REGISTRY_TYPE="${2:-dockerhub}"  # dockerhub or ghcr

echo -e "${GREEN}=== StaticWaves POD Studio Deployment ===${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t "${IMAGE_NAME}:${VERSION}" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
fi

# Test the image locally (optional)
echo ""
read -p "Do you want to test the image locally? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Starting container on port 8080...${NC}"
    echo -e "${GREEN}Visit http://localhost:8080 to test${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the test container${NC}"
    docker run --rm -p 8080:80 "${IMAGE_NAME}:${VERSION}"
fi

# Push to registry
echo ""
read -p "Do you want to push to a registry? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ "$REGISTRY_TYPE" = "dockerhub" ]; then
        read -p "Enter your Docker Hub username: " DOCKER_USERNAME
        FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"

        echo -e "${YELLOW}Tagging image for Docker Hub...${NC}"
        docker tag "${IMAGE_NAME}:${VERSION}" "${FULL_IMAGE_NAME}"

        echo -e "${YELLOW}Pushing to Docker Hub...${NC}"
        docker push "${FULL_IMAGE_NAME}"

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Image pushed successfully to Docker Hub${NC}"
            echo -e "${GREEN}Image URL: ${FULL_IMAGE_NAME}${NC}"
            echo ""
            echo -e "${YELLOW}Next steps:${NC}"
            echo "1. Go to https://www.runpod.io/"
            echo "2. Deploy a custom container"
            echo "3. Use image: ${FULL_IMAGE_NAME}"
            echo "4. Expose port 80"
            echo "5. Deploy and access your app!"
        else
            echo -e "${RED}✗ Push failed${NC}"
            exit 1
        fi

    elif [ "$REGISTRY_TYPE" = "ghcr" ]; then
        read -p "Enter your GitHub username: " GITHUB_USERNAME
        FULL_IMAGE_NAME="ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:${VERSION}"

        echo -e "${YELLOW}Tagging image for GitHub Container Registry...${NC}"
        docker tag "${IMAGE_NAME}:${VERSION}" "${FULL_IMAGE_NAME}"

        echo -e "${YELLOW}Note: Make sure you're logged in to GHCR first${NC}"
        echo -e "${YELLOW}Run: echo \$GITHUB_TOKEN | docker login ghcr.io -u ${GITHUB_USERNAME} --password-stdin${NC}"
        echo ""
        read -p "Press enter to continue with push..."

        echo -e "${YELLOW}Pushing to GitHub Container Registry...${NC}"
        docker push "${FULL_IMAGE_NAME}"

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Image pushed successfully to GHCR${NC}"
            echo -e "${GREEN}Image URL: ${FULL_IMAGE_NAME}${NC}"
            echo ""
            echo -e "${YELLOW}Next steps:${NC}"
            echo "1. Make sure the package is public in GitHub"
            echo "2. Go to https://www.runpod.io/"
            echo "3. Deploy a custom container"
            echo "4. Use image: ${FULL_IMAGE_NAME}"
            echo "5. Expose port 80"
            echo "6. Deploy and access your app!"
        else
            echo -e "${RED}✗ Push failed${NC}"
            exit 1
        fi
    fi
fi

echo ""
echo -e "${GREEN}=== Deployment script complete ===${NC}"

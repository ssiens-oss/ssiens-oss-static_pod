#!/bin/bash

# StaticWaves POD Studio - RunPod Deployment Script
# This script builds and deploys the POD Studio to RunPod

set -e

echo "🚀 StaticWaves POD Studio - RunPod Deployment"
echo "=============================================="

# Configuration
IMAGE_NAME="staticwaves-pod-studio"
VERSION="6.0.0"
REGISTRY="${DOCKER_REGISTRY:-docker.io}"
REPOSITORY="${DOCKER_REPOSITORY:-staticwaves}"

FULL_IMAGE_NAME="${REGISTRY}/${REPOSITORY}/${IMAGE_NAME}:${VERSION}"
LATEST_IMAGE_NAME="${REGISTRY}/${REPOSITORY}/${IMAGE_NAME}:latest"

# Step 1: Build Docker image
echo ""
echo "📦 Step 1: Building Docker image..."
docker build \
  --platform linux/amd64 \
  -t ${IMAGE_NAME}:${VERSION} \
  -t ${IMAGE_NAME}:latest \
  -f Dockerfile \
  .

echo "✅ Docker image built successfully"

# Step 2: Tag for registry
echo ""
echo "🏷️  Step 2: Tagging image for registry..."
docker tag ${IMAGE_NAME}:${VERSION} ${FULL_IMAGE_NAME}
docker tag ${IMAGE_NAME}:latest ${LATEST_IMAGE_NAME}

echo "✅ Image tagged: ${FULL_IMAGE_NAME}"
echo "✅ Image tagged: ${LATEST_IMAGE_NAME}"

# Step 3: Push to registry (if logged in)
echo ""
echo "📤 Step 3: Pushing to registry..."
if docker info | grep -q "Username"; then
    docker push ${FULL_IMAGE_NAME}
    docker push ${LATEST_IMAGE_NAME}
    echo "✅ Image pushed to registry"
else
    echo "⚠️  Not logged into Docker registry. Skipping push."
    echo "   Run: docker login ${REGISTRY}"
fi

# Step 4: Display deployment info
echo ""
echo "✅ Deployment preparation complete!"
echo ""
echo "📋 Next Steps:"
echo "=============="
echo "1. Log into RunPod: https://runpod.io"
echo "2. Navigate to 'My Pods' → 'Deploy'"
echo "3. Use custom Docker image: ${FULL_IMAGE_NAME}"
echo "4. Set container port: 80"
echo "5. Enable HTTP port exposure"
echo "6. Deploy and access via provided URL"
echo ""
echo "🌐 Health Check: http://your-pod-url/health"
echo "🏠 Application: http://your-pod-url/"
echo ""
echo "For detailed instructions, see: docs/RUNPOD_DEPLOYMENT.md"

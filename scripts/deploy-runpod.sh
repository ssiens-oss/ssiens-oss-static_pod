#!/bin/bash
# Deploy POD Pipeline to RunPod

set -e

echo "🚀 Deploying POD Pipeline to RunPod..."

# Configuration
DOCKER_IMAGE="${DOCKER_IMAGE:-staticwaves-pod-pipeline:latest}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
DOCKER_USERNAME="${DOCKER_USERNAME}"
RUNPOD_API_KEY="${RUNPOD_API_KEY}"

# Check required environment variables
if [ -z "$DOCKER_USERNAME" ]; then
    echo "❌ Error: DOCKER_USERNAME not set"
    echo "Usage: DOCKER_USERNAME=yourname RUNPOD_API_KEY=xxx ./scripts/deploy-runpod.sh"
    exit 1
fi

if [ -z "$RUNPOD_API_KEY" ]; then
    echo "❌ Error: RUNPOD_API_KEY not set"
    exit 1
fi

# Build Docker image
echo "📦 Building Docker image..."
docker build -f Dockerfile.runpod -t "${DOCKER_IMAGE}" .

# Tag for registry
REGISTRY_IMAGE="${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${DOCKER_IMAGE}"
docker tag "${DOCKER_IMAGE}" "${REGISTRY_IMAGE}"

# Login to Docker registry
echo "🔐 Logging in to Docker registry..."
docker login "${DOCKER_REGISTRY}" -u "${DOCKER_USERNAME}"

# Push to registry
echo "⬆️  Pushing image to registry..."
docker push "${REGISTRY_IMAGE}"

echo "✅ Image pushed: ${REGISTRY_IMAGE}"

# Deploy to RunPod
echo "🌐 Deploying to RunPod..."
curl -X POST "https://api.runpod.io/v1/pods" \
    -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{
        "cloudType": "ALL",
        "gpuCount": 1,
        "volumeInGb": 50,
        "containerDiskInGb": 50,
        "minVcpuCount": 4,
        "minMemoryInGb": 16,
        "gpuTypeId": "NVIDIA RTX A4000",
        "name": "pod-pipeline-studio",
        "imageName": "'"${REGISTRY_IMAGE}"'",
        "dockerArgs": "",
        "ports": "80/http,8188/http",
        "volumeMountPath": "/data",
        "env": []
    }'

echo ""
echo "✅ Deployment initiated!"
echo "Check RunPod dashboard for deployment status"

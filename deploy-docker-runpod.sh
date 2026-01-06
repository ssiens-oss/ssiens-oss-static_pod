#!/bin/bash
# Deploy StaticWaves POD Studio to RunPod via Docker
set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║  StaticWaves → RunPod Docker Deployment          ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Configuration
RUNPOD_API_KEY="rpa_ZLK5MWU94JE5RJLBF7J0GFTKXY6LHPPPJJGRTI0X1q8bte"
DOCKER_USERNAME="${DOCKER_USERNAME:-staticwaves}"
IMAGE_NAME="staticwaves-pod-studio"
IMAGE_TAG="latest"
REGISTRY_IMAGE="${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

# Step 1: Build Docker Image
echo "📦 Building Docker image..."
docker build -f Dockerfile.runpod -t "${IMAGE_NAME}:${IMAGE_TAG}" .

# Step 2: Tag for Registry
echo "🏷️  Tagging image for Docker Hub..."
docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${REGISTRY_IMAGE}"

# Step 3: Login to Docker Hub (if needed)
echo "🔐 Docker Hub login..."
echo "Please login to Docker Hub when prompted"
docker login

# Step 4: Push to Docker Hub
echo "⬆️  Pushing to Docker Hub..."
docker push "${REGISTRY_IMAGE}"

echo "✅ Image pushed: ${REGISTRY_IMAGE}"
echo ""

# Step 5: Deploy to RunPod
echo "🚀 Creating RunPod pod..."

RESPONSE=$(curl -s -X POST "https://api.runpod.io/graphql?api_key=${RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { podFindAndDeployOnDemand(input: { cloudType: ALL, gpuCount: 1, volumeInGb: 50, containerDiskInGb: 50, minVcpuCount: 4, minMemoryInGb: 16, gpuTypeId: \"NVIDIA RTX A4000\", name: \"staticwaves-pod-studio\", imageName: \"'"${REGISTRY_IMAGE}"'\", dockerArgs: \"\", ports: \"5173/http,8188/http,80/http\", volumeMountPath: \"/data\", env: [] }) { id imageName env machineId machine { podHostId } } }"
  }')

echo ""
echo "📡 RunPod Response:"
echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"

POD_ID=$(echo "$RESPONSE" | jq -r '.data.podFindAndDeployOnDemand.id // empty' 2>/dev/null)

if [ -n "$POD_ID" ]; then
  echo ""
  echo "╔════════════════════════════════════════════════════╗"
  echo "║  ✅ Deployment Successful!                        ║"
  echo "╚════════════════════════════════════════════════════╝"
  echo ""
  echo "Pod ID: $POD_ID"
  echo ""
  echo "📍 Access your pod:"
  echo "   1. Go to https://www.runpod.io/console/pods"
  echo "   2. Find pod: staticwaves-pod-studio"
  echo "   3. Click 'Connect' to get the public URL"
  echo ""
  echo "🌐 Your app will be available at:"
  echo "   https://<pod-id>-5173.proxy.runpod.net"
  echo ""
  echo "🎨 ComfyUI will be available at:"
  echo "   https://<pod-id>-8188.proxy.runpod.net"
else
  echo ""
  echo "❌ Deployment failed. Check the response above for errors."
  echo ""
  echo "Common issues:"
  echo "  - Invalid API key"
  echo "  - Insufficient RunPod credits"
  echo "  - No available GPUs"
  exit 1
fi

#!/bin/bash
# Flexible RunPod deployment - tries multiple GPU types
set -e

echo "🚀 Flexible RunPod Deployment for POD Pipeline GUI"
echo ""

# Configuration
DOCKER_IMAGE="${DOCKER_IMAGE:-staticwaves-pod-pipeline}"
VERSION="${VERSION:-latest}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
DOCKER_USERNAME="${DOCKER_USERNAME:-staticwaves}"
RUNPOD_API_KEY="${RUNPOD_API_KEY}"

# GPU types to try (in order of preference)
GPU_TYPES=(
    "NVIDIA RTX A4000"
    "NVIDIA RTX A5000"
    "NVIDIA RTX A6000"
    "NVIDIA RTX 3090"
    "NVIDIA RTX 4090"
)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ -z "$RUNPOD_API_KEY" ]; then
    echo -e "${RED}❌ Error: RUNPOD_API_KEY not set${NC}"
    exit 1
fi

FULL_IMAGE_NAME="${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${DOCKER_IMAGE}:${VERSION}"

echo -e "${GREEN}📦 Using Docker image: ${FULL_IMAGE_NAME}${NC}"
echo ""

# Try each GPU type
for GPU_TYPE in "${GPU_TYPES[@]}"; do
    echo -e "${YELLOW}🔍 Trying GPU type: ${GPU_TYPE}${NC}"

    RESPONSE=$(curl -s -X POST "https://api.runpod.io/graphql?api_key=${RUNPOD_API_KEY}" \
        -H "Content-Type: application/json" \
        -d '{
            "query": "mutation { podFindAndDeployOnDemand(input: { cloudType: SECURE, gpuTypeId: \"'"${GPU_TYPE}"'\", name: \"pod-pipeline-gui\", imageName: \"'"${FULL_IMAGE_NAME}"'\", dockerArgs: \"\", ports: \"80/http,8080/http,8081/http,8188/http\", volumeInGb: 50, containerDiskInGb: 50, env: [], minVcpuCount: 4, minMemoryInGb: 16 }) { id imageName env machineId machine { podHostId } } }"
        }')

    # Check if successful
    POD_ID=$(echo "$RESPONSE" | jq -r '.data.podFindAndDeployOnDemand.id // empty' 2>/dev/null)

    if [ -n "$POD_ID" ]; then
        echo ""
        echo -e "${GREEN}✅ Deployment successful with ${GPU_TYPE}!${NC}"
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
        exit 0
    else
        echo -e "${YELLOW}⚠️  ${GPU_TYPE} not available, trying next...${NC}"
    fi
done

# If we get here, all GPU types failed
echo ""
echo -e "${RED}❌ No GPU instances available${NC}"
echo ""
echo "Suggestions:"
echo "  1. Try again in 10-15 minutes (peak hours)"
echo "  2. Check RunPod status: https://status.runpod.io"
echo "  3. Use Community Cloud (cheaper, less availability)"
echo "  4. Run locally without GPU for testing"
echo ""
exit 1

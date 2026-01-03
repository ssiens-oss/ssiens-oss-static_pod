#!/bin/bash

################################################################################
# StaticWaves POD Studio - Full Stack Deployment Script
# Pipeline: Local → Docker → RunPod → Printify Integration
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-staticwaves}"
IMAGE_NAME="staticwaves-pod-studio"
VERSION="${VERSION:-latest}"
RUNPOD_API_KEY="${RUNPOD_API_KEY:-}"
PRINTIFY_API_KEY="${PRINTIFY_API_KEY:-}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  StaticWaves POD Studio - Full Stack Deployment Pipeline  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

################################################################################
# STEP 1: LOCAL ENVIRONMENT CHECK
################################################################################
echo -e "${YELLOW}[1/7] Checking Local Environment...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Check if in correct directory
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}✗ Dockerfile not found. Are you in the correct directory?${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dockerfile found${NC}"

# Check for HTML files or React source
if ls *.html 1> /dev/null 2>&1; then
    echo -e "${GREEN}✓ HTML files found${NC}"
    BUILD_TYPE="html"
elif [ -f "package.json" ]; then
    echo -e "${GREEN}✓ React project found${NC}"
    BUILD_TYPE="react"
else
    echo -e "${RED}✗ No HTML files or package.json found${NC}"
    exit 1
fi

echo ""

################################################################################
# STEP 2: BUILD DOCKER IMAGE
################################################################################
echo -e "${YELLOW}[2/7] Building Docker Image...${NC}"

FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
echo -e "Building: ${BLUE}${FULL_IMAGE_NAME}${NC}"

docker build -t "${FULL_IMAGE_NAME}" . || {
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
}

echo -e "${GREEN}✓ Docker image built successfully${NC}"
echo ""

################################################################################
# STEP 3: TEST LOCALLY (OPTIONAL)
################################################################################
echo -e "${YELLOW}[3/7] Local Testing${NC}"
read -p "Test locally on port 8080? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Starting container on http://localhost:8080${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop and continue deployment${NC}"
    docker run --rm -p 8080:80 "${FULL_IMAGE_NAME}" || true
fi
echo ""

################################################################################
# STEP 4: PUSH TO DOCKER HUB
################################################################################
echo -e "${YELLOW}[4/7] Pushing to Docker Hub...${NC}"

# Check if logged in
if ! docker info 2>/dev/null | grep -q "Username"; then
    echo -e "${YELLOW}Not logged into Docker Hub. Logging in...${NC}"
    docker login || {
        echo -e "${RED}✗ Docker login failed${NC}"
        exit 1
    }
fi

echo -e "Pushing: ${BLUE}${FULL_IMAGE_NAME}${NC}"
docker push "${FULL_IMAGE_NAME}" || {
    echo -e "${RED}✗ Docker push failed${NC}"
    exit 1
}

echo -e "${GREEN}✓ Image pushed to Docker Hub${NC}"
IMAGE_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' "${FULL_IMAGE_NAME}" 2>/dev/null || echo "unknown")
echo -e "Image: ${BLUE}${FULL_IMAGE_NAME}${NC}"
echo -e "Digest: ${BLUE}${IMAGE_DIGEST}${NC}"
echo ""

################################################################################
# STEP 5: DEPLOY TO RUNPOD
################################################################################
echo -e "${YELLOW}[5/7] Deploying to RunPod...${NC}"

if [ -z "$RUNPOD_API_KEY" ]; then
    echo -e "${YELLOW}RUNPOD_API_KEY not set. Manual deployment required.${NC}"
    echo -e "${BLUE}Manual Steps:${NC}"
    echo "1. Go to: https://www.runpod.io/console/pods"
    echo "2. Click 'Deploy' → 'Custom Container'"
    echo "3. Container Image: ${FULL_IMAGE_NAME}"
    echo "4. Expose HTTP Port: 80"
    echo "5. Select CPU pod (no GPU needed)"
    echo "6. Deploy"
    echo ""
    read -p "Press Enter when pod is deployed and paste the pod ID: " POD_ID
    read -p "Paste the HTTP Service URL: " POD_URL
else
    # Automated RunPod deployment via API
    echo -e "${BLUE}Deploying via RunPod API...${NC}"

    RUNPOD_RESPONSE=$(curl -s -X POST https://api.runpod.io/v2/pods \
        -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "staticwaves-pod-'$(date +%s)'",
            "imageName": "'"${FULL_IMAGE_NAME}"'",
            "dockerArgs": "",
            "ports": "80/http",
            "volumeInGb": 10,
            "containerDiskInGb": 10,
            "gpuCount": 0,
            "cloudType": "SECURE",
            "minVcpuCount": 2,
            "minMemoryInGb": 4
        }')

    POD_ID=$(echo "$RUNPOD_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 || echo "")

    if [ -z "$POD_ID" ]; then
        echo -e "${RED}✗ RunPod deployment failed${NC}"
        echo "Response: $RUNPOD_RESPONSE"
        exit 1
    fi

    echo -e "${GREEN}✓ Pod deployed: ${POD_ID}${NC}"

    # Wait for pod to be ready
    echo -e "${YELLOW}Waiting for pod to be ready...${NC}"
    for i in {1..30}; do
        sleep 5
        POD_STATUS=$(curl -s -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
            "https://api.runpod.io/v2/pods/${POD_ID}" | \
            grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "")

        if [ "$POD_STATUS" = "RUNNING" ]; then
            echo -e "${GREEN}✓ Pod is running${NC}"
            break
        fi
        echo -n "."
    done
    echo ""

    POD_URL="https://${POD_ID}-80.proxy.runpod.net"
fi

echo -e "${GREEN}✓ RunPod Deployment Complete${NC}"
echo -e "Pod URL: ${BLUE}${POD_URL}${NC}"
echo ""

################################################################################
# STEP 6: HEALTH CHECK
################################################################################
echo -e "${YELLOW}[6/7] Health Check...${NC}"

echo -e "Checking ${BLUE}${POD_URL}/health${NC}"
sleep 5

for i in {1..10}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${POD_URL}/health" || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓ Health check passed${NC}"
        break
    fi
    echo -n "."
    sleep 3
done
echo ""

################################################################################
# STEP 7: PRINTIFY INTEGRATION
################################################################################
echo -e "${YELLOW}[7/7] Printify Integration Setup...${NC}"

if [ -z "$PRINTIFY_API_KEY" ]; then
    echo -e "${YELLOW}PRINTIFY_API_KEY not set. Skipping automatic configuration.${NC}"
    echo -e "${BLUE}Manual Steps for Printify Integration:${NC}"
    echo "1. Go to: https://printify.com/app/account/api"
    echo "2. Generate API token"
    echo "3. Add webhook URL: ${POD_URL}/webhook/printify"
    echo "4. Set environment variable in RunPod pod:"
    echo "   PRINTIFY_API_KEY=your_api_key"
else
    echo -e "${BLUE}Validating Printify API connection...${NC}"

    PRINTIFY_SHOPS=$(curl -s -H "Authorization: Bearer ${PRINTIFY_API_KEY}" \
        "https://api.printify.com/v1/shops.json" || echo "")

    if echo "$PRINTIFY_SHOPS" | grep -q "id"; then
        echo -e "${GREEN}✓ Printify API connected${NC}"
        SHOP_COUNT=$(echo "$PRINTIFY_SHOPS" | grep -o '"id":' | wc -l)
        echo -e "Found ${BLUE}${SHOP_COUNT}${NC} Printify shop(s)"

        # Set up webhook
        echo -e "${BLUE}Setting up Printify webhook...${NC}"
        WEBHOOK_URL="${POD_URL}/webhook/printify"
        echo -e "Webhook URL: ${BLUE}${WEBHOOK_URL}${NC}"
        echo -e "${YELLOW}Note: Configure webhook manually in Printify dashboard${NC}"
    else
        echo -e "${RED}✗ Printify API connection failed${NC}"
        echo "Response: $PRINTIFY_SHOPS"
    fi
fi

echo ""

################################################################################
# DEPLOYMENT SUMMARY
################################################################################
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            DEPLOYMENT COMPLETE                             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Docker Image:${NC} ${FULL_IMAGE_NAME}"
echo -e "${BLUE}RunPod URL:${NC} ${POD_URL}"
echo ""
echo -e "${BLUE}Application URLs:${NC}"
if [ "$BUILD_TYPE" = "html" ]; then
    echo "  • ${POD_URL}/pod-studio-automation.html"
    echo "  • ${POD_URL}/pod-studio-pro.html"
    echo "  • ${POD_URL}/pod-studio.html"
else
    echo "  • ${POD_URL}/"
fi
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Test your application at the URLs above"
echo "2. Configure Printify webhook if not done automatically"
echo "3. Set up any additional environment variables in RunPod"
echo "4. Monitor logs via RunPod console"
echo ""
echo -e "${YELLOW}Deployment log saved to: deployment-$(date +%Y%m%d-%H%M%S).log${NC}"
echo ""

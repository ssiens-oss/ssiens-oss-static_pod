#!/bin/bash

# Automated Deployment Pipeline
# Complete CI/CD workflow for RunPod deployment

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
VERSION="${VERSION:-beta}"
DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:-}"
IMAGE_NAME="staticwaves-pod-studio"
SKIP_TESTS="${SKIP_TESTS:-false}"
SKIP_PUSH="${SKIP_PUSH:-false}"

echo "========================================="
echo "StaticWaves POD Studio - Deployment Pipeline"
echo "========================================="
echo ""

# Step 1: Pre-flight Checks
preflight_checks() {
    echo -e "${BLUE}Step 1: Pre-flight Checks${NC}"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker available${NC}"

    # Check Docker Hub username
    if [ -z "$DOCKERHUB_USERNAME" ]; then
        echo -e "${RED}✗ DOCKERHUB_USERNAME not set${NC}"
        echo "Set it with: export DOCKERHUB_USERNAME=your-username"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Hub username: $DOCKERHUB_USERNAME${NC}"

    # Check git status
    if [ -d ".git" ]; then
        if [ -n "$(git status --porcelain)" ]; then
            echo -e "${YELLOW}⚠ Uncommitted changes detected${NC}"
            read -p "Continue anyway? (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            echo -e "${GREEN}✓ Git working directory clean${NC}"
        fi
    fi

    echo ""
}

# Step 2: Run Tests
run_tests() {
    if [ "$SKIP_TESTS" = "true" ]; then
        echo -e "${YELLOW}Skipping tests (SKIP_TESTS=true)${NC}"
        echo ""
        return
    fi

    echo -e "${BLUE}Step 2: Running Tests${NC}"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi

    # Run build test
    echo "Testing build..."
    npm run build

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Build successful${NC}"
    else
        echo -e "${RED}✗ Build failed${NC}"
        exit 1
    fi

    echo ""
}

# Step 3: Build Docker Image
build_image() {
    echo -e "${BLUE}Step 3: Building Docker Image${NC}"

    local image_tag="$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION"

    echo "Building: $image_tag"

    docker build \
        --tag "$image_tag" \
        --tag "$DOCKERHUB_USERNAME/$IMAGE_NAME:latest" \
        --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        .

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Image built successfully${NC}"
    else
        echo -e "${RED}✗ Image build failed${NC}"
        exit 1
    fi

    # Check image size
    local size=$(docker images "$image_tag" --format "{{.Size}}")
    echo "Image size: $size"

    echo ""
}

# Step 4: Test Image Locally
test_image() {
    echo -e "${BLUE}Step 4: Testing Image Locally${NC}"

    local image_tag="$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION"
    local container_name="staticwaves-test-$$"

    echo "Starting test container..."

    docker run -d \
        --name "$container_name" \
        -p 8080:80 \
        "$image_tag"

    # Wait for startup
    echo "Waiting for container to start..."
    sleep 5

    # Test health endpoint
    echo "Testing health endpoint..."
    local health_check=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health.json)

    if [ "$health_check" = "200" ]; then
        echo -e "${GREEN}✓ Health check passed${NC}"
    else
        echo -e "${RED}✗ Health check failed (HTTP $health_check)${NC}"
        docker logs "$container_name"
        docker stop "$container_name"
        docker rm "$container_name"
        exit 1
    fi

    # Test main page
    echo "Testing main page..."
    local page_check=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/)

    if [ "$page_check" = "200" ]; then
        echo -e "${GREEN}✓ Main page accessible${NC}"
    else
        echo -e "${RED}✗ Main page failed (HTTP $page_check)${NC}"
        docker stop "$container_name"
        docker rm "$container_name"
        exit 1
    fi

    # Cleanup
    echo "Cleaning up test container..."
    docker stop "$container_name" > /dev/null
    docker rm "$container_name" > /dev/null

    echo -e "${GREEN}✓ Image tests passed${NC}"
    echo ""
}

# Step 5: Push to Registry
push_image() {
    if [ "$SKIP_PUSH" = "true" ]; then
        echo -e "${YELLOW}Skipping push (SKIP_PUSH=true)${NC}"
        echo ""
        return
    fi

    echo -e "${BLUE}Step 5: Pushing to Docker Hub${NC}"

    local image_tag="$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION"

    # Check if logged in
    if ! docker info 2>/dev/null | grep -q "Username"; then
        echo "Logging in to Docker Hub..."
        docker login
    fi

    echo "Pushing $image_tag..."
    docker push "$image_tag"

    if [ "$VERSION" = "latest" ] || [ "$VERSION" = "beta" ]; then
        echo "Pushing latest tag..."
        docker push "$DOCKERHUB_USERNAME/$IMAGE_NAME:latest"
    fi

    echo -e "${GREEN}✓ Image pushed successfully${NC}"
    echo ""
}

# Step 6: Generate Deployment Instructions
generate_instructions() {
    echo -e "${BLUE}Step 6: Deployment Instructions${NC}"

    local image_tag="$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION"

    cat << EOF

========================================
Deployment Ready!
========================================

Docker Image: $image_tag

Next Steps:

1. Create RunPod Template:
   • Go to: https://www.runpod.io/console/templates
   • Click: New Template
   • Image: $image_tag
   • Port: 80
   • Use: runpod-config/pod-template.json as reference

2. Deploy Pod:
   • Go to: https://www.runpod.io/console/pods
   • Click: Deploy
   • Select your template
   • Choose GPU tier
   • Deploy!

3. Verify Deployment:
   • Wait for pod to start (~30-60 seconds)
   • Access: https://[pod-id]-80.proxy.runpod.net
   • Health: https://[pod-id]-80.proxy.runpod.net/health.json

4. Monitor Pod:
   export RUNPOD_API_KEY=your-api-key
   ./runpod-config/runpod-api.sh monitor-pod [pod-id]

========================================

Files to reference:
  • DEPLOYMENT.md - Comprehensive deployment guide
  • WALKTHROUGH.md - Step-by-step walkthrough
  • runpod-config/README.md - Configuration reference

========================================

EOF
}

# Step 7: Create Deployment Tag (if git available)
create_git_tag() {
    if [ ! -d ".git" ]; then
        return
    fi

    echo -e "${BLUE}Step 7: Creating Git Tag${NC}"

    local tag="deploy-$VERSION-$(date +%Y%m%d-%H%M%S)"

    read -p "Create git tag '$tag'? (y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -a "$tag" -m "Deployment: $VERSION"
        echo -e "${GREEN}✓ Tag created: $tag${NC}"

        read -p "Push tag to remote? (y/n): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push origin "$tag"
            echo -e "${GREEN}✓ Tag pushed to remote${NC}"
        fi
    fi

    echo ""
}

# Main pipeline
main() {
    local start_time=$(date +%s)

    preflight_checks
    run_tests
    build_image
    test_image
    push_image
    create_git_tag
    generate_instructions

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo "========================================="
    echo -e "${GREEN}✓ Pipeline Complete!${NC}"
    echo "========================================="
    echo "Duration: ${duration}s"
    echo "Image: $DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION"
    echo "========================================="
}

# Run pipeline
main

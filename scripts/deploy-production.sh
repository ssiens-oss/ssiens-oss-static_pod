#!/bin/bash
# Production Deployment Script for POD Pipeline
# Supports Docker Hub, GHCR, and RunPod deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="${PROJECT_NAME:-staticwaves-pod-pipeline}"
VERSION="${VERSION:-latest}"
DOCKER_USERNAME="${DOCKER_USERNAME}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
RUNPOD_API_KEY="${RUNPOD_API_KEY}"
DEPLOY_TARGET="${DEPLOY_TARGET:-docker}"  # docker, runpod, or both

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi

    log_success "All prerequisites met"
}

validate_environment() {
    log_info "Validating environment variables..."

    local has_error=0

    if [ -z "$DOCKER_USERNAME" ]; then
        log_error "DOCKER_USERNAME is not set"
        has_error=1
    fi

    if [ "$DEPLOY_TARGET" == "runpod" ] || [ "$DEPLOY_TARGET" == "both" ]; then
        if [ -z "$RUNPOD_API_KEY" ]; then
            log_error "RUNPOD_API_KEY is required for RunPod deployment"
            has_error=1
        fi
    fi

    if [ $has_error -eq 1 ]; then
        echo ""
        log_info "Required environment variables:"
        echo "  DOCKER_USERNAME    - Your Docker Hub or registry username"
        echo "  RUNPOD_API_KEY     - Your RunPod API key (for RunPod deployment)"
        echo ""
        log_info "Optional environment variables:"
        echo "  VERSION            - Image version tag (default: latest)"
        echo "  DOCKER_REGISTRY    - Docker registry (default: docker.io)"
        echo "  DEPLOY_TARGET      - Deployment target: docker, runpod, or both (default: docker)"
        echo ""
        log_info "Example usage:"
        echo "  DOCKER_USERNAME=myuser RUNPOD_API_KEY=xxx DEPLOY_TARGET=both ./scripts/deploy-production.sh"
        exit 1
    fi

    log_success "Environment validated"
}

build_production() {
    log_info "Building production image..."

    # Build the image
    docker build \
        -f Dockerfile.runpod \
        -t "${PROJECT_NAME}:${VERSION}" \
        --build-arg NODE_ENV=production \
        .

    log_success "Image built: ${PROJECT_NAME}:${VERSION}"
}

tag_and_push() {
    log_info "Tagging and pushing image to ${DOCKER_REGISTRY}..."

    local registry_image="${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${PROJECT_NAME}:${VERSION}"

    # Tag the image
    docker tag "${PROJECT_NAME}:${VERSION}" "${registry_image}"
    log_success "Image tagged: ${registry_image}"

    # Login to registry
    log_info "Logging in to ${DOCKER_REGISTRY}..."
    docker login "${DOCKER_REGISTRY}" -u "${DOCKER_USERNAME}"

    # Push to registry
    log_info "Pushing image..."
    docker push "${registry_image}"

    log_success "Image pushed to registry"
    echo "📦 Image: ${registry_image}"
}

deploy_runpod() {
    log_info "Deploying to RunPod..."

    local registry_image="${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${PROJECT_NAME}:${VERSION}"

    # Create the deployment
    local response=$(curl -s -X POST "https://api.runpod.io/v2/pods" \
        -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{
            \"cloudType\": \"ALL\",
            \"gpuCount\": 1,
            \"volumeInGb\": 50,
            \"containerDiskInGb\": 50,
            \"minVcpuCount\": 4,
            \"minMemoryInGb\": 16,
            \"gpuTypeId\": \"NVIDIA RTX A4000\",
            \"name\": \"${PROJECT_NAME}-${VERSION}\",
            \"imageName\": \"${registry_image}\",
            \"dockerArgs\": \"\",
            \"ports\": \"80/http,8188/http,5000/http\",
            \"volumeMountPath\": \"/data\",
            \"env\": []
        }")

    # Check for errors
    if echo "$response" | grep -q "error"; then
        log_error "RunPod deployment failed"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
        exit 1
    fi

    log_success "RunPod deployment initiated"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo ""
    log_info "Check your RunPod dashboard for deployment status"
}

test_local() {
    log_info "Testing image locally..."

    # Stop any existing container
    docker stop "${PROJECT_NAME}-test" 2>/dev/null || true
    docker rm "${PROJECT_NAME}-test" 2>/dev/null || true

    # Run the container
    log_info "Starting container on port 8080..."
    docker run -d \
        --name "${PROJECT_NAME}-test" \
        -p 8080:80 \
        -p 8188:8188 \
        "${PROJECT_NAME}:${VERSION}"

    # Wait for container to be ready
    log_info "Waiting for services to start..."
    sleep 10

    # Test health endpoint
    if curl -sf http://localhost:8080/health > /dev/null; then
        log_success "Health check passed"
        echo ""
        log_success "Test deployment running at http://localhost:8080"
        log_info "ComfyUI API available at http://localhost:8188"
        echo ""
        log_info "To stop the test deployment:"
        echo "  docker stop ${PROJECT_NAME}-test && docker rm ${PROJECT_NAME}-test"
    else
        log_error "Health check failed"
        log_info "Container logs:"
        docker logs "${PROJECT_NAME}-test"
        exit 1
    fi
}

print_summary() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║          🚀 Production Deployment Complete! 🚀              ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Image: ${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${PROJECT_NAME}:${VERSION}"
    echo ""
    echo "Next steps:"
    echo "  1. Monitor your deployment in the RunPod dashboard"
    echo "  2. Access the web UI via the RunPod provided URL"
    echo "  3. Configure your .env variables in the pod"
    echo "  4. Test the pipeline with a sample design"
    echo ""
    echo "Documentation: README.md, DEPLOYMENT.md"
    echo ""
}

# Main execution
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║       POD Pipeline Production Deployment Script            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    check_prerequisites
    validate_environment

    # Build
    build_production

    # Test locally (optional)
    if [ "${TEST_LOCAL}" == "true" ]; then
        test_local
        read -p "Continue with deployment? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_warning "Deployment cancelled"
            exit 0
        fi
    fi

    # Deploy based on target
    if [ "$DEPLOY_TARGET" == "docker" ] || [ "$DEPLOY_TARGET" == "both" ]; then
        tag_and_push
    fi

    if [ "$DEPLOY_TARGET" == "runpod" ] || [ "$DEPLOY_TARGET" == "both" ]; then
        deploy_runpod
    fi

    print_summary
}

# Run main
main

#!/bin/bash

# Local Docker Testing Script for POD Studio

set -e

echo "🧪 Testing POD Studio Docker Build Locally"
echo "=========================================="

IMAGE_NAME="staticwaves-pod-studio"
CONTAINER_NAME="pod-studio-test"
PORT="8080"

# Step 1: Build image
echo ""
echo "📦 Building Docker image..."
docker build -t ${IMAGE_NAME}:test .

echo "✅ Build successful"

# Step 2: Stop existing container
echo ""
echo "🧹 Cleaning up existing containers..."
docker rm -f ${CONTAINER_NAME} 2>/dev/null || true

# Step 3: Run container
echo ""
echo "🚀 Starting container on port ${PORT}..."
docker run -d \
  --name ${CONTAINER_NAME} \
  -p ${PORT}:80 \
  ${IMAGE_NAME}:test

# Step 4: Wait for container to be ready
echo ""
echo "⏳ Waiting for container to be ready..."
sleep 3

# Step 5: Health check
echo ""
echo "🏥 Running health check..."
if curl -sf http://localhost:${PORT}/health > /dev/null; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    docker logs ${CONTAINER_NAME}
    exit 1
fi

# Step 6: Test main page
echo ""
echo "🌐 Testing main page..."
if curl -sf http://localhost:${PORT}/ > /dev/null; then
    echo "✅ Main page accessible"
else
    echo "❌ Main page failed"
    docker logs ${CONTAINER_NAME}
    exit 1
fi

# Success message
echo ""
echo "✅ All tests passed!"
echo ""
echo "🌐 Application running at: http://localhost:${PORT}"
echo "🏥 Health check at: http://localhost:${PORT}/health"
echo ""
echo "To view logs: docker logs ${CONTAINER_NAME}"
echo "To stop: docker stop ${CONTAINER_NAME}"
echo "To remove: docker rm ${CONTAINER_NAME}"
echo ""
echo "Press Ctrl+C to exit (container will keep running)"

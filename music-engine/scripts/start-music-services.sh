#!/bin/bash

# StaticWaves Music Engine - Start Script
# This script starts all music generation services

set -e

echo "🎵 Starting StaticWaves Music Engine..."
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Navigate to music-engine directory
cd "$(dirname "$0")/.."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp ../.env.example .env
    echo "⚠️  Please edit .env with your configuration before running in production"
fi

# Pull latest images (optional)
if [ "$1" == "--pull" ]; then
    echo "📥 Pulling latest images..."
    docker-compose pull
fi

# Start services
echo "🚀 Starting services with docker-compose..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check health
echo ""
echo "🏥 Health Check:"
echo "================"

# Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Running"
else
    echo "❌ Redis: Not responding"
fi

# API
API_HEALTH=$(curl -s http://localhost:8000/health || echo "failed")
if echo "$API_HEALTH" | grep -q "healthy"; then
    echo "✅ Music API: Running (http://localhost:8000)"
else
    echo "❌ Music API: Not responding"
fi

# Worker
if docker-compose ps | grep -q "music-worker.*Up"; then
    echo "✅ Music Worker: Running"
else
    echo "❌ Music Worker: Not running"
fi

echo ""
echo "======================================"
echo "🎉 StaticWaves Music Engine Started!"
echo ""
echo "API Docs: http://localhost:8000/docs"
echo "Health:   http://localhost:8000/health"
echo ""
echo "View logs:  docker-compose logs -f"
echo "Stop:       docker-compose down"
echo "======================================"

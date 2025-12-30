#!/bin/bash

echo "=========================================="
echo "StaticWaves Maker - Quick Start"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env"
    echo ""
    echo "⚠️  Please edit backend/.env with your API keys before continuing!"
    echo "   Required: STRIPE_SECRET_KEY, ANTHROPIC_API_KEY"
    echo ""
    read -p "Press Enter after updating .env file..."
fi

echo "Starting services with Docker Compose..."
echo ""

# Start services
docker-compose up -d

echo ""
echo "✓ Services started!"
echo ""
echo "=========================================="
echo "Access Points:"
echo "=========================================="
echo "Backend API:    http://localhost:8000"
echo "API Docs:       http://localhost:8000/docs"
echo "Database:       localhost:5432"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Check API health: curl http://localhost:8000/health"
echo "2. View logs:        docker-compose logs -f"
echo "3. Stop services:    docker-compose down"
echo ""
echo "For frontend setup, see README.md"
echo "=========================================="

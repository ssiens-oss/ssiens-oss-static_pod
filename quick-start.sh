#!/bin/bash
# Quick Start Script for StaticWaves POD

echo "Starting StaticWaves POD locally..."

# Create directories
mkdir -p logs output

# Start Redis
echo "Starting Redis..."
redis-server --daemonize yes --logfile logs/redis.log
sleep 2

# Setup Python environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r music-engine/requirements-api.txt

# Start Music API
echo "Starting Music API..."
export REDIS_HOST=localhost
export REDIS_PORT=6379
export OUTPUT_DIR=$PWD/output

cd music-engine/api
python main.py > ../../logs/music-api.log 2>&1 &
echo $! > ../../logs/music-api.pid
cd ../..

sleep 3

# Check if API is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Music API is running: http://localhost:8000"
else
    echo "❌ Music API failed to start. Check logs/music-api.log"
    exit 1
fi

echo ""
echo "✅ Backend services are running!"
echo ""
echo "Now starting frontend..."
echo "Music Studio will be available at: http://localhost:5174"
echo ""

# Start frontend
npm run dev:music

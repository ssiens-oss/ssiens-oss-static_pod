#!/bin/bash

# MashDeck GUI Startup Script

echo "🎵 Starting MashDeck GUI..."
echo ""

# Kill any existing processes on the ports
echo "Checking for existing processes..."
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Start backend in background
echo "Starting FastAPI backend on port 8080..."
cd mashdeck/gui/api
python3 main.py > /tmp/mashdeck-api.log 2>&1 &
BACKEND_PID=$!
cd ../../..

# Wait for backend to be ready
echo "Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✓ Backend is running on http://localhost:8080"
else
    echo "⚠ Backend may not be running. Check /tmp/mashdeck-api.log"
fi

# Install frontend dependencies if needed
if [ ! -d "mashdeck/gui/web/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd mashdeck/gui/web
    npm install
    cd ../../..
fi

# Start frontend
echo ""
echo "Starting React frontend on port 3000..."
echo ""
cd mashdeck/gui/web
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT

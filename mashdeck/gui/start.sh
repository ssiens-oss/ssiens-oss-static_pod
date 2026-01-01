#!/bin/bash

# Quick start script from mashdeck/gui directory

echo "🎵 MashDeck GUI Quick Start"
echo ""

# Start backend
echo "Starting backend..."
cd api
python3 main.py > /tmp/mashdeck-api.log 2>&1 &
BACKEND_PID=$!
cd ..

sleep 2

# Start frontend
echo "Starting frontend..."
cd web

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

npm run dev

# Cleanup
trap "kill $BACKEND_PID 2>/dev/null" EXIT

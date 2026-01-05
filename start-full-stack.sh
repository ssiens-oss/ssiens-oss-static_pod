#!/bin/bash
#
# StaticWaves POD Engine - Full Stack Startup Script
# Launches both FastAPI backend and React frontend
#

set -e

echo "======================================================================"
echo "  StaticWaves POD Engine - Full Stack Launcher"
echo "======================================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo "Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file${NC}"
        echo -e "${YELLOW}Please edit .env with your API keys before continuing${NC}"
    else
        echo -e "${RED}Error: .env.example not found${NC}"
    fi
fi

echo ""
echo "======================================================================"
echo "  Step 1: Installing Dependencies"
echo "======================================================================"
echo ""

# Install Python backend dependencies
echo -e "${BLUE}📦 Installing Python backend dependencies...${NC}"
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  backend/requirements.txt not found, skipping...${NC}"
fi

# Install Node.js frontend dependencies
echo ""
echo -e "${BLUE}📦 Installing Node.js frontend dependencies...${NC}"
if command -v npm &> /dev/null; then
    npm install
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${RED}Error: npm not found. Please install Node.js${NC}"
    exit 1
fi

echo ""
echo "======================================================================"
echo "  Step 2: Launching Services"
echo "======================================================================"
echo ""

# Create log directory
mkdir -p logs

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✓ All services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start FastAPI backend
echo -e "${BLUE}🚀 Starting FastAPI backend on http://localhost:8000${NC}"
cd backend
python3 main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend to be ready...${NC}"
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}✗ Backend failed to start. Check logs/backend.log${NC}"
    cat logs/backend.log
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Start Vite frontend
echo ""
echo -e "${BLUE}🎨 Starting Vite frontend on http://localhost:5173${NC}"
npm run dev > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

echo ""
echo "======================================================================"
echo "  🎉 Full Stack Running!"
echo "======================================================================"
echo ""
echo -e "${GREEN}Backend API:${NC}  http://localhost:8000"
echo -e "${GREEN}API Docs:${NC}     http://localhost:8000/docs"
echo -e "${GREEN}Frontend UI:${NC}  http://localhost:5173"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo "  Backend:  logs/backend.log"
echo "  Frontend: logs/frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Monitor processes
while true; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}Backend process died. Check logs/backend.log${NC}"
        cleanup
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}Frontend process died. Check logs/frontend.log${NC}"
        cleanup
    fi
    sleep 5
done

#!/bin/bash
#
# StaticWaves POD Engine - RunPod Deployment Script
# Optimized for RunPod ComfyUI template with ports 5174 and 8188
#

set -e

echo "========================================"
echo "🚀 StaticWaves POD Engine Deployment"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to script directory
cd "$(dirname "$0")"

echo "📦 Step 1: Installing Dependencies"
echo "-----------------------------------"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python packages..."
pip install -q -r backend/requirements.txt
echo -e "${GREEN}✓${NC} Python dependencies installed"

# Install Node dependencies
echo "Installing Node packages..."
npm install --silent
echo -e "${GREEN}✓${NC} Node dependencies installed"

echo ""
echo "🔨 Step 2: Building Frontend"
echo "-----------------------------------"
npm run build
echo -e "${GREEN}✓${NC} Frontend built successfully"

echo ""
echo "🗄️  Step 3: Database Setup"
echo "-----------------------------------"
mkdir -p logs
cd backend
if [ ! -f "staticwaves_pod.db" ]; then
    echo "Initializing database..."
    python -c "from main import Base, engine; Base.metadata.create_all(bind=engine)"
    echo -e "${GREEN}✓${NC} Database initialized"
else
    echo -e "${YELLOW}⚠${NC}  Database already exists, skipping"
fi
cd ..

echo ""
echo "🔄 Step 4: Stopping Old Services"
echo "-----------------------------------"
pkill -f "python3.*main.py" 2>/dev/null && echo "Stopped old backend" || echo "No old backend running"
pkill -f "vite" 2>/dev/null && echo "Stopped old frontend" || echo "No old frontend running"
sleep 2

echo ""
echo "🚀 Step 5: Starting Services"
echo "-----------------------------------"

# Start backend on port 8188
echo "Starting backend on port 8188..."
cd backend
nohup python main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo "Waiting for backend to initialize..."
for i in {1..10}; do
    if curl -s http://localhost:8188/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend is ready!"
        break
    fi
    sleep 1
done

# Start frontend on port 5174
echo "Starting frontend on port 5174..."
nohup npm run dev > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID)"

# Wait for frontend to be ready
echo "Waiting for frontend to initialize..."
for i in {1..10}; do
    if curl -s http://localhost:5174 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Frontend is ready!"
        break
    fi
    sleep 1
done

echo ""
echo "========================================"
echo "✨ POD Engine Deployed Successfully!"
echo "========================================"
echo ""
echo "📡 Service Status:"
echo "   Backend:  http://localhost:8188 ✓"
echo "   Frontend: http://localhost:5174 ✓"
echo ""
echo "🌐 RunPod Access:"
echo "   1. Go to your RunPod dashboard"
echo "   2. Find your pod: ckgp3l49rwtvjr"
echo "   3. Click: Port 5174 → HTTP Service (Main App)"
echo "   4. Click: Port 8188 → HTTP Service (API Docs)"
echo ""
echo "📝 Log Files:"
echo "   Backend:  logs/backend.log"
echo "   Frontend: logs/frontend.log"
echo ""
echo "🔧 Management Commands:"
echo "   View logs:    tail -f logs/backend.log"
echo "   Stop backend: kill $BACKEND_PID"
echo "   Stop frontend: kill $FRONTEND_PID"
echo ""
echo "📚 Documentation:"
echo "   - Full guide: README_FULLSTACK_APP.md"
echo "   - AI features: AI_GENERATION_GUIDE.md"
echo ""

# Save PIDs for later management
echo "$BACKEND_PID" > logs/backend.pid
echo "$FRONTEND_PID" > logs/frontend.pid

echo "🎉 Ready to create POD products! Happy designing!"
echo ""

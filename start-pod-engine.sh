#!/bin/bash

# POD Engine Startup Script
# Starts all services required for the production POD engine

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << "EOF"
╔════════════════════════════════════════════════════╗
║              POD Engine Startup                    ║
║         Production POD Automation System           ║
╚════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Function to check if a port is in use
check_port() {
  local port=$1
  if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
    return 0
  else
    return 1
  fi
}

# Function to wait for a service to be ready
wait_for_service() {
  local name=$1
  local url=$2
  local max_attempts=30
  local attempt=0

  echo -e "${YELLOW}⏳ Waiting for $name to be ready...${NC}"

  while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "$url" > /dev/null 2>&1; then
      echo -e "${GREEN}✓ $name is ready${NC}"
      return 0
    fi
    attempt=$((attempt + 1))
    sleep 2
  done

  echo -e "${RED}✗ $name failed to start${NC}"
  return 1
}

# Load environment variables
if [ -f .env ]; then
  echo -e "${BLUE}📂 Loading environment variables...${NC}"
  export $(cat .env | grep -v '^#' | xargs)
  echo -e "${GREEN}✓ Environment loaded${NC}"
else
  echo -e "${YELLOW}⚠️  No .env file found, using defaults${NC}"
fi

# Create required directories
echo -e "${BLUE}📁 Creating required directories...${NC}"
mkdir -p /data/designs
mkdir -p /data/comfyui/output
mkdir -p /workspace/ComfyUI
echo -e "${GREEN}✓ Directories created${NC}"

# Check if running in RunPod environment
if [ -n "$RUNPOD_POD_ID" ]; then
  echo -e "${BLUE}☁️  Running in RunPod environment${NC}"
  COMFYUI_URL=${COMFYUI_URL:-http://localhost:8188}
else
  echo -e "${BLUE}🖥️  Running in local environment${NC}"
  COMFYUI_URL=${COMFYUI_URL:-http://localhost:8188}
fi

# Start ComfyUI if not already running
if ! check_port 8188; then
  echo -e "${BLUE}🎨 Starting ComfyUI...${NC}"

  if [ -d "/workspace/ComfyUI" ]; then
    cd /workspace/ComfyUI
    nohup python3 main.py --listen 0.0.0.0 --port 8188 > /data/comfyui.log 2>&1 &
    COMFYUI_PID=$!
    echo $COMFYUI_PID > /tmp/comfyui.pid
    cd - > /dev/null

    # Wait for ComfyUI to be ready
    wait_for_service "ComfyUI" "http://localhost:8188/system_stats"
  else
    echo -e "${YELLOW}⚠️  ComfyUI not found at /workspace/ComfyUI${NC}"
    echo -e "${YELLOW}⚠️  Please install ComfyUI or set COMFYUI_URL to an external instance${NC}"
  fi
else
  echo -e "${GREEN}✓ ComfyUI is already running${NC}"
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo -e "${BLUE}📦 Installing dependencies...${NC}"
  npm install
  echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Start the POD Engine API
echo -e "${BLUE}🚀 Starting POD Engine API...${NC}"

PORT=${PORT:-3000}

if check_port $PORT; then
  echo -e "${RED}✗ Port $PORT is already in use${NC}"
  echo -e "${YELLOW}Please stop the service using port $PORT or change PORT in .env${NC}"
  exit 1
fi

# Start the engine
npm run engine &
ENGINE_PID=$!
echo $ENGINE_PID > /tmp/pod-engine.pid

# Wait for the engine to be ready
wait_for_service "POD Engine" "http://localhost:$PORT/health"

# Display status
echo -e "\n${GREEN}"
cat << "EOF"
╔════════════════════════════════════════════════════╗
║           POD Engine Started Successfully!         ║
╚════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}Services:${NC}"
echo -e "  ${GREEN}✓${NC} ComfyUI:    http://localhost:8188"
echo -e "  ${GREEN}✓${NC} POD Engine: http://localhost:$PORT"
echo -e ""
echo -e "${BLUE}API Endpoints:${NC}"
echo -e "  Health:    http://localhost:$PORT/health"
echo -e "  Metrics:   http://localhost:$PORT/api/metrics"
echo -e "  Jobs:      http://localhost:$PORT/api/jobs"
echo -e "  Generate:  http://localhost:$PORT/api/generate"
echo -e ""
echo -e "${BLUE}Logs:${NC}"
echo -e "  ComfyUI:   tail -f /data/comfyui.log"
echo -e "  Engine:    Check console output"
echo -e ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo -e ""

# Function to cleanup on exit
cleanup() {
  echo -e "\n${YELLOW}🛑 Stopping services...${NC}"

  if [ -f /tmp/pod-engine.pid ]; then
    ENGINE_PID=$(cat /tmp/pod-engine.pid)
    if ps -p $ENGINE_PID > /dev/null 2>&1; then
      kill $ENGINE_PID
      echo -e "${GREEN}✓ POD Engine stopped${NC}"
    fi
    rm /tmp/pod-engine.pid
  fi

  if [ -f /tmp/comfyui.pid ]; then
    COMFYUI_PID=$(cat /tmp/comfyui.pid)
    if ps -p $COMFYUI_PID > /dev/null 2>&1; then
      kill $COMFYUI_PID
      echo -e "${GREEN}✓ ComfyUI stopped${NC}"
    fi
    rm /tmp/comfyui.pid
  fi

  echo -e "${BLUE}👋 Goodbye!${NC}"
  exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for the engine process
wait $ENGINE_PID

#!/bin/bash

###############################################################################
# StaticWaves POD Engine - Complete Deployment Script
#
# Deploys the full POD automation pipeline including:
#   - ComfyUI AI Image Generation
#   - POD Gateway (Human-in-the-loop approval)
#   - Printify Integration
#   - Multi-Platform Publishing
#   - Health Monitoring & Status Dashboard
#
# Usage:
#   Local:  ./deploy-pod-engine.sh local
#   RunPod: ./deploy-pod-engine.sh runpod
#   Docker: ./deploy-pod-engine.sh docker
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Print functions
print_header() {
    echo -e "\n${PURPLE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Banner
clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗  ██████╗ ██████╗     ███████╗███╗   ██╗ ██████╗   ║
║   ██╔══██╗██╔═══██╗██╔══██╗    ██╔════╝████╗  ██║██╔════╝   ║
║   ██████╔╝██║   ██║██║  ██║    █████╗  ██╔██╗ ██║██║  ███╗  ║
║   ██╔═══╝ ██║   ██║██║  ██║    ██╔══╝  ██║╚██╗██║██║   ██║  ║
║   ██║     ╚██████╔╝██████╔╝    ███████╗██║ ╚████║╚██████╔╝  ║
║   ╚═╝      ╚═════╝ ╚═════╝     ╚══════╝╚═╝  ╚═══╝ ╚═════╝   ║
║                                                               ║
║          Complete POD Automation Pipeline Deployment         ║
║                        Version 2.0                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "${CYAN}"
echo "🎨 AI Image Generation (ComfyUI + Claude)"
echo "✋ Human-in-the-Loop Approval Gateway"
echo "🛍️  Multi-Platform Publishing (Printify, Shopify, etc.)"
echo "📊 Real-time Monitoring Dashboard"
echo "☁️  Cloud-Ready Deployment"
echo -e "${NC}"

# Determine deployment mode
DEPLOY_MODE="${1:-local}"

if [[ "$DEPLOY_MODE" != "local" && "$DEPLOY_MODE" != "runpod" && "$DEPLOY_MODE" != "docker" ]]; then
    print_error "Invalid deployment mode: $DEPLOY_MODE"
    echo "Usage: $0 [local|runpod|docker]"
    exit 1
fi

print_info "Deployment Mode: ${DEPLOY_MODE}"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

###############################################################################
# Step 1: Environment Setup
###############################################################################

print_header "Environment Configuration"

# Check for .env file
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_info "Please edit .env with your API keys before continuing"
    print_info "Required: ANTHROPIC_API_KEY, PRINTIFY_API_KEY, PRINTIFY_SHOP_ID"
    read -p "Press Enter after editing .env..."
fi

# Load environment
set -a
source .env
set +a
print_success "Environment loaded"

# Validate critical variables
print_step "Validating configuration..."

MISSING_VARS=()

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" == "sk-ant-your-api-key-here" ]; then
    MISSING_VARS+=("ANTHROPIC_API_KEY")
fi

if [ -z "$PRINTIFY_API_KEY" ] || [ "$PRINTIFY_API_KEY" == "your-printify-api-key" ]; then
    MISSING_VARS+=("PRINTIFY_API_KEY")
fi

if [ -z "$PRINTIFY_SHOP_ID" ] || [ "$PRINTIFY_SHOP_ID" == "your-shop-id" ]; then
    MISSING_VARS+=("PRINTIFY_SHOP_ID")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    print_info "Please set these in your .env file"
    exit 1
fi

print_success "Configuration valid"

###############################################################################
# Step 2: Dependencies Installation
###############################################################################

print_header "Installing Dependencies"

# Check Python
print_step "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION installed"
else
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check Node.js
print_step "Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION installed"
else
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Install Python dependencies for Gateway
print_step "Installing POD Gateway dependencies..."
cd gateway
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    print_success "Virtual environment created"
fi
source .venv/bin/activate
pip install -q -r requirements.txt
print_success "Gateway dependencies installed"
cd ..

# Install Node.js dependencies
print_step "Installing Node.js dependencies..."
npm install --silent
print_success "Node.js dependencies installed"

###############################################################################
# Step 3: ComfyUI Setup (if local/runpod)
###############################################################################

if [[ "$DEPLOY_MODE" != "docker" ]]; then
    print_header "ComfyUI Setup"

    if [ ! -d "ComfyUI" ]; then
        print_step "ComfyUI not found. Setting up..."
        ./scripts/setup-comfyui.sh
        print_success "ComfyUI installed"
    else
        print_info "ComfyUI already installed"
    fi
fi

###############################################################################
# Step 4: Create Required Directories
###############################################################################

print_header "Creating Directories"

DIRS=(
    "${STORAGE_PATH:-/data/designs}"
    "${POD_IMAGE_DIR:-/workspace/comfyui/output}"
    "${POD_ARCHIVE_DIR:-/workspace/gateway/archive}"
    "/data/logs"
)

for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_success "Created: $dir"
    else
        print_info "Exists: $dir"
    fi
done

###############################################################################
# Step 5: Deploy POD Gateway
###############################################################################

print_header "Deploying POD Gateway"

cd gateway

# Create gateway state file
if [ ! -f "state.json" ]; then
    echo '{"designs": []}' > state.json
    print_success "Initialized state file"
fi

# Copy .env for gateway
if [ ! -f ".env" ]; then
    cat > .env << GATEWAY_ENV
PRINTIFY_API_KEY=$PRINTIFY_API_KEY
PRINTIFY_SHOP_ID=$PRINTIFY_SHOP_ID
POD_IMAGE_DIR=${POD_IMAGE_DIR:-/workspace/comfyui/output}
POD_STATE_FILE=${POD_STATE_FILE:-/workspace/gateway/state.json}
POD_ARCHIVE_DIR=${POD_ARCHIVE_DIR:-/workspace/gateway/archive}
FLASK_HOST=${FLASK_HOST:-0.0.0.0}
FLASK_PORT=${FLASK_PORT:-5000}
FLASK_DEBUG=${FLASK_DEBUG:-false}
GATEWAY_ENV
    print_success "Gateway .env configured"
fi

cd ..

print_success "POD Gateway ready"

###############################################################################
# Step 6: Health Check System
###############################################################################

print_header "Setting Up Health Checks"

# Create health check endpoint
mkdir -p services/health

cat > services/health/checker.ts << 'HEALTH_EOF'
/**
 * Health Check System for POD Engine
 */

import fs from 'fs';
import path from 'path';

export interface HealthStatus {
  service: string;
  status: 'healthy' | 'degraded' | 'down';
  message: string;
  timestamp: string;
}

export class HealthChecker {
  async checkComfyUI(url: string): Promise<HealthStatus> {
    try {
      const response = await fetch(`${url}/system_stats`, { signal: AbortSignal.timeout(5000) });
      const healthy = response.ok;

      return {
        service: 'ComfyUI',
        status: healthy ? 'healthy' : 'down',
        message: healthy ? 'ComfyUI is running' : 'ComfyUI not responding',
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        service: 'ComfyUI',
        status: 'down',
        message: `ComfyUI unreachable: ${error}`,
        timestamp: new Date().toISOString()
      };
    }
  }

  async checkGateway(url: string): Promise<HealthStatus> {
    try {
      const response = await fetch(`${url}/health`, { signal: AbortSignal.timeout(5000) });
      const healthy = response.ok;

      return {
        service: 'POD Gateway',
        status: healthy ? 'healthy' : 'down',
        message: healthy ? 'Gateway is running' : 'Gateway not responding',
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        service: 'POD Gateway',
        status: 'down',
        message: `Gateway unreachable: ${error}`,
        timestamp: new Date().toISOString()
      };
    }
  }

  async checkPrintify(apiKey: string): Promise<HealthStatus> {
    try {
      const response = await fetch('https://api.printify.com/v1/shops.json', {
        headers: { 'Authorization': `Bearer ${apiKey}` },
        signal: AbortSignal.timeout(5000)
      });

      const healthy = response.ok;

      return {
        service: 'Printify API',
        status: healthy ? 'healthy' : 'degraded',
        message: healthy ? 'Printify API accessible' : 'Printify API issues',
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        service: 'Printify API',
        status: 'down',
        message: `Printify unreachable: ${error}`,
        timestamp: new Date().toISOString()
      };
    }
  }

  async checkAll(config: {
    comfyuiUrl: string;
    gatewayUrl: string;
    printifyApiKey: string;
  }): Promise<HealthStatus[]> {
    return Promise.all([
      this.checkComfyUI(config.comfyuiUrl),
      this.checkGateway(config.gatewayUrl),
      this.checkPrintify(config.printifyApiKey)
    ]);
  }

  generateReport(statuses: HealthStatus[]): string {
    const allHealthy = statuses.every(s => s.status === 'healthy');
    const anyDown = statuses.some(s => s.status === 'down');

    let report = '\n';
    report += '╔═══════════════════════════════════════════╗\n';
    report += '║       POD Engine Health Report           ║\n';
    report += '╚═══════════════════════════════════════════╝\n\n';

    for (const status of statuses) {
      const icon = status.status === 'healthy' ? '✓' :
                   status.status === 'degraded' ? '⚠' : '✗';
      const color = status.status === 'healthy' ? '32' :
                    status.status === 'degraded' ? '33' : '31';

      report += `\x1b[${color}m${icon}\x1b[0m ${status.service}: ${status.message}\n`;
    }

    report += '\n';
    if (allHealthy) {
      report += '\x1b[32m✓ All systems operational\x1b[0m\n';
    } else if (anyDown) {
      report += '\x1b[31m✗ Critical services down\x1b[0m\n';
    } else {
      report += '\x1b[33m⚠ Some services degraded\x1b[0m\n';
    }

    return report;
  }
}
HEALTH_EOF

print_success "Health check system created"

###############################################################################
# Step 7: Create Startup Scripts
###############################################################################

print_header "Creating Startup Scripts"

# Main startup script
cat > start-pod-engine.sh << 'START_EOF'
#!/bin/bash

set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}Starting POD Engine...${NC}\n"

# Load environment
set -a
source .env 2>/dev/null || true
set +a

# Start ComfyUI
if [ -d "ComfyUI" ]; then
    echo -e "${CYAN}▶ Starting ComfyUI...${NC}"
    cd ComfyUI
    python3 main.py --listen 0.0.0.0 --port 8188 > ../logs/comfyui.log 2>&1 &
    COMFYUI_PID=$!
    echo $COMFYUI_PID > ../logs/comfyui.pid
    cd ..
    echo -e "${GREEN}✓ ComfyUI started (PID: $COMFYUI_PID)${NC}"
    echo -e "${YELLOW}  Access at: http://localhost:8188${NC}"
else
    echo -e "${YELLOW}⚠ ComfyUI not found, skipping...${NC}"
fi

# Wait for ComfyUI to initialize
sleep 5

# Start POD Gateway
echo -e "${CYAN}▶ Starting POD Gateway...${NC}"
cd gateway
source .venv/bin/activate
python app/main.py > ../logs/gateway.log 2>&1 &
GATEWAY_PID=$!
echo $GATEWAY_PID > ../logs/gateway.pid
cd ..
echo -e "${GREEN}✓ POD Gateway started (PID: $GATEWAY_PID)${NC}"
echo -e "${YELLOW}  Access at: http://localhost:5000${NC}"

# Start Web UI (optional, for pipeline management)
echo -e "${CYAN}▶ Starting Web UI...${NC}"
npm run dev > logs/webui.log 2>&1 &
WEBUI_PID=$!
echo $WEBUI_PID > logs/webui.pid
echo -e "${GREEN}✓ Web UI started (PID: $WEBUI_PID)${NC}"
echo -e "${YELLOW}  Access at: http://localhost:5173${NC}"

# Save all PIDs
cat > logs/pod-engine.pids << PIDS_EOF
COMFYUI_PID=$COMFYUI_PID
GATEWAY_PID=$GATEWAY_PID
WEBUI_PID=$WEBUI_PID
PIDS_EOF

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   POD Engine Started Successfully!       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Services:${NC}"
echo -e "  ComfyUI:      http://localhost:8188"
echo -e "  POD Gateway:  http://localhost:5000"
echo -e "  Web UI:       http://localhost:5173"
echo ""
echo -e "${CYAN}Logs:${NC}"
echo -e "  tail -f logs/comfyui.log"
echo -e "  tail -f logs/gateway.log"
echo -e "  tail -f logs/webui.log"
echo ""
echo -e "${CYAN}Stop:${NC}"
echo -e "  ./stop-pod-engine.sh"
echo ""
START_EOF

chmod +x start-pod-engine.sh
print_success "Created start-pod-engine.sh"

# Stop script
cat > stop-pod-engine.sh << 'STOP_EOF'
#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Stopping POD Engine..."

if [ -f logs/pod-engine.pids ]; then
    source logs/pod-engine.pids

    for pid_var in COMFYUI_PID GATEWAY_PID WEBUI_PID; do
        pid=${!pid_var}
        if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
            kill $pid
            echo -e "${GREEN}✓ Stopped $pid_var ($pid)${NC}"
        fi
    done

    rm logs/pod-engine.pids
else
    echo -e "${RED}✗ No PID file found${NC}"
fi

echo "Stopped."
STOP_EOF

chmod +x stop-pod-engine.sh
print_success "Created stop-pod-engine.sh"

###############################################################################
# Step 8: Mode-Specific Configuration
###############################################################################

print_header "Finalizing ${DEPLOY_MODE} Deployment"

case "$DEPLOY_MODE" in
    local)
        print_info "Local deployment configured"
        print_info "All services will run on localhost"
        ;;

    runpod)
        print_step "Configuring for RunPod..."

        # Update environment for RunPod paths
        sed -i 's|COMFYUI_OUTPUT_DIR=.*|COMFYUI_OUTPUT_DIR=/workspace/ComfyUI/output|g' .env
        sed -i 's|STORAGE_PATH=.*|STORAGE_PATH=/workspace/data/designs|g' .env
        sed -i 's|POD_IMAGE_DIR=.*|POD_IMAGE_DIR=/workspace/ComfyUI/output|g' .env

        print_success "RunPod paths configured"
        print_warning "Remember to expose ports 5000 (Gateway) and 8188 (ComfyUI) in RunPod"
        ;;

    docker)
        print_step "Building Docker image..."
        docker build -f Dockerfile.runpod -t staticwaves-pod-engine:latest .
        print_success "Docker image built"

        print_info "To run: docker run -p 5000:5000 -p 8188:8188 --gpus all staticwaves-pod-engine:latest"
        ;;
esac

###############################################################################
# Step 9: Health Check & Verification
###############################################################################

print_header "Deployment Complete!"

cat << 'COMPLETE_EOF'

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              🎉 POD Engine Deployment Complete! 🎉           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

📋 Next Steps:

1. Start the engine:
   ./start-pod-engine.sh

2. Access services:
   • POD Gateway (Approval):  http://localhost:5000
   • ComfyUI (Generation):    http://localhost:8188
   • Web UI (Management):     http://localhost:5173

3. Workflow:
   a) Generate designs with ComfyUI
   b) Review & approve in POD Gateway (localhost:5000)
   c) Approved designs auto-publish to Printify
   d) Products sync to your stores

4. Monitor:
   • Check logs: tail -f logs/*.log
   • Health: curl http://localhost:5000/health

5. Stop engine:
   ./stop-pod-engine.sh

📚 Documentation:
   • Gateway:   gateway/README.md
   • Setup:     SETUP_GUIDE.md
   • Pipeline:  PIPELINE_ARCHITECTURE.md

🔑 Configuration:
   Edit .env for API keys and platform settings

COMPLETE_EOF

print_success "Deployment completed successfully!"

###############################################################################
# Create logs directory
###############################################################################

mkdir -p logs
touch logs/comfyui.log logs/gateway.log logs/webui.log

echo ""
print_info "Logs will be written to: ./logs/"
echo ""

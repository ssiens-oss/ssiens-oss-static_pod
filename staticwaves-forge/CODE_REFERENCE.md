# StaticWaves Forge - Complete Code Reference

This document contains all the key code files for the StaticWaves Forge AI 3D Asset Generation Platform.

---

## Table of Contents

1. [Deployment & Infrastructure](#deployment--infrastructure)
   - [One-Click Boot Script](#one-click-boot-script)
   - [RunPod Auto-Start](#runpod-auto-start)
   - [RunPod Template](#runpod-template)
2. [Frontend - Next.js Web App](#frontend---nextjs-web-app)
   - [Generate Page](#generate-page)
   - [Prompt Panel Component](#prompt-panel-component)
3. [Backend - FastAPI](#backend---fastapi)
   - [Main API Entry](#main-api-entry)
   - [Common Schemas](#common-schemas)
   - [Generation Routes](#generation-routes)
4. [Docker & CI/CD](#docker--cicd)
   - [Web Dockerfile](#web-dockerfile)
   - [API Dockerfile](#api-dockerfile)
   - [Production Docker Compose](#production-docker-compose)
   - [GitHub Actions Workflow](#github-actions-workflow)

---

## Deployment & Infrastructure

### One-Click Boot Script

**File:** `staticwaves-forge/start-unified.sh`

```bash
#!/bin/bash
# StaticWaves Forge - One-Click Boot System for RunPod
# Starts all services in the correct order with health checks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE_DIR="/workspace"
FORGE_DIR="$WORKSPACE_DIR/staticwaves-forge/staticwaves-forge"
POD_DIR="$WORKSPACE_DIR/ssiens-oss-static_pod"
LOG_DIR="/tmp/staticwaves-logs"
PID_DIR="/tmp/staticwaves-pids"

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Banner
clear
echo -e "${PURPLE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                                        ║${NC}"
echo -e "${PURPLE}║         ${CYAN}✨ StaticWaves Forge ${PURPLE}${YELLOW}One-Click Boot${PURPLE} ✨         ║${NC}"
echo -e "${PURPLE}║                                                        ║${NC}"
echo -e "${PURPLE}║         ${GREEN}Unified RunPod Instance Startup${PURPLE}            ║${NC}"
echo -e "${PURPLE}║                                                        ║${NC}"
echo -e "${PURPLE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Progress indicator
show_progress() {
    local service=$1
    local status=$2
    if [ "$status" == "start" ]; then
        echo -e "${YELLOW}▶  Starting ${service}...${NC}"
    elif [ "$status" == "done" ]; then
        echo -e "${GREEN}✓  ${service} started successfully${NC}"
    elif [ "$status" == "fail" ]; then
        echo -e "${RED}✗  ${service} failed to start${NC}"
    fi
}

# Health check function
wait_for_service() {
    local name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo -e "${CYAN}   Waiting for $name to be ready...${NC}"

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}   ✓ $name is healthy${NC}"
            return 0
        fi
        echo -ne "${YELLOW}   ⏳ Attempt $attempt/$max_attempts...${NC}\r"
        sleep 2
        ((attempt++))
    done

    echo -e "${RED}   ✗ $name failed health check${NC}"
    return 1
}

# Kill existing processes
cleanup_existing() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"

    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "redis-server" 2>/dev/null || true

    rm -f "$PID_DIR"/*.pid
    echo -e "${GREEN}✓ Cleanup complete${NC}"
    echo ""
}

# Start Redis (optional, for job queue)
start_redis() {
    show_progress "Redis Queue" "start"

    if command -v redis-server > /dev/null 2>&1; then
        redis-server --daemonize yes \
            --port 6379 \
            --logfile "$LOG_DIR/redis.log" \
            --pidfile "$PID_DIR/redis.pid" \
            --save 60 1

        sleep 2
        if redis-cli ping > /dev/null 2>&1; then
            show_progress "Redis Queue" "done"
            echo "$!" > "$PID_DIR/redis.pid"
            return 0
        fi
    else
        echo -e "${YELLOW}   ⚠ Redis not installed - running without queue${NC}"
    fi
    return 0
}

# Start Forge API Backend
start_forge_api() {
    show_progress "Forge API Backend" "start"

    cd "$FORGE_DIR/apps/api"

    # Install dependencies if needed
    if [ ! -f "$PID_DIR/api_deps_installed" ]; then
        echo -e "${CYAN}   Installing Python dependencies...${NC}"
        pip install -q fastapi uvicorn python-multipart aiofiles pydantic python-jose passlib || true
        touch "$PID_DIR/api_deps_installed"
    fi

    # Start API server
    nohup python3 -m uvicorn main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 2 \
        > "$LOG_DIR/forge-api.log" 2>&1 &

    echo $! > "$PID_DIR/forge-api.pid"

    if wait_for_service "Forge API" "http://localhost:8000/"; then
        show_progress "Forge API Backend" "done"
        return 0
    else
        show_progress "Forge API Backend" "fail"
        return 1
    fi
}

# Start Forge Web GUI
start_forge_web() {
    show_progress "Forge Web GUI" "start"

    cd "$FORGE_DIR/apps/web"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${CYAN}   Installing Node dependencies (this may take a minute)...${NC}"
        npm install --silent
    fi

    # Start web server
    nohup npm run dev \
        > "$LOG_DIR/forge-web.log" 2>&1 &

    echo $! > "$PID_DIR/forge-web.pid"

    if wait_for_service "Forge Web" "http://localhost:3000/"; then
        show_progress "Forge Web GUI" "done"
        return 0
    else
        show_progress "Forge Web GUI" "fail"
        return 1
    fi
}

# Display service URLs
show_service_urls() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ All services are running!${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${CYAN}📡 Service URLs:${NC}"
    echo ""

    # Get RunPod ID from hostname
    POD_ID=$(hostname)

    echo -e "${PURPLE}Forge Web GUI:${NC}"
    echo -e "   Local:  ${GREEN}http://localhost:3000${NC}"
    echo -e "   Public: ${GREEN}https://$POD_ID-3000.proxy.runpod.net${NC}"
    echo ""

    echo -e "${PURPLE}Forge API:${NC}"
    echo -e "   Local:  ${GREEN}http://localhost:8000${NC}"
    echo -e "   Public: ${GREEN}https://$POD_ID-8000.proxy.runpod.net${NC}"
    echo -e "   Docs:   ${GREEN}https://$POD_ID-8000.proxy.runpod.net/docs${NC}"
    echo ""

    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${PURPLE}Redis Queue:${NC}"
        echo -e "   Local:  ${GREEN}localhost:6379${NC}"
        echo ""
    fi

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${CYAN}📊 Service Status:${NC}"
    echo -e "   PID files: ${YELLOW}$PID_DIR${NC}"
    echo -e "   Log files: ${YELLOW}$LOG_DIR${NC}"
    echo ""
    echo -e "${CYAN}🛠  Management Commands:${NC}"
    echo -e "   View logs:    ${YELLOW}tail -f $LOG_DIR/*.log${NC}"
    echo -e "   Stop all:     ${YELLOW}$0 stop${NC}"
    echo -e "   Restart all:  ${YELLOW}$0 restart${NC}"
    echo -e "   Status check: ${YELLOW}$0 status${NC}"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Stop all services
stop_all_services() {
    echo -e "${YELLOW}🛑 Stopping all services...${NC}"

    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            service=$(basename "$pid_file" .pid)
            kill "$pid" 2>/dev/null || true
            rm "$pid_file"
            echo -e "${GREEN}✓ Stopped $service${NC}"
        fi
    done

    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    redis-cli shutdown 2>/dev/null || true

    echo -e "${GREEN}✅ All services stopped${NC}"
}

# Show status
show_status() {
    echo -e "${CYAN}📊 Service Status:${NC}"
    echo ""

    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            service=$(basename "$pid_file" .pid)
            if ps -p "$pid" > /dev/null 2>&1; then
                echo -e "   ${GREEN}●${NC} $service (PID: $pid) - ${GREEN}Running${NC}"
            else
                echo -e "   ${RED}●${NC} $service (PID: $pid) - ${RED}Dead${NC}"
            fi
        fi
    done
    echo ""
}

# Main execution
main() {
    case "${1:-start}" in
        start)
            cleanup_existing
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${CYAN}🚀 Starting all services...${NC}"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""

            start_redis
            echo ""
            start_forge_api
            echo ""
            start_forge_web
            echo ""

            show_service_urls

            echo -e "${GREEN}🎉 StaticWaves Forge is ready!${NC}"
            echo ""
            ;;

        stop)
            stop_all_services
            ;;

        restart)
            stop_all_services
            sleep 2
            $0 start
            ;;

        status)
            show_status
            ;;

        logs)
            tail -f "$LOG_DIR"/*.log
            ;;

        *)
            echo "Usage: $0 {start|stop|restart|status|logs}"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
```

---

### RunPod Auto-Start

**File:** `staticwaves-forge/runpod-start.sh`

```bash
#!/bin/bash
# RunPod Auto-Start Script
# Place this in /workspace and it will run on pod boot

set -e

echo "🚀 RunPod Boot - Initializing StaticWaves Forge..."

# Wait for system to be ready
sleep 5

# Clone/update repository if needed
if [ ! -d "/workspace/staticwaves-forge" ]; then
    echo "📥 Cloning StaticWaves Forge repository..."
    cd /workspace
    git clone -b claude/ai-3d-asset-engine-Q6XOw \
        https://github.com/ssiens-oss/ssiens-oss-static_pod.git \
        staticwaves-forge
fi

# Run the unified startup script
if [ -f "/workspace/staticwaves-forge/staticwaves-forge/start-unified.sh" ]; then
    echo "▶️  Launching unified boot system..."
    bash /workspace/staticwaves-forge/staticwaves-forge/start-unified.sh start
else
    echo "❌ Startup script not found!"
    echo "Run: git pull to update the repository"
    exit 1
fi

echo "✅ StaticWaves Forge auto-start complete!"
```

---

### RunPod Template

**File:** `staticwaves-forge/runpod-template.json`

```json
{
  "name": "StaticWaves Forge - AI 3D Asset Generation",
  "description": "Complete StaticWaves Forge platform with unified boot system. Includes Web GUI, API backend, and asset generation pipeline.",
  "version": "1.0.0",
  "category": "AI/ML",
  "image": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
  "env": [
    {
      "key": "NODE_ENV",
      "value": "production"
    },
    {
      "key": "ENVIRONMENT",
      "value": "production"
    },
    {
      "key": "WORKSPACE_DIR",
      "value": "/workspace"
    }
  ],
  "ports": [
    {
      "port": 3000,
      "protocol": "http",
      "description": "Forge Web GUI"
    },
    {
      "port": 8000,
      "protocol": "http",
      "description": "Forge API & Docs"
    },
    {
      "port": 6379,
      "protocol": "tcp",
      "description": "Redis Queue (internal)"
    }
  ],
  "volumeMounts": [
    {
      "containerPath": "/workspace",
      "volumePath": "/workspace"
    }
  ],
  "startScript": "#!/bin/bash\ncd /workspace\n\nif [ ! -d 'staticwaves-forge' ]; then\n  git clone -b claude/ai-3d-asset-engine-Q6XOw https://github.com/ssiens-oss/ssiens-oss-static_pod.git staticwaves-forge\nfi\n\ncd staticwaves-forge/staticwaves-forge\nbash start-unified.sh start\n\n# Keep container alive\ntail -f /tmp/staticwaves-logs/*.log",
  "requirements": {
    "gpu": "Any",
    "minVRAM": 8,
    "minDisk": 50,
    "minRAM": 16
  },
  "readme": "# StaticWaves Forge - One-Click Deployment\n\n## Quick Start\n\n1. Start your RunPod pod with this template\n2. Wait 2-3 minutes for initialization\n3. Access the services:\n\n### Web GUI\n`https://YOUR-POD-ID-3000.proxy.runpod.net`\n\n### API Documentation\n`https://YOUR-POD-ID-8000.proxy.runpod.net/docs`\n\n## Features\n\n- ✨ AI-powered 3D asset generation\n- 🎨 Interactive web GUI with toast notifications\n- 📦 Asset pack creation wizard\n- 📊 Analytics dashboard with charts\n- 🔄 Asset library management\n- ⚙️ Complete settings interface\n\n## Management\n\nSSH into your pod and run:\n\n```bash\n# View status\nbash /workspace/staticwaves-forge/staticwaves-forge/start-unified.sh status\n\n# View logs\nbash /workspace/staticwaves-forge/staticwaves-forge/start-unified.sh logs\n\n# Restart all services\nbash /workspace/staticwaves-forge/staticwaves-forge/start-unified.sh restart\n\n# Stop all services\nbash /workspace/staticwaves-forge/staticwaves-forge/start-unified.sh stop\n```\n\n## Troubleshooting\n\nIf services don't start:\n\n1. Check logs: `tail -f /tmp/staticwaves-logs/*.log`\n2. Restart: `bash start-unified.sh restart`\n3. Manual start: Navigate to `/workspace/staticwaves-forge/staticwaves-forge` and run `bash start-unified.sh`\n\n## Support\n\nGitHub: https://github.com/ssiens-oss/ssiens-oss-static_pod\n"
}
```

---

## Frontend - Next.js Web App

### Generate Page

**File:** `staticwaves-forge/apps/web/app/generate/page.tsx`

```typescript
'use client'

import { useState } from 'react'
import { Sparkles, History, BookOpen, Zap, Layers } from 'lucide-react'
import PromptPanel from '@/components/PromptPanel'
import Viewport3D from '@/components/Viewport3D'
import ExportPanel from '@/components/ExportPanel'
import JobStatus from '@/components/JobStatus'
import { useToast } from '@/components/Toast'

const EXAMPLE_PROMPTS = [
  {
    category: 'Weapons',
    prompts: [
      'A low-poly medieval sword with leather-wrapped grip',
      'Futuristic energy blade with glowing blue core',
      'Ornate fantasy staff with crystal top',
      'Steampunk revolver with brass details'
    ]
  },
  {
    category: 'Creatures',
    prompts: [
      'Stylized dragon with vibrant scales',
      'Cute low-poly fox with bushy tail',
      'Alien creature with bioluminescent features',
      'Mythical phoenix with flame effects'
    ]
  },
  {
    category: 'Props',
    prompts: [
      'Treasure chest overflowing with gold coins',
      'Sci-fi cargo crate with holographic labels',
      'Medieval wooden barrel with iron bands',
      'Cyberpunk vending machine with neon signs'
    ]
  }
]

export default function GeneratePage() {
  const [currentJobId, setCurrentJobId] = useState<string | null>(null)
  const [previewModel, setPreviewModel] = useState<string | null>(null)
  const [showExamples, setShowExamples] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const { showToast } = useToast()

  const handleExampleSelect = (prompt: string) => {
    showToast(`Example loaded: "${prompt.substring(0, 40)}..."`, 'info')
    setShowExamples(false)
  }

  const quickActions = [
    { icon: Sparkles, label: 'Random', tooltip: 'Generate random asset' },
    { icon: Layers, label: 'Batch', tooltip: 'Batch generation' },
    { icon: Zap, label: 'Quick', tooltip: 'Quick generation (low quality)' }
  ]

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4 bg-gray-900/50 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-6 h-6 text-blue-400" />
              <h1 className="text-2xl font-bold">Asset Generator</h1>
            </div>
            <p className="text-sm text-gray-400">Create production-ready 3D assets from prompts</p>
          </div>
          <div className="flex gap-3">
            {/* Quick Actions */}
            {quickActions.map((action) => (
              <button
                key={action.label}
                className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors group"
                title={action.tooltip}
                onClick={() => showToast(`${action.label} mode activated`, 'info')}
              >
                <action.icon className="w-4 h-4" />
                <span className="hidden sm:inline">{action.label}</span>
              </button>
            ))}

            {/* Examples */}
            <div className="relative">
              <button
                onClick={() => setShowExamples(!showExamples)}
                className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <BookOpen className="w-4 h-4" />
                <span className="hidden sm:inline">Examples</span>
              </button>

              {showExamples && (
                <div className="absolute top-full right-0 mt-2 w-80 bg-gray-900 border border-gray-800 rounded-xl shadow-2xl z-50 animate-fade-in">
                  <div className="p-4 border-b border-gray-800">
                    <h3 className="font-semibold">Example Prompts</h3>
                    <p className="text-xs text-gray-400 mt-1">Click to use</p>
                  </div>
                  <div className="max-h-96 overflow-y-auto p-2">
                    {EXAMPLE_PROMPTS.map((category) => (
                      <div key={category.category} className="mb-4">
                        <div className="px-3 py-2 text-sm font-medium text-gray-400">
                          {category.category}
                        </div>
                        <div className="space-y-1">
                          {category.prompts.map((prompt, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleExampleSelect(prompt)}
                              className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors text-sm"
                            >
                              {prompt}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* History */}
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
            >
              <History className="w-4 h-4" />
              <span className="hidden sm:inline">History</span>
            </button>
          </div>
        </div>

        {/* Keyboard Shortcuts Hint */}
        <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <kbd className="px-2 py-1 bg-gray-800 rounded">Ctrl</kbd>
            <span>+</span>
            <kbd className="px-2 py-1 bg-gray-800 rounded">Enter</kbd>
            <span>Generate</span>
          </div>
          <div className="flex items-center gap-1">
            <kbd className="px-2 py-1 bg-gray-800 rounded">Ctrl</kbd>
            <span>+</span>
            <kbd className="px-2 py-1 bg-gray-800 rounded">R</kbd>
            <span>Random</span>
          </div>
          <div className="flex items-center gap-1">
            <kbd className="px-2 py-1 bg-gray-800 rounded">?</kbd>
            <span>Show all shortcuts</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-0">
        {/* Left Panel - Prompt & Controls */}
        <div className="lg:col-span-3 border-r border-gray-800 overflow-y-auto max-h-[calc(100vh-180px)]">
          <PromptPanel onJobCreated={setCurrentJobId} />
        </div>

        {/* Center - 3D Viewport */}
        <div className="lg:col-span-6 relative bg-black min-h-[400px] lg:min-h-0">
          <Viewport3D modelPath={previewModel} />

          {/* Viewport Overlay - Stats */}
          <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2 text-xs font-mono">
            <div className="text-gray-400">Viewport Stats</div>
            <div className="mt-1 space-y-0.5">
              <div>FPS: <span className="text-green-400">60</span></div>
              <div>Triangles: <span className="text-blue-400">{previewModel ? '5.2k' : '0'}</span></div>
            </div>
          </div>

          {/* Viewport Controls Hint */}
          {!previewModel && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center text-gray-500">
                <Sparkles className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="text-lg font-medium mb-2">No model loaded</p>
                <p className="text-sm">Generate an asset to preview it here</p>
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Export & Status */}
        <div className="lg:col-span-3 border-l border-gray-800 overflow-y-auto max-h-[calc(100vh-180px)]">
          <div className="p-6 space-y-6">
            {currentJobId && (
              <>
                <div className="border-b border-gray-800 pb-4">
                  <h3 className="font-semibold mb-1 flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-400" />
                    Generation Status
                  </h3>
                  <p className="text-xs text-gray-400">Real-time progress tracking</p>
                </div>
                <JobStatus
                  jobId={currentJobId}
                  onComplete={(result) => {
                    if (result.output_files?.glb) {
                      setPreviewModel(result.output_files.glb)
                      showToast('Asset generated successfully!', 'success')
                    }
                  }}
                />
              </>
            )}

            {!currentJobId && (
              <div className="text-center py-8 text-gray-500">
                <History className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm">No active generation</p>
                <p className="text-xs mt-1">Start generating to see progress</p>
              </div>
            )}

            <div className="border-t border-gray-800 pt-6">
              <ExportPanel />
            </div>
          </div>
        </div>
      </div>

      {/* History Sidebar */}
      {showHistory && (
        <div className="fixed inset-y-0 right-0 w-80 bg-gray-900 border-l border-gray-800 shadow-2xl z-40 animate-slide-in-right overflow-y-auto">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">Generation History</h2>
              <button
                onClick={() => setShowHistory(false)}
                className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className="bg-gray-800/50 rounded-lg p-3 hover:bg-gray-800 transition-colors cursor-pointer"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded flex items-center justify-center flex-shrink-0">
                      ⚔️
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">Medieval Sword</div>
                      <div className="text-xs text-gray-400 mt-1">2 hours ago</div>
                      <div className="text-xs text-green-400 mt-1">Completed</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Click outside to close dropdowns */}
      {(showExamples || showHistory) && (
        <div
          className="fixed inset-0 z-30"
          onClick={() => {
            setShowExamples(false)
            setShowHistory(false)
          }}
        />
      )}
    </div>
  )
}
```

---

### Prompt Panel Component

**File:** `staticwaves-forge/apps/web/components/PromptPanel.tsx`

```typescript
'use client'

import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface PromptPanelProps {
  onJobCreated: (jobId: string) => void
}

export default function PromptPanel({ onJobCreated }: PromptPanelProps) {
  const [prompt, setPrompt] = useState('')
  const [assetType, setAssetType] = useState('prop')
  const [style, setStyle] = useState('low-poly')
  const [targetEngine, setTargetEngine] = useState('unity')
  const [polyBudget, setPolyBudget] = useState(10000)
  const [includeRig, setIncludeRig] = useState(false)
  const [includeAnimations, setIncludeAnimations] = useState<string[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      alert('Please enter a prompt')
      return
    }

    setIsGenerating(true)

    try {
      const response = await axios.post(`${API_URL}/api/generate/`, {
        prompt,
        asset_type: assetType,
        style,
        target_engine: targetEngine,
        export_formats: ['glb', 'fbx'],
        poly_budget: polyBudget,
        include_rig: includeRig,
        include_animations: includeAnimations,
        generate_lods: true
      })

      onJobCreated(response.data.job_id)
    } catch (error) {
      console.error('Generation error:', error)
      alert('Failed to start generation. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const toggleAnimation = (anim: string) => {
    setIncludeAnimations(prev =>
      prev.includes(anim)
        ? prev.filter(a => a !== anim)
        : [...prev, anim]
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-lg font-semibold mb-4">Asset Configuration</h2>

        {/* Prompt */}
        <div className="space-y-2">
          <label className="text-sm text-gray-400">Describe your asset</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., A stylized fantasy sword with glowing runes..."
            className="w-full h-32 bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:border-blue-500 focus:outline-none resize-none"
          />
        </div>

        {/* Asset Type */}
        <div className="space-y-2 mt-4">
          <label className="text-sm text-gray-400">Asset Type</label>
          <select
            value={assetType}
            onChange={(e) => setAssetType(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="creature">Creature</option>
            <option value="character">Character</option>
            <option value="prop">Prop</option>
            <option value="weapon">Weapon</option>
            <option value="building">Building</option>
            <option value="environment">Environment</option>
            <option value="vehicle">Vehicle</option>
          </select>
        </div>

        {/* Style */}
        <div className="space-y-2 mt-4">
          <label className="text-sm text-gray-400">Style</label>
          <select
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="low-poly">Low Poly</option>
            <option value="realistic">Realistic</option>
            <option value="stylized">Stylized</option>
            <option value="voxel">Voxel</option>
            <option value="toon">Toon</option>
            <option value="roblox-safe">Roblox-Safe</option>
          </select>
        </div>

        {/* Target Engine */}
        <div className="space-y-2 mt-4">
          <label className="text-sm text-gray-400">Target Engine</label>
          <select
            value={targetEngine}
            onChange={(e) => setTargetEngine(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="unity">Unity</option>
            <option value="unreal">Unreal Engine</option>
            <option value="roblox">Roblox</option>
            <option value="godot">Godot</option>
            <option value="generic">Generic</option>
          </select>
        </div>

        {/* Poly Budget */}
        <div className="space-y-2 mt-4">
          <label className="text-sm text-gray-400">Poly Budget: {polyBudget.toLocaleString()}</label>
          <input
            type="range"
            min="1000"
            max="100000"
            step="1000"
            value={polyBudget}
            onChange={(e) => setPolyBudget(parseInt(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>1K</span>
            <span>50K</span>
            <span>100K</span>
          </div>
        </div>

        {/* Rigging */}
        <div className="mt-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={includeRig}
              onChange={(e) => setIncludeRig(e.target.checked)}
              className="w-4 h-4 rounded"
            />
            <span className="text-sm">Include Auto-Rig</span>
          </label>
        </div>

        {/* Animations */}
        {includeRig && (
          <div className="space-y-2 mt-4">
            <label className="text-sm text-gray-400">Animations</label>
            <div className="space-y-2">
              {['idle', 'walk', 'run', 'jump', 'attack'].map(anim => (
                <label key={anim} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeAnimations.includes(anim)}
                    onChange={() => toggleAnimation(anim)}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-sm capitalize">{anim}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="w-full mt-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-semibold transition-colors"
        >
          {isGenerating ? 'Generating...' : 'Generate Asset'}
        </button>
      </div>
    </div>
  )
}
```

---

## Backend - FastAPI

### Main API Entry

**File:** `staticwaves-forge/apps/api/main.py`

```python
"""
StaticWaves Forge - FastAPI Control Plane
Main API server for asset generation orchestration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
import os

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../packages'))

from common.schemas import (
    GenerationRequest,
    GenerationResult,
    JobStatus,
    AssetPackMetadata,
    WorkerStatus
)

from routes import generate, jobs, packs

app = FastAPI(
    title="StaticWaves Forge API",
    description="AI-powered 3D asset generation platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate.router, prefix="/api/generate", tags=["Generation"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(packs.router, prefix="/api/packs", tags=["Packs"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "StaticWaves Forge",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api": "operational",
        "workers": "available",
        "queue": "operational"
    }

@app.get("/api/stats")
async def get_stats():
    """Get platform statistics"""
    return {
        "total_assets_generated": 0,
        "active_jobs": 0,
        "total_packs_created": 0,
        "uptime_seconds": 0
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

---

### Common Schemas

**File:** `staticwaves-forge/packages/common/schemas.py`

```python
"""
StaticWaves Forge - Common Data Schemas
Shared data models and types across the platform
"""

from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class AssetType(str, Enum):
    """Types of 3D assets that can be generated"""
    CREATURE = "creature"
    CHARACTER = "character"
    PROP = "prop"
    WEAPON = "weapon"
    BUILDING = "building"
    ENVIRONMENT = "environment"
    VEHICLE = "vehicle"

class AssetStyle(str, Enum):
    """Visual styles for generated assets"""
    LOW_POLY = "low-poly"
    REALISTIC = "realistic"
    STYLIZED = "stylized"
    VOXEL = "voxel"
    TOON = "toon"
    ROBLOX = "roblox-safe"

class TargetEngine(str, Enum):
    """Target game engines for export"""
    UNITY = "unity"
    UNREAL = "unreal"
    ROBLOX = "roblox"
    GODOT = "godot"
    GENERIC = "generic"

class ExportFormat(str, Enum):
    """Export file formats"""
    GLB = "glb"
    FBX = "fbx"
    OBJ = "obj"
    GLTF = "gltf"
    BLEND = "blend"

class AnimationType(str, Enum):
    """Types of animations to generate"""
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    JUMP = "jump"
    ATTACK = "attack"
    EMOTE = "emote"
    CUSTOM = "custom"

class JobStatus(str, Enum):
    """Asset generation job statuses"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class GenerationRequest(BaseModel):
    """Request to generate a 3D asset"""
    prompt: str = Field(..., description="Text description of the asset to generate")
    asset_type: AssetType = Field(default=AssetType.PROP)
    style: AssetStyle = Field(default=AssetStyle.LOW_POLY)
    target_engine: TargetEngine = Field(default=TargetEngine.UNITY)
    export_formats: List[ExportFormat] = Field(default=[ExportFormat.GLB, ExportFormat.FBX])
    poly_budget: Optional[int] = Field(default=10000, description="Target polygon count")
    include_rig: bool = Field(default=False)
    include_animations: List[AnimationType] = Field(default=[])
    generate_lods: bool = Field(default=True)
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")

    class Config:
        use_enum_values = True

class AssetMetadata(BaseModel):
    """Metadata about a generated asset"""
    asset_id: str
    name: str
    asset_type: AssetType
    style: AssetStyle
    poly_count: int
    vertex_count: int
    has_rig: bool
    animations: List[str]
    file_size_mb: float
    created_at: str
    seed: int

class GenerationResult(BaseModel):
    """Result of an asset generation job"""
    job_id: str
    status: JobStatus
    asset_metadata: Optional[AssetMetadata] = None
    output_files: Dict[str, str] = Field(default={}, description="Format -> file path")
    error_message: Optional[str] = None
    progress: float = Field(default=0.0, ge=0.0, le=1.0)

    class Config:
        use_enum_values = True

class AssetPackMetadata(BaseModel):
    """Metadata for an asset pack"""
    pack_id: str
    name: str
    description: str
    price: float
    asset_count: int
    tags: List[str]
    version: str
    created_at: str
    formats: List[str]
    total_size_mb: float

class WorkerStatus(BaseModel):
    """Status of a Blender worker instance"""
    worker_id: str
    status: str
    current_job: Optional[str] = None
    jobs_completed: int = 0
    uptime_seconds: float = 0
    gpu_name: Optional[str] = None
    gpu_utilization: Optional[float] = None
```

---

### Generation Routes

**File:** `staticwaves-forge/apps/api/routes/generate.py`

```python
"""
StaticWaves Forge - Generation Routes
Endpoints for creating new 3D assets
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import uuid
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../packages'))

from common.schemas import (
    GenerationRequest,
    GenerationResult,
    JobStatus,
    AssetMetadata
)

router = APIRouter()

# In-memory job storage (replace with Redis/DB in production)
active_jobs = {}

async def process_generation_job(job_id: str, request: GenerationRequest):
    """
    Background task to process asset generation
    In production, this would dispatch to RunPod workers via queue
    """
    try:
        # Update job status
        active_jobs[job_id]["status"] = JobStatus.PROCESSING
        active_jobs[job_id]["progress"] = 0.1

        # Simulate processing stages
        time.sleep(2)  # Simulate mesh generation
        active_jobs[job_id]["progress"] = 0.4

        time.sleep(1)  # Simulate rigging
        active_jobs[job_id]["progress"] = 0.6

        time.sleep(1)  # Simulate animation
        active_jobs[job_id]["progress"] = 0.8

        time.sleep(1)  # Simulate export
        active_jobs[job_id]["progress"] = 1.0

        # Create mock asset metadata
        asset_metadata = AssetMetadata(
            asset_id=job_id,
            name=f"asset_{job_id[:8]}",
            asset_type=request.asset_type,
            style=request.style,
            poly_count=request.poly_budget or 10000,
            vertex_count=(request.poly_budget or 10000) * 3,
            has_rig=request.include_rig,
            animations=[str(anim) for anim in request.include_animations],
            file_size_mb=2.5,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            seed=request.seed or 42
        )

        # Mock output files
        output_files = {
            str(fmt): f"/output/{job_id}/{job_id}.{str(fmt)}"
            for fmt in request.export_formats
        }

        # Update job as completed
        active_jobs[job_id]["status"] = JobStatus.COMPLETED
        active_jobs[job_id]["asset_metadata"] = asset_metadata
        active_jobs[job_id]["output_files"] = output_files

    except Exception as e:
        active_jobs[job_id]["status"] = JobStatus.FAILED
        active_jobs[job_id]["error_message"] = str(e)

@router.post("/", response_model=GenerationResult)
async def create_generation_job(
    request: GenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new asset generation job
    """
    # Generate job ID
    job_id = str(uuid.uuid4())

    # Set seed if not provided
    if request.seed is None:
        request.seed = int(time.time() * 1000) % 2147483647

    # Create job record
    job_result = GenerationResult(
        job_id=job_id,
        status=JobStatus.QUEUED,
        progress=0.0
    )

    active_jobs[job_id] = job_result.dict()

    # Queue background processing
    background_tasks.add_task(process_generation_job, job_id, request)

    return job_result

@router.post("/batch", response_model=list[GenerationResult])
async def create_batch_generation(
    requests: list[GenerationRequest],
    background_tasks: BackgroundTasks
):
    """
    Create multiple asset generation jobs at once
    """
    results = []

    for req in requests:
        job_id = str(uuid.uuid4())

        if req.seed is None:
            req.seed = int(time.time() * 1000) % 2147483647

        job_result = GenerationResult(
            job_id=job_id,
            status=JobStatus.QUEUED,
            progress=0.0
        )

        active_jobs[job_id] = job_result.dict()
        background_tasks.add_task(process_generation_job, job_id, req)

        results.append(job_result)

    return results

@router.get("/quick", response_model=GenerationResult)
async def quick_generate(
    prompt: str,
    asset_type: str = "prop",
    background_tasks: BackgroundTasks = None
):
    """
    Quick generation endpoint with minimal parameters
    """
    request = GenerationRequest(
        prompt=prompt,
        asset_type=asset_type,
        style="low-poly",
        export_formats=["glb"]
    )

    return await create_generation_job(request, background_tasks)
```

---

## Docker & CI/CD

### Web Dockerfile

**File:** `staticwaves-forge/apps/web/Dockerfile`

```dockerfile
# Stage 1: Build the Next.js application
FROM node:20-bullseye AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production runtime
FROM node:20-bullseye-slim

WORKDIR /app

# Set environment to production
ENV NODE_ENV=production

# Copy built application from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/public ./public

# Expose port 3000
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start the application
CMD ["npm", "run", "start"]
```

---

### API Dockerfile

**File:** `staticwaves-forge/apps/api/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy packages
COPY ../../packages /app/packages

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

### Production Docker Compose

**File:** `staticwaves-forge/docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  web:
    image: ghcr.io/${GITHUB_REPOSITORY}/web:${VERSION:-latest}
    container_name: staticwaves-web
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://api:8000
    depends_on:
      - api
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"]
      interval: 30s
      timeout: 3s
      start_period: 40s
      retries: 3
    networks:
      - staticwaves

  api:
    image: ghcr.io/${GITHUB_REPOSITORY}/api:${VERSION:-latest}
    container_name: staticwaves-api
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"]
      interval: 30s
      timeout: 3s
      start_period: 30s
      retries: 3
    networks:
      - staticwaves

  redis:
    image: redis:7-alpine
    container_name: staticwaves-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    networks:
      - staticwaves

networks:
  staticwaves:
    driver: bridge

volumes:
  redis_data:
```

---

### GitHub Actions Workflow

**File:** `.github/workflows/docker-release.yml`

```yaml
name: Build & Push StaticWaves Images

on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version tag (e.g., v1.0.0)'
        required: true
        type: string

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    strategy:
      matrix:
        service: [web, api]

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract version from tag
        id: version
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            VERSION="${{ github.event.inputs.version }}"
          else
            VERSION=${GITHUB_REF#refs/tags/}
          fi
          echo "VERSION=$VERSION" >> $GITHUB_OUTPUT

          # Generate additional tags
          MAJOR=$(echo $VERSION | sed 's/v\([0-9]*\).*/\1/')
          MINOR=$(echo $VERSION | sed 's/v\([0-9]*\)\.\([0-9]*\).*/\1.\2/')
          echo "MAJOR=$MAJOR" >> $GITHUB_OUTPUT
          echo "MINOR=$MINOR" >> $GITHUB_OUTPUT

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./staticwaves-forge/apps/${{ matrix.service }}
          file: ./staticwaves-forge/apps/${{ matrix.service }}/Dockerfile
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:${{ steps.version.outputs.VERSION }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:${{ steps.version.outputs.MINOR }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:${{ steps.version.outputs.MAJOR }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:main-${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          labels: |
            org.opencontainers.image.title=StaticWaves Forge ${{ matrix.service }}
            org.opencontainers.image.description=AI 3D Asset Generation - ${{ matrix.service }}
            org.opencontainers.image.version=${{ steps.version.outputs.VERSION }}
            org.opencontainers.image.source=${{ github.server_url }}/${{ github.repository }}

      - name: Generate deployment summary
        run: |
          echo "### 🚀 Deployment Summary - ${{ matrix.service }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Version**: ${{ steps.version.outputs.VERSION }}" >> $GITHUB_STEP_SUMMARY
          echo "**Service**: ${{ matrix.service }}" >> $GITHUB_STEP_SUMMARY
          echo "**Registry**: ${{ env.REGISTRY }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Image Tags**:" >> $GITHUB_STEP_SUMMARY
          echo "- \`${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:${{ steps.version.outputs.VERSION }}\`" >> $GITHUB_STEP_SUMMARY
          echo "- \`${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:${{ steps.version.outputs.MINOR }}\`" >> $GITHUB_STEP_SUMMARY
          echo "- \`${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:${{ steps.version.outputs.MAJOR }}\`" >> $GITHUB_STEP_SUMMARY
          echo "- \`${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:latest\`" >> $GITHUB_STEP_SUMMARY
```

---

## End of Code Reference

This document contains all major code files for the StaticWaves Forge platform. For additional documentation, see:

- `ONE_CLICK_DEPLOY.md` - Deployment guide
- `PRODUCTION_DEPLOYMENT.md` - Production deployment procedures
- API docs at `http://localhost:8000/docs` when running

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Repository**: https://github.com/ssiens-oss/ssiens-oss-static_pod

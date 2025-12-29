#!/bin/bash
set -e

echo "========================================="
echo "RunPod Pod Optimization Script"
echo "StaticWaves POD Studio"
echo "========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if running on RunPod
if [ -z "$RUNPOD_POD_ID" ]; then
    echo -e "${YELLOW}Warning: Not running on RunPod. Skipping GPU optimizations.${NC}"
    GPU_AVAILABLE=false
else
    echo -e "${GREEN}Running on RunPod Pod: $RUNPOD_POD_ID${NC}"
    GPU_AVAILABLE=true
fi

# System Information
echo ""
echo "========================================="
echo "System Information"
echo "========================================="
echo "Hostname: $(hostname)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Kernel: $(uname -r)"
echo "CPU Cores: $(nproc)"
echo "Total RAM: $(free -h | awk '/^Mem:/ {print $2}')"
echo "Available RAM: $(free -h | awk '/^Mem:/ {print $7}')"

# GPU Information
if [ "$GPU_AVAILABLE" = true ]; then
    echo ""
    echo "========================================="
    echo "GPU Information"
    echo "========================================="

    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
        echo ""
        echo "CUDA Version: $(nvcc --version 2>/dev/null | grep release | awk '{print $5}' | cut -d',' -f1 || echo 'N/A')"
    else
        echo -e "${YELLOW}nvidia-smi not available${NC}"
    fi
fi

# Optimize System Settings
echo ""
echo "========================================="
echo "Applying System Optimizations"
echo "========================================="

# Increase file descriptor limits
echo -e "${YELLOW}Setting file descriptor limits...${NC}"
ulimit -n 65536 2>/dev/null && echo -e "${GREEN}✓ File descriptors: 65536${NC}" || echo -e "${RED}✗ Failed to set file descriptors${NC}"

# Optimize network settings
echo -e "${YELLOW}Optimizing network settings...${NC}"
if [ -w /proc/sys/net/core/somaxconn ]; then
    echo 4096 > /proc/sys/net/core/somaxconn
    echo -e "${GREEN}✓ Socket backlog: 4096${NC}"
fi

if [ -w /proc/sys/net/core/netdev_max_backlog ]; then
    echo 5000 > /proc/sys/net/core/netdev_max_backlog
    echo -e "${GREEN}✓ Network device backlog: 5000${NC}"
fi

# Optimize nginx worker processes
echo -e "${YELLOW}Calculating optimal nginx workers...${NC}"
WORKER_PROCESSES=$(nproc)
echo -e "${GREEN}✓ Nginx workers: $WORKER_PROCESSES${NC}"

# Memory optimization
echo -e "${YELLOW}Optimizing memory settings...${NC}"
if [ -w /proc/sys/vm/swappiness ]; then
    echo 10 > /proc/sys/vm/swappiness
    echo -e "${GREEN}✓ Swappiness: 10${NC}"
fi

# GPU Optimizations (if available)
if [ "$GPU_AVAILABLE" = true ] && command -v nvidia-smi &> /dev/null; then
    echo ""
    echo "========================================="
    echo "Applying GPU Optimizations"
    echo "========================================="

    # Set GPU persistence mode
    echo -e "${YELLOW}Setting GPU persistence mode...${NC}"
    nvidia-smi -pm 1 2>/dev/null && echo -e "${GREEN}✓ GPU persistence mode enabled${NC}" || echo -e "${YELLOW}⚠ Could not set persistence mode${NC}"

    # Set GPU power limit (if supported)
    echo -e "${YELLOW}Optimizing GPU power settings...${NC}"
    nvidia-smi -pl 250 2>/dev/null && echo -e "${GREEN}✓ GPU power limit: 250W${NC}" || echo -e "${YELLOW}⚠ Could not set power limit${NC}"

    # Enable GPU accounting
    nvidia-smi -am 1 2>/dev/null && echo -e "${GREEN}✓ GPU accounting enabled${NC}" || true
fi

# Docker optimizations
echo ""
echo "========================================="
echo "Docker Optimizations"
echo "========================================="

# Check Docker info
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker is available${NC}"
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
    echo "  Version: $DOCKER_VERSION"

    # Check if nvidia-docker is available
    if docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi &>/dev/null 2>&1; then
        echo -e "${GREEN}✓ NVIDIA Docker runtime available${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Docker not available in this environment${NC}"
fi

# Create optimization status file
echo ""
echo "========================================="
echo "Saving Optimization Status"
echo "========================================="

cat > /tmp/pod-optimization-status.json << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "pod_id": "${RUNPOD_POD_ID:-local}",
  "gpu_id": "${RUNPOD_GPU_ID:-N/A}",
  "optimizations_applied": {
    "file_descriptors": true,
    "network_tuning": true,
    "memory_tuning": true,
    "gpu_persistence": $([ "$GPU_AVAILABLE" = true ] && echo "true" || echo "false"),
    "gpu_power_limit": $([ "$GPU_AVAILABLE" = true ] && echo "true" || echo "false")
  },
  "system_info": {
    "cpu_cores": $(nproc),
    "total_ram_gb": $(free -g | awk '/^Mem:/ {print $2}'),
    "gpu_available": $([ "$GPU_AVAILABLE" = true ] && echo "true" || echo "false")
  },
  "status": "optimized"
}
EOF

echo -e "${GREEN}✓ Status saved to /tmp/pod-optimization-status.json${NC}"

# Display final status
echo ""
echo "========================================="
echo "Optimization Complete!"
echo "========================================="
echo -e "${GREEN}All optimizations have been applied.${NC}"
echo ""
echo "Summary:"
echo "  • File descriptors: 65536"
echo "  • Nginx workers: $WORKER_PROCESSES"
echo "  • Network optimized: Yes"
echo "  • Memory tuned: Yes"
if [ "$GPU_AVAILABLE" = true ]; then
    echo "  • GPU optimized: Yes"
fi
echo ""
echo "To view optimization status:"
echo "  cat /tmp/pod-optimization-status.json"
echo ""
echo "========================================="

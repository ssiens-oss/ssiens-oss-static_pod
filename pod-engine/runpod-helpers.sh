#!/usr/bin/env bash
###############################################################################
# StaticWaves POD Engine - RunPod Helper Scripts
# Common management commands for RunPod deployment
###############################################################################

WORKSPACE="${WORKSPACE:-/workspace}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  $1${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
}

# Check system health
check_health() {
    print_header "System Health Check"

    echo "📊 Service Status:"
    supervisorctl status

    echo ""
    echo "💾 Disk Usage:"
    df -h "$WORKSPACE" | tail -1

    echo ""
    echo "🧠 Memory Usage:"
    free -h | grep Mem

    echo ""
    echo "🎮 GPU Status:"
    nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader

    echo ""
    echo "📦 Queue Status:"
    echo "  Incoming:  $(ls -1 $WORKSPACE/queues/incoming 2>/dev/null | wc -l) files"
    echo "  Done:      $(ls -1 $WORKSPACE/queues/done 2>/dev/null | wc -l) files"
    echo "  Failed:    $(ls -1 $WORKSPACE/queues/failed 2>/dev/null | wc -l) files"
    echo "  Published: $(ls -1 $WORKSPACE/queues/published 2>/dev/null | wc -l) files"
}

# Restart all services
restart_all() {
    print_header "Restarting All Services"
    supervisorctl restart staticwaves:*
    sleep 3
    supervisorctl status
}

# Clean queues
clean_queues() {
    print_header "Cleaning Queues"

    read -p "Clean failed queue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$WORKSPACE/queues/failed/"*
        echo -e "${GREEN}✅ Failed queue cleared${NC}"
    fi

    read -p "Clean done queue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$WORKSPACE/queues/done/"*
        echo -e "${GREEN}✅ Done queue cleared${NC}"
    fi
}

# View logs
view_logs() {
    print_header "Service Logs"

    echo "1) ComfyUI"
    echo "2) POD API"
    echo "3) Printify Worker"
    echo "4) Shopify Worker"
    echo "5) All logs"

    read -p "Select log to view: " choice

    case $choice in
        1) tail -f "$WORKSPACE/logs/comfyui.log" ;;
        2) tail -f "$WORKSPACE/logs/pod-api.log" ;;
        3) tail -f "$WORKSPACE/logs/printify.log" ;;
        4) tail -f "$WORKSPACE/logs/shopify.log" ;;
        5) tail -f "$WORKSPACE/logs/"*.log ;;
        *) echo -e "${RED}Invalid choice${NC}" ;;
    esac
}

# Backup to S3
backup() {
    print_header "Backup to S3"

    if ! command -v rclone &> /dev/null; then
        echo -e "${YELLOW}Installing rclone...${NC}"
        apt-get install -y rclone
    fi

    if [ ! -f ~/.config/rclone/rclone.conf ]; then
        echo -e "${YELLOW}Configure rclone first:${NC}"
        echo "  rclone config"
        exit 1
    fi

    TIMESTAMP=$(date +%Y%m%d_%H%M%S)

    echo "Backing up pod-engine..."
    rclone sync "$WORKSPACE/pod-engine" s3:staticwaves-backup/pod-engine-$TIMESTAMP

    echo "Backing up queues..."
    rclone sync "$WORKSPACE/queues" s3:staticwaves-backup/queues-$TIMESTAMP

    echo -e "${GREEN}✅ Backup complete!${NC}"
}

# Quick status
quick_status() {
    curl -s http://localhost:8000/health | python3 -m json.tool
}

# Create client
create_client() {
    print_header "Create Client Workspace"

    read -p "Client ID (e.g., client_acme): " client_id
    read -p "Monthly product limit: " limit

    python3 << EOF
import json
from pathlib import Path

client = "$client_id"
limit = int("$limit")

base = Path("$WORKSPACE/clients/$client_id")
base.mkdir(parents=True, exist_ok=True)

for d in ["queues/incoming", "queues/done", "queues/failed", "queues/published", "outputs"]:
    (base / d).mkdir(parents=True, exist_ok=True)

limits = {
    "products_per_month": limit,
    "gpu_minutes": limit * 10,
    "api_calls": limit * 20
}

(base / "limits.json").write_text(json.dumps(limits, indent=2))
(base / ".env").write_text(f"CLIENT_ID={client}\n")

print(f"✅ Created client workspace: {base}")
print(f"   Limits: {limits}")
EOF
}

# Show menu
show_menu() {
    clear
    print_header "StaticWaves POD Engine - RunPod Management"

    echo "1) Check Health"
    echo "2) Restart All Services"
    echo "3) View Logs"
    echo "4) Clean Queues"
    echo "5) Quick Status"
    echo "6) Create Client"
    echo "7) Backup to S3"
    echo "8) GPU Monitor"
    echo "9) Exit"
    echo ""
    read -p "Select option: " choice

    case $choice in
        1) check_health ;;
        2) restart_all ;;
        3) view_logs ;;
        4) clean_queues ;;
        5) quick_status ;;
        6) create_client ;;
        7) backup ;;
        8) watch -n 1 nvidia-smi ;;
        9) exit 0 ;;
        *) echo -e "${RED}Invalid choice${NC}"; sleep 2 ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
}

# Main loop
if [ "$1" == "" ]; then
    while true; do
        show_menu
    done
else
    # Direct command
    case $1 in
        health) check_health ;;
        restart) restart_all ;;
        logs) view_logs ;;
        clean) clean_queues ;;
        status) quick_status ;;
        backup) backup ;;
        *) echo "Unknown command: $1" ;;
    esac
fi

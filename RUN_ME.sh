#!/bin/bash
# Simple launcher script you can run from anywhere

echo "🚀 Pod Engine Launcher"
echo ""
echo "Project location: /home/user/ssiens-oss-static_pod"
echo ""

cd /home/user/ssiens-oss-static_pod || {
    echo "❌ Error: Cannot access project directory"
    echo "Current directory: $(pwd)"
    echo "User: $(whoami)"
    exit 1
}

echo "✅ Successfully entered project directory"
echo ""

PS3="Select an option: "
options=("Setup (First Time)" "Start Services" "Stop Services" "Check Status" "View Logs" "Exit")

select opt in "${options[@]}"
do
    case $opt in
        "Setup (First Time)")
            echo "Running setup..."
            ./scripts/setup-pod-engine.sh
            break
            ;;
        "Start Services")
            echo "Starting all services..."
            ./scripts/start-pod-engine.sh
            break
            ;;
        "Stop Services")
            echo "Stopping all services..."
            ./scripts/stop-pod-engine.sh
            break
            ;;
        "Check Status")
            echo "Checking service status..."
            echo ""
            echo "=== Running Processes ==="
            ps aux | grep -E "comfyui|uvicorn|redis|music-engine" | grep -v grep
            echo ""
            echo "=== Port Usage ==="
            netstat -tuln | grep -E "8188|8000|6379" || lsof -i -P -n | grep -E "8188|8000|6379"
            break
            ;;
        "View Logs")
            echo "Select log to view:"
            echo "1) Music Worker"
            echo "2) ComfyUI"
            echo "3) Music API"
            echo "4) Redis"
            read -p "Choice: " logchoice
            case $logchoice in
                1) tail -f logs/music-worker.log ;;
                2) tail -f logs/comfyui.log ;;
                3) tail -f logs/music-api.log ;;
                4) tail -f logs/redis.log ;;
            esac
            break
            ;;
        "Exit")
            break
            ;;
        *) echo "Invalid option $REPLY";;
    esac
done

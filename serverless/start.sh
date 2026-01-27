#!/bin/bash
set -e

echo "Starting ComfyUI..."
cd /workspace/ComfyUI
python main.py --listen 127.0.0.1 --port 8188 &
COMFYUI_PID=$!

echo "Waiting for ComfyUI to be ready..."
for i in {1..60}; do
    if curl -sf http://127.0.0.1:8188/system_stats > /dev/null 2>&1; then
        echo "ComfyUI is ready!"
        break
    fi
    sleep 2
done

echo "Starting RunPod handler..."
python /handler.py

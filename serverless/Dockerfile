# RunPod Serverless ComfyUI Handler
# Deploy this to your RunPod serverless endpoint

FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

ENV COMFYUI_PATH=/workspace/ComfyUI
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Clone and setup ComfyUI
WORKDIR /workspace
RUN git clone https://github.com/comfyanonymous/ComfyUI.git

WORKDIR ${COMFYUI_PATH}
RUN pip install -r requirements.txt

# Install RunPod SDK
RUN pip install runpod requests

# Copy handler
COPY handler.py /handler.py

# Create output directory
RUN mkdir -p ${COMFYUI_PATH}/output

# Start script that runs both ComfyUI and handler
COPY <<'EOF' /start.sh
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
EOF

RUN chmod +x /start.sh

CMD ["/start.sh"]

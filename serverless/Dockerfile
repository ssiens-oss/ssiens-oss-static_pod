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

# Copy handler and start script
COPY handler.py /handler.py
COPY start.sh /start.sh

# Create output directory and set permissions
RUN mkdir -p ${COMFYUI_PATH}/output && chmod +x /start.sh

CMD ["/start.sh"]

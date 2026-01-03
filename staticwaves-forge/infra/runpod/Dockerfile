# StaticWaves Forge - RunPod Worker Image
# Optimized for GPU-accelerated 3D asset generation with Blender

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

LABEL maintainer="StaticWaves <dev@staticwaves.io>"
LABEL description="AI-powered 3D asset generation worker"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    blender \
    python3.10 \
    python3-pip \
    git \
    wget \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /worker

# Copy Python packages
COPY ../../packages ./packages

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn==0.27.0 \
    redis==5.0.1 \
    boto3==1.34.34 \
    requests==2.31.0 \
    pydantic==2.5.3 \
    numpy \
    trimesh

# Copy worker scripts
COPY start_worker.sh .
COPY worker.py .

# Make scripts executable
RUN chmod +x start_worker.sh

# Set environment variables
ENV BLENDER_PATH=/usr/bin/blender
ENV PYTHONUNBUFFERED=1

# Expose port for worker status API
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start worker
CMD ["./start_worker.sh"]

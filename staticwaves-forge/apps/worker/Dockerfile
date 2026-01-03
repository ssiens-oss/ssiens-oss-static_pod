# StaticWaves Forge Worker - Docker Image
# Includes Blender + Python + AI Models

FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV BLENDER_VERSION=3.6
ENV BLENDER_PATH=/usr/local/blender/blender

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    xz-utils \
    libx11-6 \
    libxi6 \
    libxxf86vm1 \
    libxfixes3 \
    libxrender1 \
    libgl1 \
    libglu1-mesa \
    libsm6 \
    python3.10 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Download and install Blender
RUN wget -q https://download.blender.org/release/Blender${BLENDER_VERSION}/blender-${BLENDER_VERSION}.5-linux-x64.tar.xz && \
    tar -xf blender-${BLENDER_VERSION}.5-linux-x64.tar.xz && \
    mv blender-${BLENDER_VERSION}.5-linux-x64 /usr/local/blender && \
    rm blender-${BLENDER_VERSION}.5-linux-x64.tar.xz && \
    ln -s /usr/local/blender/blender /usr/local/bin/blender

# Set working directory
WORKDIR /app

# Copy worker code
COPY . /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Blender Python packages
RUN /usr/local/blender/3.6/python/bin/python3.10 -m pip install --upgrade pip && \
    /usr/local/blender/3.6/python/bin/python3.10 -m pip install numpy trimesh

# Create output directory
RUN mkdir -p /workspace/generated_assets

# Environment variables
ENV WORKER_TYPE=docker
ENV OUTPUT_DIR=/workspace/generated_assets
ENV BLENDER_PATH=/usr/local/blender/blender

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD python3 -c "import redis; redis.from_url('${REDIS_URL}').ping()" || exit 1

# Run worker
CMD ["python3", "worker.py"]

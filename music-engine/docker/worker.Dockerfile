# StaticWaves Music Worker - GPU-accelerated
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY music-engine/requirements-worker.txt .
RUN pip3 install --no-cache-dir -r requirements-worker.txt

# Copy application code
COPY music-engine/worker /app/worker
COPY music-engine/shared /app/shared

# Create output directory
RUN mkdir -p /data/output

# Run worker
CMD ["python3", "worker/worker.py"]

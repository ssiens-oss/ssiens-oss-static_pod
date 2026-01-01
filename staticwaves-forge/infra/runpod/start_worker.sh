#!/bin/bash
# StaticWaves Forge - Worker Startup Script

set -e

echo "🔥 StaticWaves Forge Worker Starting..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Environment info
echo "📍 Environment:"
echo "   - CUDA: $(nvcc --version 2>/dev/null | grep release || echo 'Not available')"
echo "   - Blender: $(blender --version 2>/dev/null | head -n1 || echo 'Not available')"
echo "   - Python: $(python3 --version)"
echo "   - Worker ID: ${RUNPOD_POD_ID:-local}"

# Set defaults
export WORKER_ID="${RUNPOD_POD_ID:-worker-$(hostname)}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379}"
export S3_BUCKET="${S3_BUCKET:-staticwaves-assets}"
export OUTPUT_DIR="${OUTPUT_DIR:-/output}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  Configuration:"
echo "   - Worker ID: $WORKER_ID"
echo "   - Redis: $REDIS_URL"
echo "   - S3 Bucket: $S3_BUCKET"
echo "   - Output: $OUTPUT_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# GPU check
if command -v nvidia-smi &> /dev/null; then
    echo "🎮 GPU Status:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "⚠️  No GPU detected (CPU mode)"
fi

# Start worker
echo "✅ Worker ready. Starting job processor..."
echo ""

python3 worker.py

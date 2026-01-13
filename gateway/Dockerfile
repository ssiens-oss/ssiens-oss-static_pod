# POD Gateway Dockerfile - Standalone Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ ./app/
COPY templates/ ./templates/
COPY .env.example .env.example

# Create necessary directories
RUN mkdir -p /app/data/images /app/data/state /app/data/archive

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV POD_IMAGE_DIR=/app/data/images
ENV POD_STATE_FILE=/app/data/state/state.json
ENV POD_ARCHIVE_DIR=/app/data/archive
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run as non-root user
RUN useradd -m -u 1000 poduser && \
    chown -R poduser:poduser /app
USER poduser

# Start the application
CMD ["python", "-u", "app/main.py"]

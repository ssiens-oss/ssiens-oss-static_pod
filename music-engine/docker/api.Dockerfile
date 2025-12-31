# StaticWaves Music API - FastAPI Server
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY music-engine/requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy application code
COPY music-engine/api /app/api
COPY music-engine/shared /app/shared

# Expose port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

"""
StaticWaves Forge - FastAPI Control Plane
Main API server for asset generation orchestration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
import os

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../packages'))

from common.schemas import (
    GenerationRequest,
    GenerationResult,
    JobStatus,
    AssetPackMetadata,
    WorkerStatus
)

from routes import generate, jobs, packs

app = FastAPI(
    title="StaticWaves Forge API",
    description="AI-powered 3D asset generation platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate.router, prefix="/api/generate", tags=["Generation"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(packs.router, prefix="/api/packs", tags=["Packs"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "StaticWaves Forge",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api": "operational",
        "workers": "available",  # TODO: Check actual worker status
        "queue": "operational"   # TODO: Check Redis/queue status
    }

@app.get("/api/stats")
async def get_stats():
    """Get platform statistics"""
    return {
        "total_assets_generated": 0,  # TODO: Implement counter
        "active_jobs": 0,
        "total_packs_created": 0,
        "uptime_seconds": 0
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

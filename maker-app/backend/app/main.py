"""
StaticWaves Maker - FastAPI Application
Main backend server for image, video, music, and book generation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.database import init_db
from app.routes import maker, billing, rewards, library

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="StaticWaves Maker API",
    description="AI-powered content generation API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize database
@app.on_event("startup")
async def startup():
    logger.info("Starting StaticWaves Maker API")
    init_db()
    logger.info("Database initialized")


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "maker-api",
        "version": "1.0.0"
    }


# Include routers
app.include_router(maker.router)
app.include_router(billing.router)
app.include_router(rewards.router)
app.include_router(library.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

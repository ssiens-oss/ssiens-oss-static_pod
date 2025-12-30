"""
Main FastAPI Application - Automated Dropshipping Platform
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from config.settings import settings
from api import (
    shopify_router,
    aliexpress_router,
    tiktok_router,
    printify_router,
    products_router,
    orders_router,
    automation_router,
    analytics_router,
)


# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO" if not settings.DEBUG else "DEBUG",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Automated dropshipping platform with multi-platform integration",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Include routers
app.include_router(shopify_router.router, prefix="/api/shopify", tags=["Shopify"])
app.include_router(aliexpress_router.router, prefix="/api/aliexpress", tags=["AliExpress"])
app.include_router(tiktok_router.router, prefix="/api/tiktok", tags=["TikTok"])
app.include_router(printify_router.router, prefix="/api/printify", tags=["Printify"])
app.include_router(products_router.router, prefix="/api/products", tags=["Products"])
app.include_router(orders_router.router, prefix="/api/orders", tags=["Orders"])
app.include_router(automation_router.router, prefix="/api/automation", tags=["Automation"])
app.include_router(analytics_router.router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Automated Dropshipping Platform API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )

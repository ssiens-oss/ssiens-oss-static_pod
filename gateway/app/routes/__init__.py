"""
Flask Routes

Blueprint-based route organization for the POD Gateway API.
"""
from app.routes.api import api_bp
from app.routes.health import health_bp

__all__ = ["api_bp", "health_bp"]

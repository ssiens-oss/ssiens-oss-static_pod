"""
StaticWaves TikTok Integration API Server
==========================================
Flask application entry point for TikTok Shop automation API.

Usage:
    # Development
    python app.py

    # Production (with gunicorn)
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
"""

import os
from pathlib import Path

try:
    from flask import Flask, jsonify
    from flask_cors import CORS
except ImportError:
    print("❌ Flask not installed. Run: pip install flask flask-cors")
    exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️  python-dotenv not installed. Run: pip install python-dotenv")
    load_dotenv = None

from api.routes_tiktok import tiktok_bp
from core.logger import get_logger

# Load environment variables
if load_dotenv:
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"✅ Loaded environment from {env_path}")
    else:
        print(f"⚠️  No .env file found. Using system environment variables.")

# Initialize logger
log = get_logger("FLASK-APP")

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# CORS configuration
cors_origins = os.getenv('CORS_ORIGINS', '*')
if cors_origins != '*':
    cors_origins = cors_origins.split(',')

CORS(app, origins=cors_origins)

# Register blueprints
app.register_blueprint(tiktok_bp, url_prefix='/api')

log.info("✅ TikTok API blueprint registered at /api")


# Root endpoint
@app.route('/')
def index():
    """API index with available endpoints."""
    return jsonify({
        "service": "StaticWaves TikTok Integration API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "status": "/api/tiktok/status",
            "mode": "/api/tiktok/mode",
            "config": "/api/tiktok/config",
            "generate": "/api/tiktok/generate",
            "upload": "/api/tiktok/upload",
            "health": "/api/tiktok/health"
        },
        "docs": "See TIKTOK_README.md for full documentation"
    }), 200


# Health check
@app.route('/health')
def health():
    """Global health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "tiktok-integration-api"
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": [
            "/",
            "/health",
            "/api/tiktok/status",
            "/api/tiktok/mode",
            "/api/tiktok/config",
            "/api/tiktok/generate",
            "/api/tiktok/upload"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    log.error(f"Internal server error: {str(e)}")
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500


if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'

    log.info("=" * 60)
    log.info("🚀 Starting StaticWaves TikTok Integration API")
    log.info("=" * 60)
    log.info(f"📍 Host: {host}")
    log.info(f"🔌 Port: {port}")
    log.info(f"🐛 Debug: {debug}")
    log.info(f"🌍 CORS Origins: {cors_origins}")
    log.info("=" * 60)
    log.info("")
    log.info("📚 API Documentation: TIKTOK_README.md")
    log.info("🔧 Configuration: .env")
    log.info("")

    # Run Flask development server
    app.run(
        host=host,
        port=port,
        debug=debug
    )

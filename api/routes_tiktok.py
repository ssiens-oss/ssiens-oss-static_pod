"""
TikTok Shop API Routes
======================
Flask Blueprint for TikTok integration REST API.

Endpoints:
- GET  /tiktok/status       - System status and configuration
- GET  /tiktok/mode         - Safe mode status
- POST /tiktok/mode         - Toggle safe mode
- POST /tiktok/generate     - Generate product feed
- POST /tiktok/upload       - Upload products to TikTok
- GET  /tiktok/config       - Get firewall and price config

Usage:
    from api.routes_tiktok import tiktok_bp
    app.register_blueprint(tiktok_bp, url_prefix="/api")
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from flask import Blueprint, jsonify, request
except ImportError:
    print("❌ Flask not installed. Run: pip install flask")
    sys.exit(1)

from tools.tiktok_variant_expander import (
    get_safe_mode_status,
    toggle_safe_mode
)
from tools.tiktok_firewall import get_firewall_config
from tools.tiktok_price_ab import get_all_buckets
from tools.tiktok_feed_generator import generate_feed
from core.logger import get_logger

log = get_logger("TIKTOK-API")

# Create Blueprint
tiktok_bp = Blueprint("tiktok", __name__)


@tiktok_bp.route("/tiktok/status", methods=["GET"])
def get_status():
    """
    Get TikTok integration system status.

    Returns:
        JSON: System status and configuration

    Example:
        GET /api/tiktok/status
        {
            "status": "operational",
            "safe_mode": true,
            "region": "US"
        }
    """
    try:
        safe_mode = get_safe_mode_status()
        firewall = get_firewall_config()

        return jsonify({
            "status": "operational",
            "safe_mode": safe_mode["safe_mode_enabled"],
            "region": os.getenv("TIKTOK_REGION", "US"),
            "seller_id": os.getenv("TIKTOK_SELLER_ID", "NOT_CONFIGURED"),
            "firewall_enabled": firewall["enabled"],
            "min_inventory": firewall["min_inventory"],
            "api_configured": bool(os.getenv("TIKTOK_ACCESS_TOKEN")),
            "timestamp": firewall.get("_firewall_timestamp", "N/A")
        }), 200

    except Exception as e:
        log.error(f"❌ Status check failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@tiktok_bp.route("/tiktok/mode", methods=["GET"])
def get_mode():
    """
    Get current TikTok Safe Mode status.

    Returns:
        JSON: Safe mode configuration

    Example:
        GET /api/tiktok/mode
        {
            "safe_mode_enabled": true,
            "variant_count": 1,
            "recommendation": "..."
        }
    """
    try:
        status = get_safe_mode_status()
        log.info(f"📊 Safe mode status requested: {status['safe_mode_enabled']}")
        return jsonify(status), 200

    except Exception as e:
        log.error(f"❌ Mode check failed: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500


@tiktok_bp.route("/tiktok/mode", methods=["POST"])
def set_mode():
    """
    Toggle TikTok Safe Mode.

    Request Body:
        {"enabled": true/false}

    Returns:
        JSON: Updated safe mode status

    Example:
        POST /api/tiktok/mode
        {"enabled": false}

        Response:
        {
            "safe_mode_enabled": false,
            "message": "Safe mode disabled"
        }
    """
    try:
        data = request.get_json()

        if "enabled" not in data:
            return jsonify({
                "error": "Missing 'enabled' field in request body"
            }), 400

        enabled = bool(data["enabled"])
        new_state = toggle_safe_mode(enabled)

        log.info(f"🔧 Safe mode toggled: {new_state}")

        return jsonify({
            "safe_mode_enabled": new_state,
            "message": f"Safe mode {'enabled' if new_state else 'disabled'}",
            "warning": (
                "Multi-variant mode active. Monitor account health."
                if not new_state else None
            )
        }), 200

    except Exception as e:
        log.error(f"❌ Mode toggle failed: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500


@tiktok_bp.route("/tiktok/config", methods=["GET"])
def get_config():
    """
    Get full TikTok integration configuration.

    Returns:
        JSON: Complete configuration (firewall, price buckets, etc.)

    Example:
        GET /api/tiktok/config
        {
            "firewall": {...},
            "price_buckets": {...},
            "safe_mode": {...}
        }
    """
    try:
        return jsonify({
            "firewall": get_firewall_config(),
            "price_buckets": get_all_buckets(),
            "safe_mode": get_safe_mode_status()
        }), 200

    except Exception as e:
        log.error(f"❌ Config retrieval failed: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500


@tiktok_bp.route("/tiktok/generate", methods=["POST"])
def generate_product_feed():
    """
    Generate TikTok product feed (XLSX + CSV).

    Request Body (optional):
        {
            "source_dir": "queues/published",
            "output_dir": "exports",
            "price_tier": "standard"
        }

    Returns:
        JSON: Generation result with file paths

    Example:
        POST /api/tiktok/generate
        {}

        Response:
        {
            "products_generated": 42,
            "xlsx_path": "exports/tiktok_feed.xlsx",
            "csv_path": "exports/tiktok_feed.csv"
        }
    """
    try:
        data = request.get_json() or {}

        source_dir = Path(data.get("source_dir", "queues/published"))
        output_dir = Path(data.get("output_dir", "exports"))
        price_tier = data.get("price_tier", "standard")

        log.info(f"🚀 Feed generation requested: {source_dir} -> {output_dir}")

        result = generate_feed(source_dir, output_dir, price_tier)

        if result["products_generated"] == 0:
            return jsonify({
                "error": "No products generated",
                "message": f"No design files found in {source_dir}",
                "hint": "Add PNG/JPG files to the source directory"
            }), 404

        return jsonify(result), 200

    except Exception as e:
        log.error(f"❌ Feed generation failed: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500


@tiktok_bp.route("/tiktok/upload", methods=["POST"])
def upload_products():
    """
    Upload products to TikTok Shop via Seller API.

    Request Body:
        {
            "products": [...],
            "auto_generate": false
        }

    If auto_generate=true, generates feed first, then uploads.

    Returns:
        JSON: Upload result summary

    Example:
        POST /api/tiktok/upload
        {"auto_generate": true}

        Response:
        {
            "total": 42,
            "successful": 40,
            "failed": 2,
            "errors": [...]
        }
    """
    try:
        # Lazy import to avoid loading if credentials missing
        from tools.tiktok_uploader import TikTokUploader

        data = request.get_json() or {}

        # Check if we should auto-generate feed first
        if data.get("auto_generate", False):
            log.info("🔄 Auto-generating feed before upload")

            feed_result = generate_feed(
                Path("queues/published"),
                Path("exports")
            )

            if feed_result["products_generated"] == 0:
                return jsonify({
                    "error": "No products to upload",
                    "message": "Feed generation produced no products"
                }), 404

            # Load generated products (simplified for demo)
            # In production, read from XLSX/CSV or database
            products = data.get("products", [])
        else:
            products = data.get("products", [])

        if not products:
            return jsonify({
                "error": "No products provided",
                "message": "Provide 'products' array or set 'auto_generate': true"
            }), 400

        # Initialize uploader
        uploader = TikTokUploader()

        # Track progress
        progress = {"current": 0, "total": len(products)}

        def on_progress(current, total):
            progress["current"] = current
            log.info(f"📊 Progress: {current}/{total}")

        # Bulk upload
        result = uploader.bulk_upload(products, on_progress)

        return jsonify(result), 200

    except ValueError as e:
        # Credential errors
        log.error(f"❌ Configuration error: {str(e)}")
        return jsonify({
            "error": "TikTok API not configured",
            "message": str(e),
            "hint": "Set TIKTOK_SELLER_ID and TIKTOK_ACCESS_TOKEN"
        }), 503

    except Exception as e:
        log.error(f"❌ Upload failed: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500


@tiktok_bp.route("/tiktok/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        JSON: Service health status
    """
    return jsonify({
        "status": "healthy",
        "service": "tiktok-integration",
        "version": "2.0.0"
    }), 200


# Error handlers
@tiktok_bp.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "message": str(e)
    }), 404


@tiktok_bp.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    log.error(f"❌ Internal error: {str(e)}")
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500


# Module info
if __name__ == "__main__":
    print("TikTok Shop API Routes")
    print("=" * 60)
    print("\nAvailable endpoints:")
    print("  GET  /tiktok/status")
    print("  GET  /tiktok/mode")
    print("  POST /tiktok/mode")
    print("  GET  /tiktok/config")
    print("  POST /tiktok/generate")
    print("  POST /tiktok/upload")
    print("  GET  /tiktok/health")
    print("\nImport this module in your Flask app:")
    print("  from api.routes_tiktok import tiktok_bp")
    print("  app.register_blueprint(tiktok_bp, url_prefix='/api')")

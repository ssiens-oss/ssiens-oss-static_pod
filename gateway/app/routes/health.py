"""
Health Check Routes

Health and readiness endpoints for container orchestration.
"""
import os
from flask import Blueprint, jsonify, current_app

health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
def health():
    """
    Health check endpoint for RunPod and container orchestration.

    Returns 200 if healthy, 503 if critical components are missing.
    """
    config = current_app.config
    image_dir = config.get("IMAGE_DIR", "")
    state_file = config.get("STATE_FILE", "")

    services = {
        "generation": current_app.config.get("generation_service"),
        "publishing": current_app.config.get("publishing_service"),
    }

    health_status = {
        "status": "healthy",
        "generation": services["generation"] is not None and services["generation"].is_available,
        "publishing": services["publishing"] is not None and services["publishing"].is_available,
        "image_dir": os.path.exists(image_dir) if image_dir else False,
        "state_file": os.path.exists(state_file) if state_file else False
    }

    # Return 503 if critical components are missing
    if not health_status["image_dir"]:
        health_status["status"] = "unhealthy"
        return jsonify(health_status), 503

    return jsonify(health_status)


@health_bp.route("/ready")
def ready():
    """
    Readiness check endpoint.

    Returns 200 if ready to accept traffic.
    """
    services = {
        "generation": current_app.config.get("generation_service"),
        "image": current_app.config.get("image_service"),
    }

    ready_status = {
        "ready": True,
        "services": {
            "generation": services["generation"] is not None,
            "image": services["image"] is not None,
        }
    }

    # If image service is not available, we're not ready
    if services["image"] is None:
        ready_status["ready"] = False
        return jsonify(ready_status), 503

    return jsonify(ready_status)

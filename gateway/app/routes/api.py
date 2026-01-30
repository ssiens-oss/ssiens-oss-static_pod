"""
API Routes

REST API endpoints for image generation, management, and publishing.
"""
import logging
import os
from pathlib import Path
from flask import Blueprint, jsonify, request, send_from_directory, current_app, g

from app.models.schemas import GenerateRequest, PublishRequest
from app.state import ImageStatus
from app.utils.validation import validate_image_id, validate_title, validate_image_file

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")


def get_services():
    """Get services from app context"""
    return {
        "generation": current_app.config.get("generation_service"),
        "image": current_app.config.get("image_service"),
        "publishing": current_app.config.get("publishing_service"),
    }


@api_bp.route("/images")
def list_images():
    """List all images with their status"""
    services = get_services()
    image_service = services["image"]

    if not image_service:
        return jsonify({"error": "Image service not available"}), 500

    try:
        images = image_service.list_images()
        return jsonify({"images": images, "count": len(images)})
    except Exception as e:
        logger.error(f"Error listing images: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/image/<image_id>")
def serve_image(image_id):
    """Serve an individual image file"""
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"error": error}), 400

    services = get_services()
    image_service = services["image"]

    if not image_service:
        return jsonify({"error": "Image service not available"}), 500

    image_path = image_service.get_image_path(image_id)
    if not image_path:
        return jsonify({"error": "Image not found"}), 404

    is_valid, error = validate_image_file(str(image_path))
    if not is_valid:
        return jsonify({"error": error}), 404

    return send_from_directory(image_path.parent, image_path.name)


@api_bp.route("/generate", methods=["POST"])
def generate_image():
    """Submit a prompt for image generation"""
    services = get_services()
    generation_service = services["generation"]

    if not generation_service or not generation_service.is_available:
        return jsonify({"error": "Generation service not available"}), 503

    data = request.get_json(silent=True) or {}
    req = GenerateRequest.from_dict(data)

    # Validate request
    error = req.validate()
    if error:
        return jsonify({"error": error}), 400

    try:
        result = generation_service.generate(req)

        if result.error:
            return jsonify(result.to_dict()), 502

        return jsonify(result.to_dict())

    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/generation_status")
def generation_status():
    """Check status of a generation job (ComfyUI)"""
    prompt_id = request.args.get("prompt_id")
    if not prompt_id:
        return jsonify({"error": "prompt_id is required"}), 400

    services = get_services()
    generation_service = services["generation"]

    if not generation_service:
        return jsonify({"error": "Generation service not available"}), 503

    try:
        result = generation_service.check_status(prompt_id)
        return jsonify(result.to_dict())
    except Exception as e:
        logger.error(f"Status check error: {e}", exc_info=True)
        return jsonify({"error": "Failed to check status"}), 502


@api_bp.route("/runpod_status")
def runpod_status():
    """Check status of a RunPod serverless job"""
    job_id = request.args.get("job_id")
    if not job_id:
        return jsonify({"error": "job_id is required"}), 400

    services = get_services()
    generation_service = services["generation"]

    if not generation_service or not generation_service.is_available:
        return jsonify({"error": "RunPod client not configured"}), 400

    try:
        result = generation_service.check_status(job_id)

        if result.error:
            return jsonify({
                "status": result.status,
                "error": result.error
            }), 500

        return jsonify({
            "status": result.status,
            "job_id": job_id,
            "images": result.images
        })
    except Exception as e:
        logger.error(f"RunPod status error: {e}", exc_info=True)
        return jsonify({"error": "Failed to check RunPod job"}), 502


@api_bp.route("/approve/<image_id>", methods=["POST"])
def approve_image(image_id):
    """Approve an image for publishing"""
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    services = get_services()
    image_service = services["image"]

    if not image_service:
        return jsonify({"success": False, "error": "Image service not available"}), 500

    if image_service.set_status(image_id, ImageStatus.APPROVED):
        logger.info(f"Image approved: {image_id}")
        return jsonify({"success": True, "status": ImageStatus.APPROVED.value})
    else:
        return jsonify({"success": False, "error": "Failed to update status"}), 500


@api_bp.route("/reject/<image_id>", methods=["POST"])
def reject_image(image_id):
    """Reject an image"""
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    services = get_services()
    image_service = services["image"]

    if not image_service:
        return jsonify({"success": False, "error": "Image service not available"}), 500

    if image_service.set_status(image_id, ImageStatus.REJECTED):
        logger.info(f"Image rejected: {image_id}")
        return jsonify({"success": True, "status": ImageStatus.REJECTED.value})
    else:
        return jsonify({"success": False, "error": "Failed to update status"}), 500


@api_bp.route("/reset/<image_id>", methods=["POST"])
def reset_image(image_id):
    """Reset image to pending status"""
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    services = get_services()
    image_service = services["image"]

    if not image_service:
        return jsonify({"success": False, "error": "Image service not available"}), 500

    if image_service.set_status(image_id, ImageStatus.PENDING):
        logger.info(f"Image reset: {image_id}")
        return jsonify({"success": True, "status": ImageStatus.PENDING.value})
    else:
        return jsonify({"success": False, "error": "Failed to update status"}), 500


@api_bp.route("/publish/<image_id>", methods=["POST"])
def publish_image(image_id):
    """Publish approved image to Printify"""
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    services = get_services()
    publishing_service = services["publishing"]

    if not publishing_service or not publishing_service.is_available:
        return jsonify({"success": False, "error": "Publishing not configured"}), 400

    # Parse request
    try:
        data = request.get_json() or {}
    except Exception:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400

    default_title = f"Design {image_id[:8]}"
    pub_req = PublishRequest.from_dict(data, default_title)

    # Validate title
    is_valid, error = validate_title(pub_req.title)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    # Publish
    result = publishing_service.publish(
        image_id=image_id,
        title=pub_req.title,
        description=pub_req.description,
        price_cents=pub_req.price_cents,
        blueprint_id=pub_req.blueprint_id,
        provider_id=pub_req.provider_id
    )

    status_code = 200 if result.get("success") else 500
    return jsonify(result), status_code


@api_bp.route("/stats")
def get_stats():
    """Get gallery statistics"""
    services = get_services()
    image_service = services["image"]

    if not image_service:
        return jsonify({"error": "Image service not available"}), 500

    try:
        stats = image_service.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/debug/config")
def debug_config():
    """Debug endpoint for configuration diagnostics"""
    config = current_app.config

    def mask_key(key: str, prefix_len: int = 10, suffix_len: int = 4) -> dict:
        if not key:
            return {"length": 0, "prefix": "", "suffix": "", "is_placeholder": True}
        is_placeholder = key.startswith("your-") or key in ["", "placeholder", "test"]
        return {
            "length": len(key),
            "prefix": key[:prefix_len] if len(key) > prefix_len else key[:3] + "...",
            "suffix": key[-suffix_len:] if len(key) > suffix_len else "",
            "is_placeholder": is_placeholder
        }

    services = get_services()
    image_dir = config.get("IMAGE_DIR", "")

    return jsonify({
        "printify": {
            "api_key": mask_key(config.get("PRINTIFY_API_KEY") or ""),
            "shop_id": config.get("PRINTIFY_SHOP_ID"),
            "blueprint_id": config.get("PRINTIFY_BLUEPRINT_ID"),
            "provider_id": config.get("PRINTIFY_PROVIDER_ID"),
            "client_initialized": services["publishing"] and services["publishing"].is_available
        },
        "runpod": {
            "api_key": mask_key(config.get("RUNPOD_API_KEY") or ""),
            "endpoint_id": config.get("RUNPOD_ENDPOINT_ID"),
            "client_initialized": services["generation"] and services["generation"].is_available
        },
        "paths": {
            "image_dir": image_dir,
            "image_dir_exists": os.path.exists(image_dir) if image_dir else False,
            "state_file": config.get("STATE_FILE", ""),
            "state_file_exists": os.path.exists(config.get("STATE_FILE", ""))
        }
    })

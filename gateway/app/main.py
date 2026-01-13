"""
POD Gateway - Main Flask Application
Human-in-the-loop approval system for POD designs
"""
from flask import Flask, render_template, jsonify, request, send_from_directory
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from PIL import Image
from typing import Dict, Any, Tuple
import re

# Load environment
load_dotenv()

# Import modules
from app import config
from app.state import StateManager, ImageStatus, StateManagerError
from app.printify_client import PrintifyClient, RetryConfig, PrintifyError

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.config.logging.level),
    format=config.config.logging.format
)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__, template_folder='../templates')

# Initialize services
state_manager = StateManager(config.STATE_FILE)

# Initialize Printify client (optional)
printify_client = None
if config.config.printify.is_configured():
    try:
        retry_config = RetryConfig(
            max_retries=config.config.retry.max_retries,
            initial_backoff=config.config.retry.initial_backoff_seconds,
            max_backoff=config.config.retry.max_backoff_seconds,
            backoff_multiplier=config.config.retry.backoff_multiplier
        )
        printify_client = PrintifyClient(
            config.PRINTIFY_API_KEY,
            config.PRINTIFY_SHOP_ID,
            retry_config
        )
        logger.info("✓ Printify client initialized")
    except Exception as e:
        logger.error(f"✗ Printify client failed: {e}")
else:
    logger.warning("✗ Printify not configured (missing API key or Shop ID)")


# Input validation helpers
def validate_image_id(image_id: str) -> Tuple[bool, str]:
    """
    Validate image ID format

    Args:
        image_id: Image identifier to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not image_id:
        return False, "Image ID is required"

    # Allow alphanumeric, hyphens, underscores (prevent path traversal)
    if not re.match(r'^[a-zA-Z0-9_-]+$', image_id):
        return False, "Invalid image ID format"

    if len(image_id) > 255:
        return False, "Image ID too long"

    return True, ""


def validate_title(title: str) -> Tuple[bool, str]:
    """
    Validate product title

    Args:
        title: Product title to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not title:
        return False, "Title is required"

    if len(title) < 3:
        return False, "Title must be at least 3 characters"

    if len(title) > 200:
        return False, "Title must be less than 200 characters"

    # Check for suspicious patterns (basic XSS prevention)
    if re.search(r'[<>\"\'`]', title):
        return False, "Title contains invalid characters"

    return True, ""


def validate_image_file(image_path: str) -> Tuple[bool, str]:
    """
    Validate image file exists and is a valid image

    Args:
        image_path: Path to image file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(image_path):
        return False, "Image file not found"

    # Check file size (max 20MB)
    file_size = os.path.getsize(image_path)
    max_size = 20 * 1024 * 1024  # 20MB
    if file_size > max_size:
        return False, f"Image file too large (max {max_size / 1024 / 1024}MB)"

    # Verify it's a valid image using Pillow
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True, ""
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


@app.route('/')
def index():
    """Gallery UI"""
    return render_template('gallery.html')


@app.route('/api/images')
def list_images():
    """
    List all images with their status

    Returns:
        JSON with list of images
    """
    try:
        image_dir = Path(config.IMAGE_DIR)

        if not image_dir.exists():
            logger.warning(f"Image directory does not exist: {image_dir}")
            return jsonify({"images": []})

        images = []
        state = state_manager.get_all_images()

        # Scan directory for images
        for img_file in image_dir.glob("*.png"):
            img_id = img_file.stem

            # Validate image ID format
            is_valid, error = validate_image_id(img_id)
            if not is_valid:
                logger.warning(f"Skipping invalid image ID: {img_id}")
                continue

            # Get status from state
            img_state = state.get(img_id, {})
            status = img_state.get("status", ImageStatus.PENDING.value)

            # Register if new
            if img_id not in state:
                try:
                    state_manager.add_image(img_id, img_file.name, str(img_file))
                except StateManagerError as e:
                    logger.error(f"Failed to add image {img_id}: {e}")
                    continue

            images.append({
                "id": img_id,
                "filename": img_file.name,
                "status": status,
                "path": f"/api/image/{img_id}",
                "created_at": img_state.get("created_at"),
                "updated_at": img_state.get("updated_at")
            })

        # Sort by filename (newest first)
        images.sort(key=lambda x: x['filename'], reverse=True)

        return jsonify({"images": images, "count": len(images)})

    except Exception as e:
        logger.error(f"Error listing images: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/image/<image_id>')
def serve_image(image_id):
    """
    Serve individual image

    Args:
        image_id: Image identifier

    Returns:
        Image file or error
    """
    # Validate image ID
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"error": error}), 400

    image_path = os.path.join(config.IMAGE_DIR, f"{image_id}.png")

    # Validate file exists and is valid
    is_valid, error = validate_image_file(image_path)
    if not is_valid:
        return jsonify({"error": error}), 404

    return send_from_directory(config.IMAGE_DIR, f"{image_id}.png")


@app.route('/api/approve/<image_id>', methods=['POST'])
def approve_image(image_id):
    """
    Approve an image for publishing

    Args:
        image_id: Image identifier

    Returns:
        JSON response with success status
    """
    # Validate image ID
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    try:
        state_manager.set_image_status(image_id, ImageStatus.APPROVED.value)
        logger.info(f"Image approved: {image_id}")
        return jsonify({"success": True, "status": ImageStatus.APPROVED.value})
    except StateManagerError as e:
        logger.error(f"Failed to approve image {image_id}: {e}")
        return jsonify({"success": False, "error": "Failed to update status"}), 500


@app.route('/api/reject/<image_id>', methods=['POST'])
def reject_image(image_id):
    """
    Reject an image

    Args:
        image_id: Image identifier

    Returns:
        JSON response with success status
    """
    # Validate image ID
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    try:
        state_manager.set_image_status(image_id, ImageStatus.REJECTED.value)
        logger.info(f"Image rejected: {image_id}")
        return jsonify({"success": True, "status": ImageStatus.REJECTED.value})
    except StateManagerError as e:
        logger.error(f"Failed to reject image {image_id}: {e}")
        return jsonify({"success": False, "error": "Failed to update status"}), 500


@app.route('/api/publish/<image_id>', methods=['POST'])
def publish_image(image_id):
    """
    Publish approved image to Printify

    Args:
        image_id: Image identifier

    Returns:
        JSON response with product ID or error
    """
    # Validate Printify is configured
    if not printify_client:
        return jsonify({
            "success": False,
            "error": "Printify not configured"
        }), 400

    # Validate image ID
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    # Check if approved
    status = state_manager.get_image_status(image_id)
    if status not in [ImageStatus.APPROVED.value, ImageStatus.FAILED.value]:
        return jsonify({
            "success": False,
            "error": f"Image must be approved first (current status: {status})"
        }), 400

    # Get image path
    image_path = os.path.join(config.IMAGE_DIR, f"{image_id}.png")

    # Validate image file
    is_valid, error = validate_image_file(image_path)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 404

    # Get and validate title from request
    try:
        request_data = request.get_json() or {}
    except Exception as e:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400

    title = request_data.get("title", f"Design {image_id[:8]}")
    is_valid, error = validate_title(title)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    # Update status to publishing
    try:
        state_manager.set_image_status(image_id, ImageStatus.PUBLISHING.value)
    except StateManagerError as e:
        logger.error(f"Failed to update status to publishing: {e}")
        return jsonify({"success": False, "error": "Failed to update status"}), 500

    # Publish to Printify
    try:
        description = request_data.get("description")
        price_cents = request_data.get("price_cents", config.config.printify.default_price_cents)

        # Validate price
        if not isinstance(price_cents, int) or price_cents < 0:
            return jsonify({"success": False, "error": "Invalid price"}), 400

        product_id = printify_client.create_and_publish(
            image_path=image_path,
            title=title,
            blueprint_id=config.PRINTIFY_BLUEPRINT_ID,
            provider_id=config.PRINTIFY_PROVIDER_ID,
            price_cents=price_cents,
            description=description
        )

        if product_id:
            state_manager.set_image_status(image_id, ImageStatus.PUBLISHED.value, {
                "product_id": product_id,
                "title": title
            })
            logger.info(f"Image published successfully: {image_id} -> Product {product_id}")
            return jsonify({
                "success": True,
                "product_id": product_id,
                "status": ImageStatus.PUBLISHED.value
            })
        else:
            error_msg = "Printify API failed to create product"
            state_manager.set_image_status(image_id, ImageStatus.FAILED.value, {
                "error_message": error_msg
            })
            logger.error(f"Failed to publish image {image_id}: {error_msg}")
            return jsonify({"success": False, "error": error_msg}), 500

    except PrintifyError as e:
        error_msg = f"Printify error: {str(e)}"
        logger.error(f"Printify error for image {image_id}: {e}", exc_info=True)
        try:
            state_manager.set_image_status(image_id, ImageStatus.FAILED.value, {
                "error_message": error_msg
            })
        except StateManagerError:
            pass
        return jsonify({"success": False, "error": error_msg}), 500

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error publishing image {image_id}: {e}", exc_info=True)
        try:
            state_manager.set_image_status(image_id, ImageStatus.FAILED.value, {
                "error_message": error_msg
            })
        except StateManagerError:
            pass
        return jsonify({"success": False, "error": "Internal server error"}), 500


@app.route('/api/reset/<image_id>', methods=['POST'])
def reset_image(image_id):
    """
    Reset image to pending status

    Args:
        image_id: Image identifier

    Returns:
        JSON response with success status
    """
    # Validate image ID
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    try:
        state_manager.set_image_status(image_id, ImageStatus.PENDING.value)
        logger.info(f"Image reset to pending: {image_id}")
        return jsonify({"success": True, "status": ImageStatus.PENDING.value})
    except StateManagerError as e:
        logger.error(f"Failed to reset image {image_id}: {e}")
        return jsonify({"success": False, "error": "Failed to update status"}), 500


@app.route('/api/stats')
def get_stats():
    """
    Get gallery statistics

    Returns:
        JSON with statistics
    """
    try:
        stats = state_manager.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting statistics: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/health')
def health():
    """
    Health check for RunPod

    Returns:
        JSON with health status
    """
    health_status = {
        "status": "healthy",
        "printify": printify_client is not None,
        "image_dir": os.path.exists(config.IMAGE_DIR),
        "state_file": os.path.exists(config.STATE_FILE)
    }

    # Return 503 if critical components are missing
    if not health_status["image_dir"]:
        health_status["status"] = "unhealthy"
        return jsonify(health_status), 503

    return jsonify(health_status)


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {e}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Print configuration summary
    config.config.print_summary()

    logger.info("🚀 POD Gateway starting...")
    logger.info(f"📁 Image directory: {config.IMAGE_DIR}")
    logger.info(f"💾 State file: {config.STATE_FILE}")
    logger.info(f"🔌 Printify: {'enabled' if printify_client else 'disabled'}")
    logger.info(f"🌐 Listening on {config.FLASK_HOST}:{config.FLASK_PORT}")

    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )

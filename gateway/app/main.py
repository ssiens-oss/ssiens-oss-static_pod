"""
POD Gateway - Main Flask Application
Human-in-the-loop approval system for POD designs
"""
from flask import Flask, render_template, jsonify, request, send_from_directory
from dotenv import load_dotenv
import os
from pathlib import Path
import uuid
from PIL import Image

# Load environment
load_dotenv()

# Import modules
from app import config
from app.state import StateManager
from app.printify_client import PrintifyClient

# Initialize Flask
app = Flask(__name__, template_folder='../templates')

# Initialize services
state_manager = StateManager(config.STATE_FILE)

# Initialize Printify client (optional)
printify_client = None
if config.PRINTIFY_API_KEY and config.PRINTIFY_SHOP_ID:
    try:
        printify_client = PrintifyClient(config.PRINTIFY_API_KEY, config.PRINTIFY_SHOP_ID)
        print("✓ Printify client initialized")
    except Exception as e:
        print(f"✗ Printify client failed: {e}")

@app.route('/')
def index():
    """Gallery UI"""
    return render_template('gallery.html')

@app.route('/api/images')
def list_images():
    """List all images with their status"""
    image_dir = Path(config.IMAGE_DIR)

    if not image_dir.exists():
        return jsonify({"images": []})

    images = []
    state = state_manager.get_all_images()

    # Scan directory for images
    for img_file in image_dir.glob("*.png"):
        img_id = img_file.stem

        # Get status from state
        img_state = state.get(img_id, {})
        status = img_state.get("status", "pending")

        # Register if new
        if img_id not in state:
            state_manager.add_image(img_id, img_file.name, str(img_file))

        images.append({
            "id": img_id,
            "filename": img_file.name,
            "status": status,
            "path": f"/api/image/{img_id}"
        })

    # Sort by filename (newest first)
    images.sort(key=lambda x: x['filename'], reverse=True)

    return jsonify({"images": images})

@app.route('/api/image/<image_id>')
def serve_image(image_id):
    """Serve individual image"""
    return send_from_directory(config.IMAGE_DIR, f"{image_id}.png")

@app.route('/api/approve/<image_id>', methods=['POST'])
def approve_image(image_id):
    """Approve an image for publishing"""
    state_manager.set_image_status(image_id, "approved")
    return jsonify({"success": True, "status": "approved"})

@app.route('/api/reject/<image_id>', methods=['POST'])
def reject_image(image_id):
    """Reject an image"""
    state_manager.set_image_status(image_id, "rejected")
    return jsonify({"success": True, "status": "rejected"})

@app.route('/api/publish/<image_id>', methods=['POST'])
def publish_image(image_id):
    """Publish approved image to Printify"""
    if not printify_client:
        return jsonify({"success": False, "error": "Printify not configured"}), 400

    # Check if approved
    status = state_manager.get_image_status(image_id)
    if status not in ["approved", "failed"]:
        return jsonify({"success": False, "error": f"Image must be approved first (current: {status})"}), 400

    # Get image path
    image_path = os.path.join(config.IMAGE_DIR, f"{image_id}.png")
    if not os.path.exists(image_path):
        return jsonify({"success": False, "error": "Image file not found"}), 404

    # Update status
    state_manager.set_image_status(image_id, "publishing")

    # Publish to Printify
    try:
        title = request.json.get("title", f"Design {image_id[:8]}")
        product_id = printify_client.create_and_publish(
            image_path,
            title,
            config.PRINTIFY_BLUEPRINT_ID,
            config.PRINTIFY_PROVIDER_ID
        )

        if product_id:
            state_manager.set_image_status(image_id, "published", {
                "product_id": product_id,
                "title": title
            })
            return jsonify({"success": True, "product_id": product_id})
        else:
            state_manager.set_image_status(image_id, "failed")
            return jsonify({"success": False, "error": "Printify API failed"}), 500

    except Exception as e:
        state_manager.set_image_status(image_id, "failed")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/reset/<image_id>', methods=['POST'])
def reset_image(image_id):
    """Reset image to pending status"""
    state_manager.set_image_status(image_id, "pending")
    return jsonify({"success": True, "status": "pending"})

@app.route('/api/batch/approve', methods=['POST'])
def batch_approve():
    """Batch approve multiple images"""
    data = request.get_json()
    image_ids = data.get('image_ids', [])

    if not image_ids:
        return jsonify({"success": False, "error": "No images selected"}), 400

    results = []
    for image_id in image_ids:
        try:
            state_manager.set_image_status(image_id, "approved")
            results.append({"id": image_id, "success": True, "status": "approved"})
        except Exception as e:
            results.append({"id": image_id, "success": False, "error": str(e)})

    successful = len([r for r in results if r["success"]])
    return jsonify({
        "success": True,
        "processed": len(results),
        "successful": successful,
        "failed": len(results) - successful,
        "results": results
    })

@app.route('/api/batch/reject', methods=['POST'])
def batch_reject():
    """Batch reject multiple images"""
    data = request.get_json()
    image_ids = data.get('image_ids', [])

    if not image_ids:
        return jsonify({"success": False, "error": "No images selected"}), 400

    results = []
    for image_id in image_ids:
        try:
            state_manager.set_image_status(image_id, "rejected")
            results.append({"id": image_id, "success": True, "status": "rejected"})
        except Exception as e:
            results.append({"id": image_id, "success": False, "error": str(e)})

    successful = len([r for r in results if r["success"]])
    return jsonify({
        "success": True,
        "processed": len(results),
        "successful": successful,
        "failed": len(results) - successful,
        "results": results
    })

@app.route('/api/batch/publish', methods=['POST'])
def batch_publish():
    """Batch publish multiple approved images"""
    if not printify_client:
        return jsonify({"success": False, "error": "Printify not configured"}), 400

    data = request.get_json()
    image_ids = data.get('image_ids', [])

    if not image_ids:
        return jsonify({"success": False, "error": "No images selected"}), 400

    results = []
    for image_id in image_ids:
        try:
            # Check if approved
            status = state_manager.get_image_status(image_id)
            if status not in ["approved", "failed"]:
                results.append({"id": image_id, "success": False, "error": f"Not approved (status: {status})"})
                continue

            # Get image path
            image_path = os.path.join(config.IMAGE_DIR, f"{image_id}.png")
            if not os.path.exists(image_path):
                results.append({"id": image_id, "success": False, "error": "File not found"})
                continue

            # Publish
            state_manager.set_image_status(image_id, "publishing")
            title = f"Design {image_id[:8]}"
            product_id = printify_client.create_and_publish(
                image_path,
                title,
                config.PRINTIFY_BLUEPRINT_ID,
                config.PRINTIFY_PROVIDER_ID
            )

            if product_id:
                state_manager.set_image_status(image_id, "published", {"product_id": product_id, "title": title})
                results.append({"id": image_id, "success": True, "status": "published", "product_id": product_id})
            else:
                state_manager.set_image_status(image_id, "failed")
                results.append({"id": image_id, "success": False, "error": "Printify API failed"})

        except Exception as e:
            state_manager.set_image_status(image_id, "failed")
            results.append({"id": image_id, "success": False, "error": str(e)})

    successful = len([r for r in results if r["success"]])
    return jsonify({
        "success": True,
        "processed": len(results),
        "successful": successful,
        "failed": len(results) - successful,
        "results": results
    })

@app.route('/api/stats')
def get_stats():
    """Get gallery statistics"""
    state = state_manager.get_all_images()

    stats = {
        "total": len(state),
        "pending": len([s for s in state.values() if s.get("status") == "pending"]),
        "approved": len([s for s in state.values() if s.get("status") == "approved"]),
        "rejected": len([s for s in state.values() if s.get("status") == "rejected"]),
        "published": len([s for s in state.values() if s.get("status") == "published"]),
        "failed": len([s for s in state.values() if s.get("status") == "failed"])
    }

    return jsonify(stats)

@app.route('/health')
def health():
    """Health check for RunPod"""
    return jsonify({
        "status": "healthy",
        "printify": printify_client is not None,
        "image_dir": os.path.exists(config.IMAGE_DIR)
    })

if __name__ == "__main__":
    print(f"🚀 POD Gateway starting...")
    print(f"📁 Image directory: {config.IMAGE_DIR}")
    print(f"💾 State file: {config.STATE_FILE}")
    print(f"🔌 Printify: {'enabled' if printify_client else 'disabled'}")
    print(f"🌐 Listening on {config.FLASK_HOST}:{config.FLASK_PORT}")

    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )

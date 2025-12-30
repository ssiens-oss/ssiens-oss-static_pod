#!/usr/bin/env python3
"""
StaticWaves POD API - Control Plane
Flask-based API for managing the POD automation pipeline
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from api.publish import publish_product
from api.pricing import price_product
from api.validators import validate_product
from api.alerts import send_alert
from api.license import check_license
from api.agents_api import agents_bp

app = Flask(__name__)
CORS(app)

# Register agent management blueprint
app.register_blueprint(agents_bp)

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
QUEUE_DIR = DATA_DIR / "queue"

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@app.route("/license")
def license_status():
    """Check license status"""
    try:
        license_info = check_license()
        return jsonify({
            "valid": True,
            "license": license_info
        })
    except Exception as e:
        return jsonify({
            "valid": False,
            "error": str(e)
        }), 403

@app.route("/publish", methods=["POST"])
def publish():
    """
    Publish a product through the POD pipeline

    Expected payload:
    {
        "title": "Cosmic Waves Hoodie",
        "description": "AI-generated cosmic design",
        "prompt": "cosmic waves nebula stars",
        "type": "hoodie",
        "base_cost": 35.00,
        "inventory": 100
    }
    """
    try:
        # Check license
        check_license()

        payload = request.json

        # Validate product data
        validate_product(payload)

        # Add pricing
        payload["price"] = price_product(payload)

        # Publish through pipeline
        result = publish_product(payload)

        # Send alert
        send_alert({
            "type": "success",
            "message": f"Published: {payload['title']}",
            "sku": result.get("sku")
        })

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:
        # Send error alert
        send_alert({
            "type": "error",
            "message": f"Publish failed: {str(e)}"
        })

        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route("/queue", methods=["GET"])
def queue_status():
    """Get queue status across all stages"""
    try:
        status = {
            "pending": len(list((QUEUE_DIR / "pending").glob("*.json"))),
            "processing": len(list((QUEUE_DIR / "processing").glob("*.json"))),
            "done": len(list((QUEUE_DIR / "done").glob("*.json"))),
            "failed": len(list((QUEUE_DIR / "failed").glob("*.json")))
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/queue/<stage>", methods=["GET"])
def queue_items(stage):
    """Get items in a specific queue stage"""
    if stage not in ["pending", "processing", "done", "failed"]:
        return jsonify({"error": "Invalid stage"}), 400

    try:
        items = []
        stage_dir = QUEUE_DIR / stage
        for item_file in stage_dir.glob("*.json"):
            with open(item_file) as f:
                items.append(json.load(f))

        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/queue/add", methods=["POST"])
def add_to_queue():
    """Add an item to the pending queue"""
    try:
        check_license()

        payload = request.json
        validate_product(payload)

        # Generate unique ID
        item_id = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{payload['title'][:20].replace(' ', '_')}"

        # Save to pending queue
        queue_file = QUEUE_DIR / "pending" / f"{item_id}.json"
        with open(queue_file, "w") as f:
            json.dump(payload, f, indent=2)

        return jsonify({
            "success": True,
            "id": item_id
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route("/stats", methods=["GET"])
def stats():
    """Get system statistics"""
    try:
        # Count designs
        designs_count = len(list((DATA_DIR / "designs").glob("*")))

        # Queue stats
        queue_stats = {
            "pending": len(list((QUEUE_DIR / "pending").glob("*.json"))),
            "processing": len(list((QUEUE_DIR / "processing").glob("*.json"))),
            "done": len(list((QUEUE_DIR / "done").glob("*.json"))),
            "failed": len(list((QUEUE_DIR / "failed").glob("*.json")))
        }

        return jsonify({
            "designs": designs_count,
            "queue": queue_stats,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Ensure directories exist
    for stage in ["pending", "processing", "done", "failed"]:
        (QUEUE_DIR / stage).mkdir(parents=True, exist_ok=True)

    (DATA_DIR / "designs").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "logs").mkdir(parents=True, exist_ok=True)

    # Run server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

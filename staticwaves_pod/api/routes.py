from flask import Blueprint, request, jsonify
from pathlib import Path
import uuid

api = Blueprint('api', __name__)

QUEUE_DIR = Path("queues/incoming")
QUEUE_DIR.mkdir(parents=True, exist_ok=True)

@api.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "StaticWaves POD"})

@api.route('/upload', methods=['POST'])
def upload_design():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith('.png'):
        return jsonify({"error": "Only PNG files allowed"}), 400

    # Save to incoming queue with unique ID
    file_id = uuid.uuid4().hex[:8]
    filename = f"{file_id}_{file.filename}"
    filepath = QUEUE_DIR / filename

    file.save(filepath)

    return jsonify({
        "status": "queued",
        "file_id": file_id,
        "filename": filename
    }), 200

@api.route('/queue/status', methods=['GET'])
def queue_status():
    incoming = len(list(Path("queues/incoming").glob("*.png")))
    processed = len(list(Path("queues/processed").glob("*.png")))
    published = len(list(Path("queues/published").glob("*.png")))
    failed = len(list(Path("queues/failed").glob("*.png")))

    return jsonify({
        "incoming": incoming,
        "processed": processed,
        "published": published,
        "failed": failed
    })

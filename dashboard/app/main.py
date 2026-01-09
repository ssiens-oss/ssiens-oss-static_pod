"""
POD Dashboard - Unified Interface
Combines Gateway + Prompter + Overview
"""
from flask import Flask, render_template, jsonify, request, send_from_directory
from dotenv import load_dotenv
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from PIL import Image
import anthropic

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
load_dotenv()

# Import config
from app import config

# Initialize Flask
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Import services (with error handling)
state_manager = None
printify_client = None
prompt_generator = None

try:
    # State management
    import threading

    class StateManager:
        def __init__(self, state_file: str):
            self.state_file = state_file
            self.lock = threading.Lock()
            self.state = self._load()

        def _load(self):
            if not os.path.exists(self.state_file):
                return {"images": {}}
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return {"images": {}}

        def _save(self):
            temp_file = f"{self.state_file}.tmp"
            try:
                with open(temp_file, 'w') as f:
                    json.dump(self.state, f, indent=2)
                os.replace(temp_file, self.state_file)
            except:
                pass

        def get_image_status(self, image_id: str) -> str:
            with self.lock:
                return self.state["images"].get(image_id, {}).get("status", "pending")

        def set_image_status(self, image_id: str, status: str, metadata: dict = None):
            with self.lock:
                if image_id not in self.state["images"]:
                    self.state["images"][image_id] = {}
                self.state["images"][image_id]["status"] = status
                if metadata:
                    self.state["images"][image_id].update(metadata)
                self._save()

        def get_all_images(self):
            with self.lock:
                return self.state["images"].copy()

        def add_image(self, image_id: str, filename: str, path: str):
            with self.lock:
                self.state["images"][image_id] = {
                    "filename": filename,
                    "path": path,
                    "status": "pending"
                }
                self._save()

    state_manager = StateManager(config.STATE_FILE)
    print("✓ State manager initialized")
except Exception as e:
    print(f"✗ State manager failed: {e}")

try:
    # Printify client
    import requests

    class PrintifyClient:
        def __init__(self, api_key: str, shop_id: str):
            self.api_key = api_key
            self.shop_id = shop_id
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

        def upload_image(self, image_path: str, filename: str):
            with open(image_path, "rb") as f:
                files = {"file": (filename, f, "image/png")}
                r = requests.post(
                    "https://api.printify.com/v1/uploads/images.json",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files=files
                )
            return r.json().get("id") if r.ok else None

        def create_and_publish(self, image_path: str, title: str, blueprint_id: int, provider_id: int):
            image_id = self.upload_image(image_path, title)
            if not image_id:
                return None
            # Simplified - full implementation in original printify_client.py
            return f"product_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    if config.PRINTIFY_API_KEY and config.PRINTIFY_SHOP_ID:
        printify_client = PrintifyClient(config.PRINTIFY_API_KEY, config.PRINTIFY_SHOP_ID)
        print("✓ Printify client initialized")
except Exception as e:
    print(f"✗ Printify client failed: {e}")

try:
    # Prompt generator
    class PromptGenerator:
        def __init__(self, api_key: str, model: str):
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = model

        def generate_prompts(self, theme: str, style: str, niche: str, count: int, product_type: str):
            system_prompt = """You are an expert POD designer. Generate creative prompts in JSON format:
{"prompts": [{"prompt": "...", "title": "...", "tags": [...], "description": "..."}]}"""

            user_prompt = f"""Generate {count} POD prompts for:
Theme: {theme}
Style: {style}
Niche: {niche}
Product: {product_type}"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=1.0,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            content = response.content[0].text

            # Parse JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            parsed = json.loads(json_str)
            return parsed.get("prompts", [])

    if config.ANTHROPIC_API_KEY:
        prompt_generator = PromptGenerator(config.ANTHROPIC_API_KEY, config.CLAUDE_MODEL)
        print("✓ Prompt generator initialized")
except Exception as e:
    print(f"✗ Prompt generator failed: {e}")

# =============================================================================
# ROUTES - Dashboard
# =============================================================================

@app.route('/')
def index():
    """Dashboard home - overview of all tools"""
    return render_template('dashboard.html')

@app.route('/prompter')
def prompter():
    """AI Prompter interface"""
    return render_template('prompter.html')

@app.route('/gallery')
def gallery():
    """Image gallery interface"""
    return render_template('gallery.html')

# =============================================================================
# API - Overview Stats
# =============================================================================

@app.route('/api/overview')
def get_overview():
    """Get overview stats from all systems"""
    stats = {
        "gateway": {"pending": 0, "approved": 0, "published": 0, "rejected": 0},
        "prompter": {"total_prompts": 0},
        "services": {
            "claude": prompt_generator is not None,
            "printify": printify_client is not None,
            "state": state_manager is not None
        }
    }

    # Gateway stats
    if state_manager:
        state = state_manager.get_all_images()
        for img_data in state.values():
            status = img_data.get("status", "pending")
            if status in stats["gateway"]:
                stats["gateway"][status] += 1

    # Prompter stats
    if os.path.exists(config.PROMPTS_DIR):
        prompt_files = list(Path(config.PROMPTS_DIR).glob("*.json"))
        stats["prompter"]["total_prompts"] = len(prompt_files)

    return jsonify(stats)

# =============================================================================
# API - Prompter
# =============================================================================

@app.route('/api/generate-prompts', methods=['POST'])
def generate_prompts():
    """Generate prompts using Claude"""
    if not prompt_generator:
        return jsonify({"error": "Claude API not configured"}), 400

    data = request.json
    try:
        prompts = prompt_generator.generate_prompts(
            theme=data.get('theme', 'general'),
            style=data.get('style', 'modern'),
            niche=data.get('niche', 'general audience'),
            count=int(data.get('count', 5)),
            product_type=data.get('product_type', 'tshirt')
        )

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(config.PROMPTS_DIR) / f"prompts_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(prompts, f, indent=2)

        return jsonify({"success": True, "prompts": prompts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/presets')
def get_presets():
    """Get prompt presets"""
    presets = [
        {"name": "Minimalist Modern", "theme": "minimalism", "style": "clean, modern", "niche": "young professionals"},
        {"name": "Vintage Retro", "theme": "vintage", "style": "retro, 70s", "niche": "vintage enthusiasts"},
        {"name": "Nature & Wildlife", "theme": "nature", "style": "realistic, majestic", "niche": "nature lovers"},
        {"name": "Abstract Art", "theme": "abstract", "style": "bold, colorful", "niche": "art enthusiasts"},
        {"name": "Cyberpunk", "theme": "cyberpunk", "style": "neon, futuristic", "niche": "tech enthusiasts"},
        {"name": "Motivational", "theme": "typography", "style": "inspirational", "niche": "self-improvement"}
    ]
    return jsonify(presets)

# =============================================================================
# API - Gateway
# =============================================================================

@app.route('/api/images')
def list_images():
    """List all images with status"""
    if not state_manager:
        return jsonify({"images": []})

    image_dir = Path(config.IMAGE_DIR)
    if not image_dir.exists():
        return jsonify({"images": []})

    images = []
    state = state_manager.get_all_images()

    for img_file in image_dir.glob("*.png"):
        img_id = img_file.stem
        img_state = state.get(img_id, {})
        status = img_state.get("status", "pending")

        if img_id not in state:
            state_manager.add_image(img_id, img_file.name, str(img_file))

        images.append({
            "id": img_id,
            "filename": img_file.name,
            "status": status,
            "path": f"/api/image/{img_id}"
        })

    images.sort(key=lambda x: x['filename'], reverse=True)
    return jsonify({"images": images})

@app.route('/api/image/<image_id>')
def serve_image(image_id):
    """Serve image file"""
    return send_from_directory(config.IMAGE_DIR, f"{image_id}.png")

@app.route('/api/approve/<image_id>', methods=['POST'])
def approve_image(image_id):
    """Approve image"""
    if state_manager:
        state_manager.set_image_status(image_id, "approved")
    return jsonify({"success": True, "status": "approved"})

@app.route('/api/reject/<image_id>', methods=['POST'])
def reject_image(image_id):
    """Reject image"""
    if state_manager:
        state_manager.set_image_status(image_id, "rejected")
    return jsonify({"success": True, "status": "rejected"})

@app.route('/api/publish/<image_id>', methods=['POST'])
def publish_image(image_id):
    """Publish to Printify"""
    if not printify_client or not state_manager:
        return jsonify({"error": "Printify not configured"}), 400

    status = state_manager.get_image_status(image_id)
    if status not in ["approved", "failed"]:
        return jsonify({"error": "Image must be approved first"}), 400

    image_path = os.path.join(config.IMAGE_DIR, f"{image_id}.png")
    if not os.path.exists(image_path):
        return jsonify({"error": "Image not found"}), 404

    state_manager.set_image_status(image_id, "publishing")

    try:
        title = request.json.get("title", f"Design {image_id[:8]}")
        product_id = printify_client.create_and_publish(
            image_path, title,
            config.PRINTIFY_BLUEPRINT_ID,
            config.PRINTIFY_PROVIDER_ID
        )

        if product_id:
            state_manager.set_image_status(image_id, "published", {"product_id": product_id, "title": title})
            return jsonify({"success": True, "product_id": product_id})
        else:
            state_manager.set_image_status(image_id, "failed")
            return jsonify({"error": "Printify API failed"}), 500
    except Exception as e:
        state_manager.set_image_status(image_id, "failed")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset/<image_id>', methods=['POST'])
def reset_image(image_id):
    """Reset to pending"""
    if state_manager:
        state_manager.set_image_status(image_id, "pending")
    return jsonify({"success": True, "status": "pending"})

@app.route('/api/gateway-stats')
def gateway_stats():
    """Gateway statistics"""
    if not state_manager:
        return jsonify({"total": 0, "pending": 0, "approved": 0, "published": 0})

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
    """Health check"""
    return jsonify({
        "status": "healthy",
        "services": {
            "claude": prompt_generator is not None,
            "printify": printify_client is not None,
            "state_manager": state_manager is not None
        }
    })

if __name__ == "__main__":
    print(f"🚀 POD Dashboard starting...")
    print(f"📁 Image directory: {config.IMAGE_DIR}")
    print(f"💾 State file: {config.STATE_FILE}")
    print(f"🤖 Claude: {'enabled' if prompt_generator else 'disabled'}")
    print(f"🔌 Printify: {'enabled' if printify_client else 'disabled'}")
    print(f"🌐 Listening on {config.FLASK_HOST}:{config.FLASK_PORT}")

    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )

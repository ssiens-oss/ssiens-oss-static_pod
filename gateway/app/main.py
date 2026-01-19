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
from typing import Dict, Any, Tuple, List
import re
import uuid
import requests
import base64
from io import BytesIO

# Load environment
load_dotenv()

# Import modules
from app import config
from app.state import StateManager, ImageStatus, StateManagerError
from app.printify_client import PrintifyClient, RetryConfig, PrintifyError
from app.runpod_adapter import create_comfyui_client

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

# Initialize ComfyUI/RunPod client
comfyui_client = None
try:
    comfyui_client = create_comfyui_client(
        config.config.comfyui.api_url,
        config.config.comfyui.runpod_api_key
    )
    if comfyui_client:
        logger.info("✓ RunPod serverless client initialized")
    else:
        logger.info("✓ Direct ComfyUI connection configured")
except Exception as e:
    logger.warning(f"⚠ ComfyUI/RunPod client setup: {e}")


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


def build_prompt_text(prompt: str, style: str = "", genre: str = "") -> str:
    """
    Build the full prompt text with optional style and genre.

    Args:
        prompt: Base prompt text
        style: Optional style descriptor
        genre: Optional genre descriptor
    """
    parts = [prompt.strip()]
    if style:
        parts.append(f"{style} style")
    if genre:
        parts.append(f"{genre} genre")
    return ", ".join(part for part in parts if part)


def build_comfyui_workflow(
    prompt: str,
    seed: int | None = None,
    width: int = 2048,
    height: int = 2560,
    steps: int = 28,
    cfg_scale: float = 3.5
) -> Dict[str, Any]:
    """
    Build a Flux workflow for ComfyUI optimized for t-shirt printing.

    Default resolution: 2048x2560 (6.8"x8.5" at 300 DPI)
    Balanced for GPU memory limits while maintaining print quality.
    Can be upscaled 2x for larger prints if needed.
    """
    if seed is None:
        seed = int.from_bytes(os.urandom(4), byteorder="little")

    return {
        "3": {
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg_scale,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "flux1-dev-fp8.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": prompt,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "blurry, out of focus, low resolution, pixelated, jpeg artifacts, text, watermark, signature, low quality, worst quality, compressed, noisy",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "ComfyUI",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }


def sanitize_comfyui_filename(filename: str, subfolder: str = "") -> str:
    """Build a safe filename for downloaded ComfyUI outputs."""
    safe_name = Path(filename).name
    safe_subfolder = subfolder.replace("/", "_").replace("\\", "_") if subfolder else ""
    if safe_subfolder:
        return f"{safe_subfolder}_{safe_name}"
    return safe_name


def download_comfyui_image(image_meta: Dict[str, Any]) -> str | None:
    """Download a single ComfyUI image to the local image directory."""
    filename = image_meta.get("filename")
    if not filename:
        return None

    subfolder = image_meta.get("subfolder") or ""
    image_type = image_meta.get("type") or "output"
    safe_name = sanitize_comfyui_filename(filename, subfolder)

    if not safe_name.lower().endswith(".png"):
        logger.warning("Skipping non-png output: %s", safe_name)
        return None

    output_path = Path(config.IMAGE_DIR) / safe_name
    if output_path.exists():
        return str(output_path)

    try:
        response = requests.get(
            f"{config.COMFYUI_API_URL}/view",
            params={
                "filename": filename,
                "subfolder": subfolder,
                "type": image_type
            },
            timeout=60
        )
        response.raise_for_status()
        output_path.write_bytes(response.content)
        return str(output_path)
    except requests.RequestException as exc:
        logger.error("Failed to download ComfyUI image %s: %s", filename, exc)
        return None


def sync_comfyui_outputs(history: Dict[str, Any], prompt_id: str) -> List[str]:
    """Download ComfyUI outputs for a completed prompt."""
    downloaded: List[str] = []
    prompt_entry = history.get(prompt_id, {})
    outputs = prompt_entry.get("outputs", {})

    for node_id in outputs:
        images = outputs[node_id].get("images", [])
        for image_meta in images:
            local_path = download_comfyui_image(image_meta)
            if not local_path:
                continue
            image_id = Path(local_path).stem
            try:
                state_manager.add_image(image_id, Path(local_path).name, local_path)
            except StateManagerError:
                pass
            downloaded.append(local_path)

    return downloaded


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


def download_and_save_image(image_data: str, filename: str = None) -> Tuple[str, str]:
    """
    Download and save an image from base64 data or URL

    Args:
        image_data: Base64 encoded image or URL
        filename: Optional filename, will generate if not provided

    Returns:
        Tuple of (image_id, file_path)
    """
    try:
        # Validate input
        if not image_data or not isinstance(image_data, str):
            raise ValueError(f"Invalid image_data: type={type(image_data)}, empty={not image_data}")

        logger.info(f"📥 Processing image data (length: {len(image_data)}, starts with: {image_data[:50]}...)")

        # Generate unique image ID
        image_id = f"generated_{uuid.uuid4().hex[:8]}_0"
        if not filename:
            filename = f"{image_id}.png"

        file_path = config.config.filesystem.image_dir / filename
        logger.info(f"📁 Target path: {file_path}")

        # Check if data is URL or base64
        if image_data.startswith('http://') or image_data.startswith('https://'):
            # Download from URL
            logger.info(f"🌐 Downloading image from URL: {image_data[:80]}...")
            response = requests.get(image_data, timeout=30)
            response.raise_for_status()
            image_bytes = response.content
            logger.info(f"✓ Downloaded {len(image_bytes)} bytes")
        else:
            # Assume base64
            logger.info(f"🔐 Decoding base64 image data (length: {len(image_data)})...")
            # Remove data URL prefix if present
            if ',' in image_data:
                logger.info(f"  Removing data URL prefix...")
                image_data = image_data.split(',', 1)[1]
            image_bytes = base64.b64decode(image_data)
            logger.info(f"✓ Decoded {len(image_bytes)} bytes")

        # Validate image data
        if len(image_bytes) < 100:
            raise ValueError(f"Image data too small: {len(image_bytes)} bytes")

        # Save image
        with open(file_path, 'wb') as f:
            f.write(image_bytes)

        logger.info(f"✅ Saved image: {file_path} ({len(image_bytes)} bytes)")

        # Add to state manager
        state_manager.add_image(image_id, filename, str(file_path))
        logger.info(f"✅ Added image to state: {image_id}")

        return image_id, str(file_path)

    except Exception as e:
        logger.error(f"❌ Failed to download/save image: {e}", exc_info=True)
        raise


@app.route('/api/generate', methods=['POST'])
def generate_image():
    """
    Submit a prompt to ComfyUI via the configured API URL.

    Expected JSON body:
    {
        "prompt": "Base prompt text",
        "style": "Optional style",
        "genre": "Optional genre"
    }
    """
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    style = (data.get("style") or "").strip()
    genre = (data.get("genre") or "").strip()

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    full_prompt = build_prompt_text(prompt, style, genre)
    logger.info(f"Using {'RunPod Serverless' if comfyui_client else 'direct ComfyUI'} for generation: {prompt[:50]}...")

    workflow = build_comfyui_workflow(
        full_prompt,
        seed=data.get("seed"),
        width=data.get("width", 2048),
        height=data.get("height", 2560),
        steps=data.get("steps", 28),
        cfg_scale=data.get("cfg_scale", 3.5)
    )

    client_id = data.get("client_id") or f"pod-gateway-{uuid.uuid4().hex[:8]}"

    try:
        # Use RunPod serverless client if available, otherwise direct ComfyUI
        if comfyui_client:
            # RunPod serverless
            result = comfyui_client.submit_workflow(workflow, client_id, timeout=120)

            # Download and save images from output
            output = result.get("output", {})
            saved_images = []

            # Debug: Log full output structure
            logger.info(f"🔍 RunPod result keys: {list(result.keys())}")
            logger.info(f"🔍 RunPod output keys: {list(output.keys())}")

            # Log the full output for debugging (truncated to avoid huge logs)
            import json
            try:
                output_json = json.dumps(output, indent=2)
                logger.info(f"🔍 Full RunPod output:\n{output_json[:2000]}")
            except:
                logger.info(f"🔍 RunPod output (repr): {repr(output)[:2000]}")

            # RunPod serverless worker returns images in output
            # Check for images in various possible formats
            if "images" in output:
                # Array of images
                logger.info(f"Found {len(output['images'])} image(s) in output['images']")
                for i, img_data in enumerate(output["images"]):
                    try:
                        if isinstance(img_data, dict):
                            # Extract image data from dict
                            image_url_or_data = img_data.get("url") or img_data.get("data") or img_data.get("image") or img_data.get("base64")
                        else:
                            image_url_or_data = img_data

                        if image_url_or_data:
                            image_id, file_path = download_and_save_image(image_url_or_data)
                            saved_images.append({"id": image_id, "path": file_path})
                            logger.info(f"✓ Downloaded image {i+1}/{len(output['images'])}")
                    except Exception as e:
                        logger.error(f"Failed to save image {i+1} from output: {e}")
            elif "image" in output:
                # Single image
                logger.info(f"Found single image in output['image']")
                try:
                    image_data = output["image"]
                    if isinstance(image_data, dict):
                        image_data = image_data.get("url") or image_data.get("data") or image_data.get("image") or image_data.get("base64")

                    if image_data:
                        image_id, file_path = download_and_save_image(image_data)
                        saved_images.append({"id": image_id, "path": file_path})
                except Exception as e:
                    logger.error(f"Failed to save image from output: {e}")
            elif "message" in output:
                # ComfyUI format with message containing image info
                logger.info("Checking output['message'] for images...")
                message = output.get("message", {})
                if isinstance(message, dict) and "images" in message:
                    for i, img_info in enumerate(message["images"]):
                        try:
                            # ComfyUI returns filename, subfolder, type
                            if isinstance(img_info, dict):
                                # This might be a reference to an image on the ComfyUI server
                                # For RunPod serverless, images should be base64 or URLs
                                logger.warning(f"Image {i+1} is a reference, not direct data")
                            else:
                                image_id, file_path = download_and_save_image(img_info)
                                saved_images.append({"id": image_id, "path": file_path})
                        except Exception as e:
                            logger.error(f"Failed to save image from message: {e}")
            else:
                logger.warning(f"⚠️  No recognized image format in RunPod output. Keys: {list(output.keys())}")
                logger.warning(f"⚠️  Attempting to search all output fields for images...")

                # Fallback: Search ALL fields for anything that looks like image data
                for key, value in output.items():
                    logger.info(f"  Checking field '{key}' (type: {type(value).__name__})")

                    # Check if it's a list
                    if isinstance(value, list) and len(value) > 0:
                        logger.info(f"    Found list with {len(value)} items")
                        for i, item in enumerate(value):
                            logger.info(f"    Item {i} type: {type(item).__name__}")
                            if isinstance(item, str) and len(item) > 100:
                                logger.info(f"    Item {i} looks like string data (length: {len(item)})")
                                try:
                                    image_id, file_path = download_and_save_image(item)
                                    saved_images.append({"id": image_id, "path": file_path})
                                    logger.info(f"    ✓ Successfully saved image from '{key}[{i}]'")
                                except Exception as e:
                                    logger.debug(f"    Failed to save as image: {e}")

                    # Check if it's a string that might be base64 or URL
                    elif isinstance(value, str) and len(value) > 100:
                        logger.info(f"    Field '{key}' is string (length: {len(value)})")
                        try:
                            image_id, file_path = download_and_save_image(value)
                            saved_images.append({"id": image_id, "path": file_path})
                            logger.info(f"    ✓ Successfully saved image from '{key}'")
                        except Exception as e:
                            logger.debug(f"    Failed to save as image: {e}")

            if len(saved_images) > 0:
                logger.info(f"✓ Saved {len(saved_images)} image(s) from RunPod output")
            else:
                logger.error(f"❌ No images could be extracted from RunPod output!")

            return jsonify({
                "prompt_id": result.get("prompt_id"),
                "job_id": result.get("job_id"),
                "status": result.get("status"),
                "prompt": full_prompt,
                "images": saved_images
            })
        else:
            # Direct ComfyUI connection
            payload = {
                "prompt": workflow,
                "client_id": client_id
            }
            response = requests.post(
                f"{config.COMFYUI_API_URL}/prompt",
                json=payload,
                timeout=30
            )

            if not response.ok:
                logger.error("ComfyUI error: %s", response.text)
                return jsonify({"error": "ComfyUI request failed", "details": response.text}), 502

            result = response.json()
            return jsonify({
                "prompt_id": result.get("prompt_id"),
                "prompt": full_prompt
            })

    except requests.RequestException as exc:
        logger.error("ComfyUI request failed: %s", exc)
        return jsonify({"error": "Failed to connect to ComfyUI"}), 502
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.route('/api/generation_status')
def generation_status():
    """Get generation status - handles both RunPod serverless and direct ComfyUI."""
    prompt_id = request.args.get("prompt_id")
    if not prompt_id:
        return jsonify({"error": "prompt_id is required"}), 400

    # For RunPod serverless, jobs complete synchronously
    # The status is already known from the original request
    if comfyui_client:
        # RunPod serverless - return completed status
        # Since RunPod uses sync requests, if we got a prompt_id, the job is done
        return jsonify({
            "history": {
                prompt_id: {
                    "status": {
                        "completed": True,
                        "status_str": "success"
                    }
                }
            },
            "downloaded": []  # Images are not auto-downloaded for serverless
        })

    # Direct ComfyUI - use history endpoint
    try:
        response = requests.get(
            f"{config.COMFYUI_API_URL}/history/{prompt_id}",
            timeout=30
        )
    except requests.RequestException as exc:
        logger.error("ComfyUI status request failed: %s", exc)
        return jsonify({"error": "Failed to connect to ComfyUI"}), 502

    if not response.ok:
        logger.error("ComfyUI status error: %s", response.text)
        return jsonify({"error": "Failed to fetch status", "details": response.text}), 502

    history = response.json()
    prompt_entry = history.get(prompt_id, {})
    status_info = prompt_entry.get("status", {})
    downloaded = []
    if status_info.get("completed"):
        downloaded = sync_comfyui_outputs(history, prompt_id)

    return jsonify({
        "history": history,
        "downloaded": downloaded
    })


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
        blueprint_id = request_data.get("blueprint_id", config.PRINTIFY_BLUEPRINT_ID)
        provider_id = request_data.get("provider_id", config.PRINTIFY_PROVIDER_ID)

        # Validate price
        if not isinstance(price_cents, int) or price_cents < 0:
            return jsonify({"success": False, "error": "Invalid price"}), 400
        if not isinstance(blueprint_id, int) or blueprint_id <= 0:
            return jsonify({"success": False, "error": "Invalid blueprint ID"}), 400
        if not isinstance(provider_id, int) or provider_id <= 0:
            return jsonify({"success": False, "error": "Invalid provider ID"}), 400

        product_id = printify_client.create_and_publish(
            image_path=image_path,
            title=title,
            blueprint_id=blueprint_id,
            provider_id=provider_id,
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

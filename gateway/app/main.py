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

# Load environment from parent directory (where .env actually is)
# Gateway runs from gateway/ subdirectory, but .env is in project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

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


def generate_auto_title(image_id: str, prompt: str = None) -> str:
    """
    Generate automatic title from image ID or prompt

    Args:
        image_id: Image identifier (e.g., "generated_787679c7_0")
        prompt: Optional prompt used to generate the image

    Returns:
        Human-readable product title
    """
    import re

    # If we have a prompt, use it to create a better title
    if prompt:
        # Clean up prompt (remove common negative prompts, technical terms)
        cleaned = re.sub(r'\b(high quality|vibrant colors|print-ready|professional design|centered composition)\b', '', prompt, flags=re.IGNORECASE)
        cleaned = cleaned.strip(', ')

        # Capitalize and limit length
        title = ' '.join(word.capitalize() for word in cleaned.split())
        if len(title) > 100:
            title = title[:97] + "..."
        return title

    # Fallback: Generate from image ID
    # Extract any meaningful parts from the ID
    parts = image_id.replace('_', ' ').split()

    # Remove technical parts (like "generated", numbers)
    meaningful_parts = [p for p in parts if not p.isdigit() and p.lower() != 'generated']

    if meaningful_parts:
        title = ' '.join(word.capitalize() for word in meaningful_parts)
    else:
        # Last resort: use a generic title with unique ID
        unique_part = image_id.split('_')[1] if '_' in image_id else image_id[:8]
        title = f"Abstract Design {unique_part.upper()}"

    return title


def generate_auto_description(title: str, image_id: str, style: str = "abstract art") -> str:
    """
    Generate automatic product description

    Args:
        title: Product title
        image_id: Image identifier
        style: Art style (default: "abstract art")

    Returns:
        Product description
    """
    templates = [
        f"Unique {style} design featuring bold colors and striking composition. Perfect for casual wear and making a statement.",
        f"Eye-catching {style} creation with vibrant details. Stand out with this exclusive design on premium quality apparel.",
        f"Original {style} artwork transformed into wearable art. Express your style with this one-of-a-kind design.",
        f"Bold and dynamic {style} piece that combines creativity with comfort. Limited edition design for the modern trendsetter.",
        f"Stunning {style} design with intricate patterns and vivid colors. Elevate your wardrobe with this artistic creation."
    ]

    # Use hash of image_id to consistently select the same template for the same image
    import hashlib
    hash_val = int(hashlib.md5(image_id.encode()).hexdigest(), 16)
    template_idx = hash_val % len(templates)

    return templates[template_idx]


def build_comfyui_workflow(
    prompt: str,
    seed: int | None = None,
    width: int = 1024,
    height: int = 1024,
    steps: int = 25,
    cfg_scale: float = 3.5
) -> Dict[str, Any]:
    """Build a Flux-optimized workflow for ComfyUI (POD quality settings)."""
    if seed is None:
        seed = int.from_bytes(os.urandom(4), byteorder="little")

    return {
        "3": {
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg_scale,
                "sampler_name": "euler",
                "scheduler": "simple",  # Flux-optimized scheduler
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
                "text": "",  # Flux handles negatives differently - empty is better
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


def download_and_save_image(image_data: str, filename: str | None = None) -> Tuple[str, str] | None:
    """Download and save an image from base64 data or URL."""
    if not image_data:
        return None

    image_id = f"generated_{uuid.uuid4().hex[:8]}_0"
    if not filename:
        filename = f"{image_id}.png"

    file_path = Path(config.IMAGE_DIR) / filename

    try:
        if image_data.startswith(("http://", "https://")):
            logger.info("Downloading image from URL: %s", image_data[:80])
            response = requests.get(image_data, timeout=60)
            response.raise_for_status()
            file_path.write_bytes(response.content)
        else:
            logger.info("Decoding base64 image data")
            data_to_decode = image_data.split(",", 1)[1] if "," in image_data else image_data
            file_path.write_bytes(base64.b64decode(data_to_decode))

        state_manager.add_image(image_id, filename, str(file_path))
        return image_id, str(file_path)
    except (requests.RequestException, ValueError, base64.binascii.Error) as exc:
        logger.error("Failed to save image data: %s", exc)
        return None
    except StateManagerError as exc:
        logger.error("Failed to register image in state: %s", exc)
        return None


def extract_image_payloads(output: Any) -> List[Dict[str, Any]]:
    """Extract possible image payloads from RunPod output."""
    payloads: List[Dict[str, Any]] = []
    stack = [output]

    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            if "images" in current and isinstance(current["images"], list):
                for item in current["images"]:
                    if isinstance(item, dict):
                        payloads.append(item)
                    elif isinstance(item, str):
                        payloads.append({"data": item})
            if "image" in current and isinstance(current["image"], str):
                payloads.append({"data": current["image"]})
            for value in current.values():
                stack.append(value)
        elif isinstance(current, list):
            stack.extend(current)

    return payloads


def save_runpod_output_images(output: Dict[str, Any]) -> List[Dict[str, str]]:
    """Save any images found in a RunPod output payload."""
    saved_images: List[Dict[str, str]] = []
    payloads = extract_image_payloads(output)

    for payload in payloads:
        image_data = (
            payload.get("url")
            or payload.get("data")
            or payload.get("image")
            or payload.get("base64")
        )
        if image_data:
            saved = download_and_save_image(image_data)
            if saved:
                image_id, file_path = saved
                saved_images.append({"id": image_id, "path": file_path})
            continue

        if payload.get("filename"):
            local_path = download_comfyui_image(payload)
            if local_path:
                image_id = Path(local_path).stem
                try:
                    state_manager.add_image(image_id, Path(local_path).name, local_path)
                except StateManagerError:
                    pass
                saved_images.append({"id": image_id, "path": local_path})

    return saved_images


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
                "updated_at": img_state.get("updated_at"),
                "error_message": img_state.get("error_message"),
                "product_id": img_state.get("product_id"),
                "title": img_state.get("title")
            })

        # Sort by filename (newest first)
        images.sort(key=lambda x: x['filename'], reverse=True)

        return jsonify({"images": images, "count": len(images)})

    except Exception as e:
        logger.error(f"Error listing images: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


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
        width=data.get("width", 1024),
        height=data.get("height", 1024),
        steps=data.get("steps", 25),  # Flux-optimized: higher quality
        cfg_scale=data.get("cfg_scale", 3.5)  # Flux-optimized: prevents blur
    )

    client_id = data.get("client_id") or f"pod-gateway-{uuid.uuid4().hex[:8]}"

    try:
        # Use RunPod serverless client if available, otherwise direct ComfyUI
        if comfyui_client:
            # RunPod serverless
            result = comfyui_client.submit_workflow(workflow, client_id, timeout=120)
            saved_images: List[Dict[str, str]] = []
            if result.get("status") == "COMPLETED":
                output = result.get("output", {})
                saved_images = save_runpod_output_images(output)

            return jsonify({
                "prompt_id": result.get("prompt_id"),
                "job_id": result.get("job_id"),
                "status": result.get("status"),
                "prompt": full_prompt,
                "images": saved_images,
                "source": "runpod"
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
                "prompt": full_prompt,
                "source": "comfyui"
            })

    except requests.RequestException as exc:
        logger.error("ComfyUI request failed: %s", exc)
        return jsonify({"error": "Failed to connect to ComfyUI"}), 502
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.route('/api/generation_status')
def generation_status():
    """Proxy generation status from ComfyUI history endpoint."""
    prompt_id = request.args.get("prompt_id")
    if not prompt_id:
        return jsonify({"error": "prompt_id is required"}), 400

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


@app.route('/api/runpod_status')
def runpod_status():
    """Check status for RunPod serverless jobs and download outputs when complete."""
    job_id = request.args.get("job_id")
    if not job_id:
        return jsonify({"error": "job_id is required"}), 400

    if not comfyui_client:
        return jsonify({"error": "RunPod client not configured"}), 400

    try:
        result = comfyui_client.get_job_status(job_id)
        status = result.get("status")
        saved_images: List[Dict[str, str]] = []

        if status == "COMPLETED":
            output = result.get("output", {})
            saved_images = save_runpod_output_images(output)

        if status == "FAILED":
            return jsonify({
                "status": status,
                "error": result.get("error", "RunPod job failed")
            }), 500

        return jsonify({
            "status": status,
            "job_id": job_id,
            "images": saved_images
        })
    except Exception as exc:
        logger.error("RunPod status check failed: %s", exc)
        return jsonify({"error": "Failed to check RunPod job"}), 502


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

    # Auto-generate title if not provided
    title = request_data.get("title")
    if not title:
        prompt = request_data.get("prompt")  # Optional prompt hint
        title = generate_auto_title(image_id, prompt)
        logger.info(f"📝 Auto-generated title: {title}")

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
        # Auto-generate description if not provided
        description = request_data.get("description")
        if not description:
            style = request_data.get("style", "abstract art")
            description = generate_auto_description(title, image_id, style)
            logger.info(f"📄 Auto-generated description: {description[:50]}...")
        price_cents = request_data.get("price_cents", config.config.printify.default_price_cents)
        blueprint_id = request_data.get("blueprint_id", config.PRINTIFY_BLUEPRINT_ID)
        provider_id = request_data.get("provider_id", config.PRINTIFY_PROVIDER_ID)

        # POD optimization: configurable color filter and variant limit
        color_filter = request_data.get("color_filter", config.config.printify.color_filter)
        max_variants = request_data.get("max_variants", config.config.printify.max_variants)

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
            description=description,
            color_filter=color_filter,
            max_variants=max_variants
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


@app.route('/api/batch_publish', methods=['POST'])
def batch_publish():
    """
    Batch publish multiple images to Printify

    Expected JSON body:
    {
        "image_ids": ["image_id_1", "image_id_2", ...],  // Optional, if empty will use all approved images
        "auto_approve": false,  // Auto-approve pending images before publishing
        "style": "abstract art",  // Style for auto-generated descriptions
        "price_cents": 3499,  // Optional override
        "color_filter": "black",  // Optional override
        "max_variants": 50  // Optional override
    }

    Returns:
        JSON with batch results
    """
    if not printify_client:
        return jsonify({
            "success": False,
            "error": "Printify not configured"
        }), 400

    try:
        request_data = request.get_json() or {}
    except Exception as e:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400

    # Get parameters
    image_ids = request_data.get("image_ids", [])
    auto_approve = request_data.get("auto_approve", False)
    style = request_data.get("style", "abstract art")
    price_cents = request_data.get("price_cents")
    color_filter = request_data.get("color_filter")
    max_variants = request_data.get("max_variants")

    # If no image IDs provided, use all approved (or pending if auto_approve)
    if not image_ids:
        all_images = state_manager.get_all_images()
        if auto_approve:
            # Get pending images and auto-approve them
            image_ids = [
                img_id for img_id, img_data in all_images.items()
                if img_data.get("status") in [ImageStatus.PENDING.value, ImageStatus.APPROVED.value]
            ]
        else:
            # Get only approved images
            image_ids = [
                img_id for img_id, img_data in all_images.items()
                if img_data.get("status") == ImageStatus.APPROVED.value
            ]

    logger.info(f"🔄 Batch publishing {len(image_ids)} images...")

    results = {
        "total": len(image_ids),
        "succeeded": [],
        "failed": [],
        "skipped": []
    }

    # Process each image
    for idx, image_id in enumerate(image_ids, 1):
        logger.info(f"📦 [{idx}/{len(image_ids)}] Processing {image_id}...")

        # Validate image ID
        is_valid, error = validate_image_id(image_id)
        if not is_valid:
            results["skipped"].append({"image_id": image_id, "reason": error})
            continue

        # Auto-approve if requested
        current_status = state_manager.get_image_status(image_id)
        if auto_approve and current_status == ImageStatus.PENDING.value:
            try:
                state_manager.set_image_status(image_id, ImageStatus.APPROVED.value)
                logger.info(f"✓ Auto-approved {image_id}")
            except StateManagerError as e:
                results["skipped"].append({"image_id": image_id, "reason": f"Failed to auto-approve: {str(e)}"})
                continue

        # Check status
        current_status = state_manager.get_image_status(image_id)
        if current_status not in [ImageStatus.APPROVED.value, ImageStatus.FAILED.value]:
            results["skipped"].append({"image_id": image_id, "reason": f"Not approved (status: {current_status})"})
            continue

        # Get image path
        image_path = os.path.join(config.IMAGE_DIR, f"{image_id}.png")
        is_valid, error = validate_image_file(image_path)
        if not is_valid:
            results["failed"].append({"image_id": image_id, "error": error})
            continue

        # Auto-generate metadata
        title = generate_auto_title(image_id)
        description = generate_auto_description(title, image_id, style)

        logger.info(f"  📝 Title: {title}")
        logger.info(f"  📄 Description: {description[:50]}...")

        # Set publishing status
        try:
            state_manager.set_image_status(image_id, ImageStatus.PUBLISHING.value)
        except StateManagerError as e:
            results["failed"].append({"image_id": image_id, "error": f"Status update failed: {str(e)}"})
            continue

        # Publish
        try:
            publish_params = {
                "image_path": image_path,
                "title": title,
                "blueprint_id": config.PRINTIFY_BLUEPRINT_ID,
                "provider_id": config.PRINTIFY_PROVIDER_ID,
                "description": description
            }

            # Add optional overrides
            if price_cents:
                publish_params["price_cents"] = price_cents
            if color_filter:
                publish_params["color_filter"] = color_filter
            if max_variants:
                publish_params["max_variants"] = max_variants

            product_id = printify_client.create_and_publish(**publish_params)

            if product_id:
                state_manager.set_image_status(image_id, ImageStatus.PUBLISHED.value, {
                    "product_id": product_id,
                    "title": title
                })
                results["succeeded"].append({
                    "image_id": image_id,
                    "product_id": product_id,
                    "title": title
                })
                logger.info(f"  ✅ Published: {product_id}")
            else:
                state_manager.set_image_status(image_id, ImageStatus.FAILED.value, {
                    "error_message": "Printify API failed"
                })
                results["failed"].append({"image_id": image_id, "error": "Printify API failed"})

        except Exception as e:
            error_msg = str(e)
            logger.error(f"  ❌ Error: {error_msg}")
            try:
                state_manager.set_image_status(image_id, ImageStatus.FAILED.value, {
                    "error_message": error_msg
                })
            except StateManagerError:
                pass
            results["failed"].append({"image_id": image_id, "error": error_msg})

    # Summary
    logger.info(f"✅ Batch complete: {len(results['succeeded'])} succeeded, {len(results['failed'])} failed, {len(results['skipped'])} skipped")

    return jsonify({
        "success": True,
        "results": results,
        "summary": {
            "total": results["total"],
            "succeeded": len(results["succeeded"]),
            "failed": len(results["failed"]),
            "skipped": len(results["skipped"])
        }
    })


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

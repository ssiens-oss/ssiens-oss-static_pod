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

# Load environment
load_dotenv()

# Import modules
from app import config
from app.state import StateManager, ImageStatus, StateManagerError
from app.printify_client import PrintifyClient, RetryConfig, PrintifyError
from app.runpod_client import create_comfyui_client
from app.platforms import PrintifyPlatform, ZazzlePlatform, RedbubblePlatform
from app.product_catalog import (
    get_all_products,
    get_popular_products,
    get_products_by_category,
    get_product,
    ProductCategory,
    validate_image_resolution
)
from app.analytics import (
    calculate_performance_score,
    calculate_net_profit,
    is_bestseller,
    get_platform_fee,
    get_fulfillment_cost
)

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

# Initialize POD platforms
platforms = {}

# Printify platform
if config.config.printify.is_configured():
    try:
        printify_config = {
            'api_key': config.PRINTIFY_API_KEY,
            'shop_id': config.PRINTIFY_SHOP_ID,
            'blueprint_id': config.PRINTIFY_BLUEPRINT_ID,
            'provider_id': config.PRINTIFY_PROVIDER_ID,
            'default_price_cents': config.config.printify.default_price_cents,
            'max_retries': config.config.retry.max_retries,
            'initial_backoff': config.config.retry.initial_backoff_seconds,
            'max_backoff': config.config.retry.max_backoff_seconds,
            'backoff_multiplier': config.config.retry.backoff_multiplier
        }
        platforms['printify'] = PrintifyPlatform(printify_config)
        logger.info("✓ Printify platform initialized")
    except Exception as e:
        logger.error(f"✗ Printify platform failed: {e}")

# Zazzle platform (if configured)
zazzle_api_key = os.getenv('ZAZZLE_API_KEY')
zazzle_api_secret = os.getenv('ZAZZLE_API_SECRET')
zazzle_store_id = os.getenv('ZAZZLE_STORE_ID')
if zazzle_api_key and zazzle_api_secret and zazzle_store_id:
    try:
        zazzle_config = {
            'api_key': zazzle_api_key,
            'api_secret': zazzle_api_secret,
            'store_id': zazzle_store_id,
            'product_type': os.getenv('ZAZZLE_PRODUCT_TYPE', 'tshirt')
        }
        platforms['zazzle'] = ZazzlePlatform(zazzle_config)
        logger.info("✓ Zazzle platform initialized")
    except Exception as e:
        logger.error(f"✗ Zazzle platform failed: {e}")

# Redbubble platform (manual workflow)
redbubble_username = os.getenv('REDBUBBLE_USERNAME')
if redbubble_username:
    try:
        redbubble_config = {
            'username': redbubble_username,
            'manual_upload': True
        }
        platforms['redbubble'] = RedbubblePlatform(redbubble_config)
        logger.info("✓ Redbubble platform initialized (manual workflow)")
    except Exception as e:
        logger.error(f"✗ Redbubble platform failed: {e}")

logger.info(f"📦 Configured platforms: {', '.join(platforms.keys()) or 'none'}")


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


def generate_product_title(prompt: str, style: str = "", genre: str = "") -> str:
    """
    Generate SEO-friendly product title from prompt

    Creates descriptive, keyword-rich titles for POD listings

    Args:
        prompt: Base prompt text
        style: Optional style descriptor
        genre: Optional genre descriptor

    Returns:
        Product title optimized for listings
    """
    # Extract key descriptive words from prompt
    words = prompt.strip().split()

    # Remove common articles and prepositions
    stop_words = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from'}
    keywords = [w for w in words if w.lower() not in stop_words][:5]  # Take first 5 meaningful words

    # Capitalize first letter of each keyword
    title_parts = [word.capitalize() for word in keywords]

    # Add style/genre if provided
    if style:
        title_parts.insert(0, style.capitalize())
    if genre:
        title_parts.append(f"- {genre.capitalize()}")

    # Build title
    title = " ".join(title_parts)

    # Add product type descriptor
    title = f"{title} Design"

    # Ensure reasonable length (max 140 chars for most platforms)
    if len(title) > 140:
        title = title[:137] + "..."

    return title


def build_prompt_text(prompt: str, style: str = "", genre: str = "") -> str:
    """
    Build POD-optimized prompt text with style and genre.

    Optimizations for Print-on-Demand:
    - High contrast for visibility on products
    - Bold, clear designs
    - Centered composition for product placement
    - Professional quality output

    Args:
        prompt: Base prompt text
        style: Optional style descriptor
        genre: Optional genre descriptor
    """
    # Start with base prompt
    parts = [prompt.strip()]

    # Add style if provided
    if style:
        parts.append(f"{style} style")

    # Add genre if provided
    if genre:
        parts.append(f"{genre} genre")

    # Add POD-specific quality enhancements
    pod_enhancements = [
        "high contrast",
        "bold colors",
        "centered composition",
        "professional design",
        "clean background",
        "sharp details",
        "vibrant",
        "eye-catching"
    ]

    full_prompt = ", ".join(part for part in parts if part)
    full_prompt += ", " + ", ".join(pod_enhancements)

    return full_prompt


def build_comfyui_workflow(
    prompt: str,
    seed: int | None = None,
    width: int = 3600,  # POD-optimized: 3600x3600 for good print quality
    height: int = 3600,
    steps: int = 30,  # Flux needs more steps than SDXL (30-50 for quality)
    cfg_scale: float = 2.0  # Flux works best at CFG 1.0-3.5 (NOT 7!)
) -> Dict[str, Any]:
    """
    Build a Flux-optimized workflow for ComfyUI.

    POD Resolution Guidelines:
    - Minimum: 2400x2400 (acceptable but not optimal)
    - Recommended: 3600x3600 (good balance)
    - Optimal: 4500x5400 (best for apparel)
    - Posters: 4800x6000

    Flux Sampling Guidelines (IMPORTANT):
    - CFG Scale: 1.0-3.5 (default 2.0) - Lower than SDXL!
    - Steps: 30-50 (default 30) - More than SDXL!
    - Scheduler: "simple" works best
    - Higher CFG = blurry/out of focus images
    - Fewer steps = lack of detail

    Default 3600x3600 @ 30 steps @ CFG 2.0 provides:
    - Sharp, detailed images
    - High enough DPI for quality prints
    - Reasonable processing time (~45-60s)
    - Works well for most products
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
                "scheduler": "simple",  # Changed from "normal" - better for Flux
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
                "text": "text, watermark, low quality, worst quality, blurry, muddy colors, washed out, low contrast, small details, tiny text, complex patterns, cluttered, messy background, amateur, poor composition",
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
                "updated_at": img_state.get("updated_at"),
                "metadata": img_state.get("metadata", {})
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

    # POD-optimized resolution (3600x3600 default for quality prints)
    width = data.get("width", 3600)
    height = data.get("height", 3600)

    # Flux-optimized sampling parameters
    steps = data.get("steps", 30)  # Flux needs 30-50 steps
    cfg_scale = data.get("cfg_scale", 2.0)  # Flux works best at 1.0-3.5 CFG

    # Warn if resolution is too low for POD
    if width < 2400 or height < 2400:
        logger.warning(f"⚠ Resolution {width}x{height} is below POD minimum (2400x2400). Quality may suffer.")

    # Warn if settings are likely to cause blurry images
    if cfg_scale > 4.0:
        logger.warning(f"⚠ CFG scale {cfg_scale} is too high for Flux. Recommend 1.0-3.5 for sharp images.")

    if steps < 25:
        logger.warning(f"⚠ Steps {steps} may be too low for quality. Recommend 30-50 for Flux.")

    workflow = build_comfyui_workflow(
        full_prompt,
        seed=data.get("seed"),
        width=width,
        height=height,
        steps=steps,
        cfg_scale=cfg_scale
    )

    logger.info(f"Generating image at {width}x{height}, {steps} steps, CFG {cfg_scale}")

    client_id = data.get("client_id") or f"pod-gateway-{uuid.uuid4().hex[:8]}"

    try:
        # Use RunPod serverless client if available, otherwise direct ComfyUI
        if comfyui_client:
            # RunPod serverless
            logger.info("Submitting workflow to RunPod serverless...")
            result = comfyui_client.submit_workflow(workflow, client_id, timeout=120)
            logger.info(f"RunPod result status: {result.get('status')}")
            logger.info(f"RunPod result keys: {list(result.keys())}")

            # If workflow completed, download images
            if result.get("status") == "COMPLETED" and "output" in result:
                logger.info("RunPod workflow completed, downloading images...")
                output = result.get("output", {})
                logger.debug(f"RunPod output structure: {output}")

                # Download images to the image directory
                saved_images = comfyui_client.download_images_from_output(
                    output,
                    Path(config.IMAGE_DIR)
                )

                if saved_images:
                    logger.info(f"Successfully downloaded {len(saved_images)} image(s)")

                    # Store prompt metadata for each image for auto-title generation
                    for img_path in saved_images:
                        img_id = Path(img_path).stem
                        try:
                            state_manager.set_image_status(img_id, ImageStatus.PENDING.value, {
                                "original_prompt": prompt,
                                "style": style,
                                "genre": genre,
                                "full_prompt": full_prompt
                            })
                        except StateManagerError as e:
                            logger.warning(f"Failed to store metadata for {img_id}: {e}")

                    # New images will be picked up on next /api/images call
                    return jsonify({
                        "status": "completed",
                        "prompt_id": result.get("prompt_id"),
                        "prompt": full_prompt,
                        "images": [Path(img).name for img in saved_images],
                        "message": f"Generated and downloaded {len(saved_images)} image(s)"
                    })
                else:
                    logger.warning("Workflow completed but no images were downloaded")
                    return jsonify({
                        "status": "completed",
                        "prompt_id": result.get("prompt_id"),
                        "prompt": full_prompt,
                        "warning": "Workflow completed but no images found in output"
                    })
            else:
                # Async job or still processing
                return jsonify({
                    "prompt_id": result.get("prompt_id"),
                    "job_id": result.get("job_id"),
                    "status": result.get("status"),
                    "prompt": full_prompt
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
    Reject and delete an image

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
        # Get image path
        image_path = os.path.join(config.IMAGE_DIR, f"{image_id}.png")

        # Delete the image file if it exists
        if os.path.exists(image_path):
            os.remove(image_path)
            logger.info(f"Deleted image file: {image_path}")

        # Remove from state manager
        state_manager.delete_image(image_id)
        logger.info(f"Image rejected and deleted: {image_id}")

        return jsonify({"success": True, "deleted": True})
    except Exception as e:
        logger.error(f"Failed to reject/delete image {image_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    """
    Get list of configured POD platforms

    Returns:
        JSON response with available platforms
    """
    platform_list = []
    for name, platform in platforms.items():
        platform_list.append({
            "name": name,
            "display_name": platform.platform_name,
            "configured": platform.is_configured()
        })

    return jsonify({
        "success": True,
        "platforms": platform_list
    })


@app.route('/api/products', methods=['GET'])
def list_product_types():
    """
    Get list of available product types

    Query params:
        popular: If true, only return popular products
        category: Filter by category (apparel, home_living, accessories, stationery)

    Returns:
        JSON response with available product types
    """
    try:
        # Check for filters
        popular_only = request.args.get('popular', '').lower() == 'true'
        category_filter = request.args.get('category', '').lower()

        if popular_only:
            products = get_popular_products()
        elif category_filter:
            try:
                category = ProductCategory(category_filter)
                products = get_products_by_category(category)
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": f"Invalid category. Valid categories: {', '.join(c.value for c in ProductCategory)}"
                }), 400
        else:
            products = list(get_all_products().values())

        # Convert to JSON-friendly format
        product_list = []
        for product in products:
            product_list.append({
                "id": product.id,
                "name": product.name,
                "category": product.category.value,
                "description": product.description,
                "default_price_cents": product.default_price_cents,
                "min_resolution": product.min_resolution,
                "recommended_resolution": product.recommended_resolution
            })

        return jsonify({
            "success": True,
            "products": product_list,
            "count": len(product_list)
        })

    except Exception as e:
        logger.error(f"Error listing product types: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Internal server error"}), 500


@app.route('/api/publish/<image_id>', methods=['POST'])
def publish_image(image_id):
    """
    Publish approved image to selected POD platform

    Args:
        image_id: Image identifier

    Request body:
        {
            "platform": "printify|zazzle|redbubble",
            "title": "Product title",
            "description": "Product description",
            "price_cents": 1999
        }

    Returns:
        JSON response with product ID or error
    """
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

    # Get and validate request data
    try:
        request_data = request.get_json() or {}
    except Exception as e:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400

    # Get platform selection (default to printify for backwards compatibility)
    platform_name = request_data.get("platform", "printify").lower()

    # Validate platform exists and is configured
    if platform_name not in platforms:
        available = ', '.join(platforms.keys()) if platforms else 'none'
        return jsonify({
            "success": False,
            "error": f"Platform '{platform_name}' not available. Configured platforms: {available}"
        }), 400

    platform = platforms[platform_name]
    if not platform.is_configured():
        return jsonify({
            "success": False,
            "error": f"{platform_name} not properly configured"
        }), 400

    # Get image metadata (including prompt info)
    img_state = state_manager.state.get(image_id, {})
    metadata = img_state.get("metadata", {})

    # Auto-generate title from prompt if not provided
    title = request_data.get("title")
    if not title:
        # Try to generate from stored prompt
        original_prompt = metadata.get("original_prompt", "")
        style = metadata.get("style", "")
        genre = metadata.get("genre", "")

        if original_prompt:
            title = generate_product_title(original_prompt, style, genre)
            logger.info(f"Auto-generated title: {title}")
        else:
            title = f"Design {image_id[:8]}"

    is_valid, error = validate_title(title)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    # Auto-generate description if not provided
    description = request_data.get("description")
    if not description and metadata.get("original_prompt"):
        description = f"Unique {metadata.get('style', 'artistic')} design featuring {metadata.get('original_prompt')}. Perfect for print-on-demand products."

    # Generate tags from prompt for SEO
    tags = []
    if metadata.get("original_prompt"):
        # Extract keywords as tags
        words = metadata["original_prompt"].split()
        stop_words = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from'}
        tags = [w.lower() for w in words if w.lower() not in stop_words and len(w) > 3][:10]

    if metadata.get("style"):
        tags.append(metadata["style"].lower())
    if metadata.get("genre"):
        tags.append(metadata["genre"].lower())

    # Add POD-specific tags
    tags.extend(["pod", "print-on-demand", "custom-design", "ai-generated"])

    # Update status to publishing
    try:
        state_manager.set_image_status(image_id, ImageStatus.PUBLISHING.value)
    except StateManagerError as e:
        logger.error(f"Failed to update status to publishing: {e}")
        return jsonify({"success": False, "error": "Failed to update status"}), 500

    # Publish to selected platform
    try:
        # Get product type
        product_type_id = request_data.get("product_type", "hoodie")  # Default to hoodie
        product_type_obj = get_product(product_type_id)

        if product_type_obj:
            # Use product-specific pricing if not provided
            price_cents = request_data.get("price_cents", product_type_obj.default_price_cents)
            logger.info(f"Publishing as {product_type_obj.name} ({product_type_id})")
        else:
            # Fallback to config default
            price_cents = request_data.get("price_cents", config.config.printify.default_price_cents)
            logger.warning(f"Unknown product type '{product_type_id}', using default pricing")

        # Validate price
        if not isinstance(price_cents, int) or price_cents < 0:
            return jsonify({"success": False, "error": "Invalid price"}), 400

        # Call platform publish method with tags and product type
        result = platform.publish(
            image_path=image_path,
            title=title,
            description=description,
            tags=tags,
            price=price_cents,
            product_type=product_type_id  # Pass product type to platform
        )

        if result.success:
            state_manager.set_image_status(image_id, ImageStatus.PUBLISHED.value, {
                "product_id": result.product_id,
                "product_url": result.product_url,
                "platform": result.platform,
                "title": title
            })
            logger.info(f"Image published successfully: {image_id} -> {result.platform} Product {result.product_id}")
            return jsonify({
                "success": True,
                "product_id": result.product_id,
                "product_url": result.product_url,
                "platform": result.platform,
                "status": ImageStatus.PUBLISHED.value
            })
        else:
            error_msg = result.error or f"{platform_name} API failed to create product"
            state_manager.set_image_status(image_id, ImageStatus.FAILED.value, {
                "error_message": error_msg,
                "platform": platform_name
            })
            logger.error(f"Failed to publish image {image_id} to {platform_name}: {error_msg}")
            return jsonify({"success": False, "error": error_msg}), 500

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error publishing image {image_id} to {platform_name}: {e}", exc_info=True)
        try:
            state_manager.set_image_status(image_id, ImageStatus.FAILED.value, {
                "error_message": error_msg,
                "platform": platform_name
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


@app.route('/api/sync_status/<image_id>', methods=['GET'])
def check_sync_status(image_id):
    """
    Check if product has synced to Shopify/Etsy

    Args:
        image_id: Image identifier

    Returns:
        JSON with sync status
    """
    # Validate image ID
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    try:
        # Get product ID from state
        img_state = state_manager.state.get(image_id, {})
        metadata = img_state.get("metadata", {})
        product_id = metadata.get("product_id")

        if not product_id:
            return jsonify({
                "success": False,
                "synced": False,
                "error": "Product not published yet"
            }), 404

        # Check sync status via Printify client
        if printify_client:
            sync_status = printify_client.check_product_sync_status(product_id)
            return jsonify({
                "success": True,
                **sync_status
            })
        else:
            return jsonify({
                "success": False,
                "error": "Printify client not configured"
            }), 400

    except Exception as e:
        logger.error(f"Error checking sync status for {image_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Internal server error"}), 500


@app.route('/api/product_metrics/<image_id>', methods=['GET'])
def get_product_metrics(image_id):
    """
    Get product performance metrics

    Args:
        image_id: Image identifier

    Returns:
        JSON with performance metrics
    """
    # Validate image ID
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    try:
        # Get product data from state
        img_state = state_manager.state.get(image_id, {})
        metadata = img_state.get("metadata", {})

        # Mock metrics (in production, pull from Shopify/Etsy APIs)
        views = metadata.get("views", 0)
        sales = metadata.get("sales", 0)
        favorites = metadata.get("favorites", 0)
        add_to_carts = metadata.get("add_to_carts", 0)

        # Calculate scores
        performance_score = calculate_performance_score(views, favorites, add_to_carts, sales)

        # Get product type for cost calculation
        product_type = metadata.get("product_type", "hoodie")
        price_cents = metadata.get("price_cents", 3499)
        platform = metadata.get("platform", "shopify")

        # Calculate profit
        fulfillment_cost = get_fulfillment_cost(product_type)
        platform_fee_pct = get_platform_fee(platform)
        net_profit = calculate_net_profit(
            price_cents * sales,
            fulfillment_cost * sales,
            platform_fee_pct
        )

        # Check if bestseller
        conversion_rate = sales / views if views > 0 else 0.0
        bestseller = is_bestseller(sales, conversion_rate)

        return jsonify({
            "success": True,
            "image_id": image_id,
            "metrics": {
                "views": views,
                "sales": sales,
                "favorites": favorites,
                "add_to_carts": add_to_carts,
                "conversion_rate": conversion_rate
            },
            "performance": {
                "score": performance_score,
                "bestseller": bestseller
            },
            "financial": {
                "revenue_cents": price_cents * sales,
                "fulfillment_cost_cents": fulfillment_cost * sales,
                "platform_fee_pct": platform_fee_pct,
                "net_profit_cents": net_profit
            }
        })

    except Exception as e:
        logger.error(f"Error getting metrics for {image_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Internal server error"}), 500


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

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


def generate_auto_title(prompt: str, style: str = "", genre: str = "", index: int = 1) -> str:
    """
    Generate automatic title for an image based on prompt.

    Args:
        prompt: Base prompt text
        style: Optional style descriptor
        genre: Optional genre descriptor
        index: Image index in batch (1-based)

    Returns:
        Generated title string
    """
    # Take first meaningful words from prompt (max 6 words)
    words = prompt.strip().split()[:6]
    title_base = " ".join(words)

    # Capitalize first letter of each word
    title_base = title_base.title()

    # Add style/genre if provided
    descriptors = []
    if style:
        descriptors.append(style.title())
    if genre:
        descriptors.append(genre.title())

    if descriptors:
        title = f"{title_base} - {' '.join(descriptors)}"
    else:
        title = title_base

    # Add batch number if needed
    if index > 1:
        title = f"{title} #{index}"

    # Limit to 100 chars for Printify
    if len(title) > 100:
        title = title[:97] + "..."

    return title


def calculate_auto_price(width: int, height: int, base_price: int = 1999) -> int:
    """
    Calculate automatic price based on image dimensions.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        base_price: Base price in cents (default: $19.99)

    Returns:
        Price in cents
    """
    # Price tiers based on total pixels
    total_pixels = width * height
    megapixels = total_pixels / 1_000_000

    if megapixels >= 8:  # 3300x4200 = 13.86 MP (11x14" print)
        return 2999  # $29.99
    elif megapixels >= 6:  # 2400x3000 = 7.2 MP (8x10" print)
        return 2499  # $24.99
    elif megapixels >= 4:  # 2048x2048 = 4.19 MP (square 2K)
        return 1999  # $19.99
    else:  # 1024x1024 = 1.05 MP (square 1K)
        return 1499  # $14.99


def generate_ai_description(prompt: str, title: str, style: str = "", genre: str = "") -> str:
    """
    Generate AI-powered product description for Printify.

    Args:
        prompt: Original image generation prompt
        title: Generated title
        style: Style descriptor
        genre: Genre descriptor

    Returns:
        Marketing-friendly product description
    """
    # Build context
    context_parts = [prompt]
    if style:
        context_parts.append(f"in {style} style")
    if genre:
        context_parts.append(f"of {genre} genre")

    context = " ".join(context_parts)

    # Generate a compelling marketing description
    # Using template-based generation for speed (can be replaced with LLM API call)
    description = f"""Transform your space with this stunning "{title}" design.

🎨 Created from the vision: {context}

Perfect for:
• Home decor and wall art
• Unique gifts that make an impression
• Personal expression and style
• Adding character to any room

✨ High-quality print on premium materials
🎯 Professional-grade image resolution
💯 Satisfaction guaranteed

This exclusive design captures {'the essence of ' + genre if genre else 'unique artistic expression'} with {'beautiful ' + style + ' styling' if style else 'exceptional attention to detail'}.

Make it yours today and elevate your space with art that speaks to you."""

    return description[:1000]  # Printify limit


def build_comfyui_workflow(
    prompt: str,
    seed: int | None = None,
    width: int = 2048,
    height: int = 2048,
    steps: int = 40,
    cfg_scale: float = 1.5,
    negative_prompt: str = "",
    sampler_name: str = "euler",
    scheduler: str = "simple",
    batch_size: int = 1
) -> Dict[str, Any]:
    """
    Build an optimized Flux Dev FP8 workflow for high-quality, print-ready images.

    Optimized for Flux Dev FP8:
    - CFG Scale: 1.0-2.0 (Flux works best with low guidance)
    - Scheduler: "simple" (best for Flux models)
    - Steps: 40 (FP8 quantized models need more steps than full precision)
    - Batch Size: 1-25 images per generation

    Default: 2048x2048 at 40 steps for sharp, detailed prints.
    For 8x10" print at 300 DPI, use 2400x3000.
    For 11x14" print at 300 DPI, use 3300x4200.
    """
    if seed is None:
        seed = int.from_bytes(os.urandom(4), byteorder="little")

    # Clamp batch size to valid range
    batch_size = max(1, min(25, batch_size))

    # Enhance prompt with quality tags for sharper, more detailed output
    quality_tags = "masterpiece, best quality, high resolution, extremely detailed, sharp focus, professional photography, 8k uhd"
    enhanced_prompt = f"{prompt}, {quality_tags}"

    # Default negative prompt for print quality
    if not negative_prompt:
        negative_prompt = "blurry, out of focus, low quality, worst quality, low res, jpeg artifacts, compression, noise, grainy, pixelated, watermark, text, signature, bad anatomy"

    return {
        "3": {
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg_scale,
                "sampler_name": sampler_name,
                "scheduler": scheduler,
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
                "batch_size": batch_size
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": enhanced_prompt,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": negative_prompt,
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


def extract_runpod_images(
    output: Dict[str, Any],
    prompt: str = "",
    style: str = "",
    genre: str = "",
    width: int = 2048,
    height: int = 2048
) -> List[str]:
    """
    Extract and save images from RunPod serverless output with auto-titling and pricing.

    RunPod output format can be:
    - {"images": [{"image": "base64_data", ...}]}
    - {"output": {"images": [...]}}
    - Direct base64 image data

    Args:
        output: RunPod output dict
        prompt: Base prompt for title generation
        style: Style for title generation
        genre: Genre for title generation
        width: Image width for price calculation
        height: Image height for price calculation

    Returns:
        List of local image paths
    """
    import base64

    saved_images = []

    # Try to find images in various output formats
    images_data = None

    if "images" in output:
        images_data = output["images"]
    elif "output" in output and isinstance(output["output"], dict):
        if "images" in output["output"]:
            images_data = output["output"]["images"]

    if not images_data:
        logger.warning(f"⚠️ No recognized image format in RunPod output. Keys: {list(output.keys())}")
        return []

    # Process each image
    for idx, img_data in enumerate(images_data):
        try:
            # Extract base64 data
            base64_str = None

            if isinstance(img_data, dict):
                # Try common keys for base64 data
                base64_str = img_data.get("image") or img_data.get("data") or img_data.get("base64")
            elif isinstance(img_data, str):
                # Direct base64 string
                base64_str = img_data

            if not base64_str:
                logger.warning(f"Could not extract base64 data from image {idx}")
                continue

            # Remove data URL prefix if present
            if "base64," in base64_str:
                base64_str = base64_str.split("base64,")[1]

            # Decode base64
            image_bytes = base64.b64decode(base64_str)

            # Generate unique filename
            image_id = f"runpod_{uuid.uuid4().hex[:12]}"
            filename = f"{image_id}.png"
            output_path = Path(config.IMAGE_DIR) / filename

            # Save image
            output_path.write_bytes(image_bytes)
            logger.info(f"✓ Saved RunPod image: {filename}")

            # Register in state manager
            try:
                state_manager.add_image(image_id, filename, str(output_path))

                # Generate and store title, price, and description
                title = generate_auto_title(prompt, style, genre, idx + 1)
                price_cents = calculate_auto_price(width, height)
                description = generate_ai_description(prompt, title, style, genre)

                state_manager.set_image_status(
                    image_id,
                    ImageStatus.PENDING.value,
                    metadata={
                        "title": title,
                        "price_cents": price_cents,
                        "description": description,
                        "prompt": prompt,
                        "style": style,
                        "genre": genre,
                        "width": width,
                        "height": height
                    }
                )
                logger.info(f"   Title: {title}")
                logger.info(f"   Price: ${price_cents/100:.2f}")
                logger.info(f"   Description: {description[:50]}...")

            except StateManagerError as e:
                logger.warning(f"Failed to set metadata for {image_id}: {e}")

            saved_images.append(str(output_path))

        except Exception as e:
            logger.error(f"Failed to process RunPod image {idx}: {e}")
            continue

    if not saved_images:
        logger.error("❌ No images could be extracted from RunPod output!")

    return saved_images


@app.route('/')
def index():
    """Gallery UI"""
    return render_template('gallery.html')


@app.route('/api/version')
def version():
    """Check version - has bulk actions and 50+ features"""
    return jsonify({
        "version": "2.0.0-mega-upgrade",
        "features": [
            "bulk_actions", "ai_descriptions", "search", "export",
            "statistics", "keyboard_shortcuts", "batch_generation"
        ],
        "api_endpoints": {
            "bulk": ["/api/bulk/approve", "/api/bulk/reject", "/api/bulk/delete"],
            "search": "/api/search",
            "export": "/api/export",
            "stats": "/api/statistics/detailed"
        }
    })


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


@app.route('/api/generate', methods=['POST'])
def generate_image():
    """
    Submit a prompt to ComfyUI via the configured API URL.

    Expected JSON body:
    {
        "prompt": "Base prompt text",
        "style": "Optional style",
        "genre": "Optional genre",
        "width": 2048,
        "height": 2048,
        "steps": 40,
        "cfg_scale": 1.5,
        "negative_prompt": "Optional negative prompt",
        "sampler": "euler",
        "scheduler": "simple",
        "batch_size": 1
    }

    Optimized defaults for Flux Dev FP8:
    - steps: 40 (FP8 quantized models need more steps)
    - cfg_scale: 1.5 (Flux works best with 1.0-2.0)
    - scheduler: "simple" (best for Flux)
    - batch_size: 1-25 images per generation
    """
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    style = (data.get("style") or "").strip()
    genre = (data.get("genre") or "").strip()
    negative_prompt = (data.get("negative_prompt") or "").strip()

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Get and validate parameters
    width = data.get("width", 2048)
    height = data.get("height", 2048)
    batch_size = max(1, min(25, data.get("batch_size", 1)))

    full_prompt = build_prompt_text(prompt, style, genre)
    logger.info(f"Using {'RunPod Serverless' if comfyui_client else 'direct ComfyUI'} for generation: {prompt[:50]}... (batch: {batch_size})")

    workflow = build_comfyui_workflow(
        full_prompt,
        seed=data.get("seed"),
        width=width,
        height=height,
        steps=data.get("steps", 40),
        cfg_scale=data.get("cfg_scale", 1.5),
        negative_prompt=negative_prompt,
        sampler_name=data.get("sampler", "euler"),
        scheduler=data.get("scheduler", "simple"),
        batch_size=batch_size
    )

    client_id = data.get("client_id") or f"pod-gateway-{uuid.uuid4().hex[:8]}"

    try:
        # Use RunPod serverless client if available, otherwise direct ComfyUI
        if comfyui_client:
            # RunPod serverless - submit and poll for completion
            logger.info(f"Submitting to RunPod serverless (timeout: 300s)")
            result = comfyui_client.submit_workflow(
                workflow,
                client_id,
                timeout=300,  # 5 minutes for Flux model generation
                poll_for_completion=True
            )

            status = result.get("status")
            job_id = result.get("job_id")

            # Handle different statuses
            if status == "COMPLETED":
                # Extract and save images
                output = result.get("output", {})
                logger.info(f"Job completed, extracting images from output")
                logger.debug(f"Full RunPod output: {output}")

                saved_images = extract_runpod_images(
                    output,
                    prompt=prompt,
                    style=style,
                    genre=genre,
                    width=width,
                    height=height
                )

                if saved_images:
                    logger.info(f"✓ Generated {len(saved_images)} image(s)")
                    return jsonify({
                        "prompt_id": result.get("prompt_id"),
                        "job_id": job_id,
                        "status": "COMPLETED",
                        "prompt": full_prompt,
                        "images": [Path(img).name for img in saved_images],
                        "image_count": len(saved_images)
                    })
                else:
                    logger.warning("Job completed but no images extracted")
                    return jsonify({
                        "prompt_id": result.get("prompt_id"),
                        "job_id": job_id,
                        "status": "COMPLETED",
                        "prompt": full_prompt,
                        "warning": "No images were extracted from output"
                    })

            elif status == "TIMEOUT":
                # Job timed out
                logger.warning(f"Job {job_id} timed out")
                return jsonify({
                    "prompt_id": result.get("prompt_id"),
                    "job_id": job_id,
                    "status": "TIMEOUT",
                    "prompt": full_prompt,
                    "error": result.get("error", "Job timed out")
                }), 408

            else:
                # Other status (IN_QUEUE, IN_PROGRESS, etc.)
                return jsonify({
                    "prompt_id": result.get("prompt_id"),
                    "job_id": job_id,
                    "status": status,
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
        logger.error("Unexpected error: %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 502


@app.route('/api/generation_status')
def generation_status():
    """
    Proxy generation status from ComfyUI history endpoint.

    For RunPod serverless: Jobs complete synchronously in /api/generate,
    so we return a completed status to stop frontend polling.
    """
    prompt_id = request.args.get("prompt_id")
    if not prompt_id:
        return jsonify({"error": "prompt_id is required"}), 400

    # If using RunPod serverless, jobs complete in /api/generate
    # Return completed status to stop frontend polling
    if comfyui_client:
        logger.debug(f"RunPod serverless mode: returning completed status for {prompt_id}")
        return jsonify({
            "history": {
                prompt_id: {
                    "status": {
                        "completed": True,
                        "status_str": "success"
                    }
                }
            },
            "downloaded": []
        })

    # Direct ComfyUI mode - query history endpoint
    try:
        response = requests.get(
            f"{config.COMFYUI_API_URL}/history/{prompt_id}",
            timeout=30
        )
    except requests.RequestException as exc:
        logger.error("ComfyUI status request failed: %s", exc)
        return jsonify({"error": "Failed to connect to ComfyUI"}), 502

    # Handle 404 gracefully - job might have expired
    if response.status_code == 404:
        logger.warning(f"Job {prompt_id} not found in ComfyUI history (may have expired)")
        return jsonify({
            "history": {
                prompt_id: {
                    "status": {
                        "completed": True,
                        "status_str": "success"
                    }
                }
            },
            "downloaded": []
        })

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

    # Get stored metadata (title and price)
    metadata = state_manager.get_image_metadata(image_id)

    # Use request title/price if provided, otherwise fall back to stored values
    title = request_data.get("title") or (getattr(metadata, "title", None) if metadata else None) or f"Design {image_id[:8]}"
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
        # Use request description if provided, otherwise stored description, otherwise use title
        description = request_data.get("description") or (getattr(metadata, "description", None) if metadata else None) or title

        # Use request price if provided, otherwise stored price, otherwise default
        if request_data.get("price_cents"):
            price_cents = request_data.get("price_cents")
        elif metadata and getattr(metadata, "price_cents", None):
            price_cents = metadata.price_cents
        else:
            price_cents = config.config.printify.default_price_cents
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


# =================================================================
# BULK ACTIONS API - Process multiple images at once
# =================================================================

@app.route('/api/bulk/approve', methods=['POST'])
def bulk_approve():
    """Bulk approve multiple images"""
    data = request.get_json() or {}
    image_ids = data.get("image_ids", [])

    if not image_ids or not isinstance(image_ids, list):
        return jsonify({"success": False, "error": "Invalid image_ids"}), 400

    results = {"success": [], "failed": []}
    for image_id in image_ids:
        try:
            state_manager.set_image_status(image_id, ImageStatus.APPROVED.value)
            results["success"].append(image_id)
        except Exception as e:
            results["failed"].append({"id": image_id, "error": str(e)})

    return jsonify({
        "success": True,
        "approved": len(results["success"]),
        "failed": len(results["failed"]),
        "results": results
    })


@app.route('/api/bulk/reject', methods=['POST'])
def bulk_reject():
    """Bulk reject multiple images"""
    data = request.get_json() or {}
    image_ids = data.get("image_ids", [])

    if not image_ids or not isinstance(image_ids, list):
        return jsonify({"success": False, "error": "Invalid image_ids"}), 400

    results = {"success": [], "failed": []}
    for image_id in image_ids:
        try:
            state_manager.set_image_status(image_id, ImageStatus.REJECTED.value)
            results["success"].append(image_id)
        except Exception as e:
            results["failed"].append({"id": image_id, "error": str(e)})

    return jsonify({
        "success": True,
        "rejected": len(results["success"]),
        "failed": len(results["failed"]),
        "results": results
    })


@app.route('/api/bulk/delete', methods=['POST'])
def bulk_delete():
    """Bulk delete multiple images"""
    data = request.get_json() or {}
    image_ids = data.get("image_ids", [])

    if not image_ids or not isinstance(image_ids, list):
        return jsonify({"success": False, "error": "Invalid image_ids"}), 400

    results = {"success": [], "failed": []}
    for image_id in image_ids:
        try:
            # Delete from state
            state_manager.delete_image(image_id)

            # Delete file
            image_path = os.path.join(config.IMAGE_DIR, f"{image_id}.png")
            if os.path.exists(image_path):
                os.remove(image_path)

            results["success"].append(image_id)
        except Exception as e:
            results["failed"].append({"id": image_id, "error": str(e)})

    return jsonify({
        "success": True,
        "deleted": len(results["success"]),
        "failed": len(results["failed"]),
        "results": results
    })


# =================================================================
# SEARCH & FILTER API
# =================================================================

@app.route('/api/search', methods=['GET'])
def search_images():
    """Search images by prompt, title, or metadata"""
    query = request.args.get("q", "").lower()
    status_filter = request.args.get("status")

    if not query:
        return jsonify({"images": []})

    all_images = state_manager.get_all_images()
    results = []

    for img_id, data in all_images.items():
        # Filter by status if specified
        if status_filter and data.get("status") != status_filter:
            continue

        # Search in multiple fields
        searchable_text = " ".join([
            data.get("title", ""),
            data.get("prompt", ""),
            data.get("description", ""),
            data.get("filename", ""),
            data.get("style", ""),
            data.get("genre", "")
        ]).lower()

        if query in searchable_text:
            results.append({
                "id": img_id,
                "filename": data.get("filename"),
                "title": data.get("title"),
                "prompt": data.get("prompt"),
                "status": data.get("status"),
                "price_cents": data.get("price_cents"),
                "created_at": data.get("created_at")
            })

    return jsonify({"images": results, "count": len(results)})


# =================================================================
# IMAGE OPERATIONS API - Regenerate, duplicate, export
# =================================================================

@app.route('/api/regenerate/<image_id>', methods=['POST'])
def regenerate_image(image_id):
    """Regenerate image with same parameters but new seed"""
    metadata = state_manager.get_image_metadata(image_id)

    if not metadata:
        return jsonify({"success": False, "error": "Image not found"}), 404

    # Extract generation parameters
    prompt = getattr(metadata, "prompt", None)
    style = getattr(metadata, "style", None) or ""
    genre = getattr(metadata, "genre", None) or ""
    width = getattr(metadata, "width", None) or 2048
    height = getattr(metadata, "height", None) or 2048

    if not prompt:
        return jsonify({"success": False, "error": "No prompt found in metadata"}), 400

    # Trigger new generation
    return jsonify({
        "success": True,
        "message": "Use /api/generate with these parameters",
        "parameters": {
            "prompt": prompt,
            "style": style,
            "genre": genre,
            "width": width,
            "height": height
        }
    })


@app.route('/api/export', methods=['GET'])
def export_metadata():
    """Export all image metadata as JSON"""
    format_type = request.args.get("format", "json")

    all_images = state_manager.get_all_images()

    if format_type == "csv":
        # Generate CSV
        import csv
        import io

        output = io.StringIO()
        if all_images:
            fieldnames = list(next(iter(all_images.values())).keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for img_id, data in all_images.items():
                row = {"id": img_id, **data}
                writer.writerow(row)

        return output.getvalue(), 200, {"Content-Type": "text/csv", "Content-Disposition": "attachment; filename=images.csv"}
    else:
        # Return JSON
        return jsonify({"images": all_images, "count": len(all_images)})


# =================================================================
# ADVANCED STATISTICS API
# =================================================================

@app.route('/api/statistics/detailed', methods=['GET'])
def detailed_statistics():
    """Get detailed statistics about images"""
    all_images = state_manager.get_all_images()

    # Calculate stats
    total = len(all_images)
    by_status = {}
    by_style = {}
    by_genre = {}
    total_value = 0
    resolution_distribution = {"1K": 0, "2K": 0, "8x10": 0, "11x14": 0, "other": 0}

    for img_id, data in all_images.items():
        # Status distribution
        status = data.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1

        # Style distribution
        style = data.get("style", "none")
        by_style[style] = by_style.get(style, 0) + 1

        # Genre distribution
        genre = data.get("genre", "none")
        by_genre[genre] = by_genre.get(genre, 0) + 1

        # Total value
        price = data.get("price_cents", 0)
        if price:
            total_value += price

        # Resolution distribution
        width = data.get("width", 0)
        height = data.get("height", 0)
        if width and height:
            megapixels = (width * height) / 1_000_000
            if megapixels >= 8:
                resolution_distribution["11x14"] += 1
            elif megapixels >= 6:
                resolution_distribution["8x10"] += 1
            elif megapixels >= 3:
                resolution_distribution["2K"] += 1
            elif megapixels >= 1:
                resolution_distribution["1K"] += 1
            else:
                resolution_distribution["other"] += 1

    return jsonify({
        "total_images": total,
        "by_status": by_status,
        "by_style": by_style,
        "by_genre": by_genre,
        "total_value_cents": total_value,
        "total_value_usd": f"${total_value/100:.2f}",
        "resolution_distribution": resolution_distribution
    })


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

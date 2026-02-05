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
import io

# Try to import rembg for background removal
try:
    from rembg import remove as remove_bg
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False

# Load environment from project root first (contains API keys)
project_root = Path(__file__).parent.parent.parent
root_env = project_root / ".env"
if root_env.exists():
    load_dotenv(root_env)
# Also load from current dir but don't override existing values
load_dotenv(override=False)

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


# POD-optimized style presets for t-shirt/merch designs
POD_STYLE_PRESETS = {
    "vintage": "vintage retro distressed aesthetic, worn texture, faded colors, nostalgic feel",
    "minimalist": "minimalist clean design, simple shapes, limited color palette, modern aesthetic",
    "bold": "bold graphic design, high contrast, striking colors, eye-catching composition",
    "retro": "retro 80s 90s style, neon colors, geometric shapes, synthwave aesthetic",
    "grunge": "grunge textured design, rough edges, distressed look, urban street style",
    "watercolor": "watercolor artistic style, soft blended colors, painterly effect, artistic",
    "line-art": "clean line art illustration, minimal lines, elegant strokes, vector style",
    "pop-art": "pop art style, bold outlines, halftone dots, vibrant comic book aesthetic",
    "gothic": "gothic dark aesthetic, ornate details, dramatic shadows, mysterious mood",
    "kawaii": "kawaii cute style, pastel colors, adorable characters, Japanese aesthetic",
    "streetwear": "streetwear urban design, hip hop culture, bold typography, street art",
    "nature": "nature inspired design, organic shapes, earthy tones, botanical elements",
    "geometric": "geometric abstract design, clean shapes, mathematical patterns, modern",
    "typography": "typography focused design, creative lettering, artistic text arrangement",
    "illustrative": "detailed illustration style, artistic rendering, professional artwork"
}

# POD quality enhancement suffixes
POD_QUALITY_SUFFIX = "high quality design suitable for print on demand, clean edges, transparent background friendly, centered composition, professional artwork"

# ============================================================================
# AUTO-PROMPTING SYSTEM FOR POD
# ============================================================================

import random

# POD Niche subjects - popular categories for merchandise
POD_SUBJECTS = {
    "animals": [
        "majestic wolf howling at the moon",
        "fierce lion with a crown",
        "cute cat with sunglasses",
        "wise owl in a forest",
        "playful dog with a bandana",
        "mythical phoenix rising from flames",
        "elegant horse running free",
        "adorable panda eating bamboo",
        "powerful eagle soaring",
        "mystical dragon breathing fire",
        "lazy sloth hanging from a branch",
        "curious fox in autumn leaves",
        "graceful deer in moonlight",
        "tropical parrot with vibrant colors",
        "underwater octopus with tentacles"
    ],
    "nature": [
        "mountain landscape at sunset",
        "ocean waves crashing on rocks",
        "peaceful forest with sunbeams",
        "desert cactus under starry sky",
        "cherry blossom tree in spring",
        "northern lights aurora borealis",
        "tropical beach with palm trees",
        "misty waterfall in jungle",
        "autumn leaves falling",
        "snowy mountain peak",
        "wildflower meadow at golden hour",
        "lightning storm over canyon",
        "rainbow over green hills",
        "coral reef underwater scene",
        "full moon rising over lake"
    ],
    "typography": [
        "Stay Wild",
        "Good Vibes Only",
        "Dream Big",
        "Be Kind",
        "Adventure Awaits",
        "Stay Humble Hustle Hard",
        "Live Laugh Love",
        "No Bad Days",
        "Coffee First",
        "Weekend Warrior",
        "Stay Positive",
        "Born to be Wild",
        "Choose Joy",
        "Never Give Up",
        "Make It Happen"
    ],
    "motivational": [
        "silhouette of person on mountain top achieving goals",
        "compass pointing north with adventure theme",
        "rising sun symbolizing new beginnings",
        "butterfly transformation metamorphosis",
        "rocket launching into space dreams",
        "tree growing from small seed",
        "lighthouse guiding through storm",
        "arrow breaking through barriers",
        "phoenix rising symbolizing rebirth",
        "lion representing courage and strength"
    ],
    "fantasy": [
        "magical wizard casting spell",
        "fairy in enchanted garden",
        "unicorn in mystical forest",
        "knight fighting dragon",
        "mermaid under the sea",
        "mystical crystal cave",
        "floating castle in clouds",
        "ancient tree of life",
        "magical potion bottles",
        "enchanted sword with runes"
    ],
    "space": [
        "astronaut floating in space",
        "galaxy spiral with stars",
        "planets aligned in solar system",
        "rocket ship exploring cosmos",
        "alien landscape with two moons",
        "nebula clouds colorful cosmic",
        "black hole with light bending",
        "space station orbiting earth",
        "meteor shower across night sky",
        "astronaut on moon surface"
    ],
    "retro": [
        "vintage car on sunset highway",
        "old school boombox with cassettes",
        "retro arcade game machine",
        "vinyl record player spinning",
        "80s roller skating disco",
        "vintage television with antenna",
        "classic motorcycle chopper",
        "retro diner with neon signs",
        "old camera with film roll",
        "vintage surfboard on beach"
    ],
    "skulls": [
        "sugar skull dia de los muertos",
        "floral skull with roses",
        "geometric skull modern art",
        "pirate skull with crossbones",
        "neon skull cyberpunk style",
        "skull with crown royal",
        "skull made of flowers",
        "viking skull with helmet",
        "crystal skull mystical",
        "skull with butterfly transformation"
    ],
    "sports": [
        "basketball player slam dunk silhouette",
        "soccer ball on fire",
        "surfing big wave action",
        "skateboard tricks aerial",
        "mountain bike extreme downhill",
        "boxing gloves crossed",
        "golf ball on tee sunrise",
        "tennis racket smashing ball",
        "swimming freestyle motion",
        "yoga pose meditation silhouette"
    ],
    "food": [
        "pizza slice dripping cheese",
        "coffee cup with steam heart",
        "sushi roll arrangement",
        "ice cream cone melting",
        "burger stacked tall",
        "donut with colorful sprinkles",
        "tacos with all toppings",
        "avocado toast trendy",
        "ramen bowl steaming",
        "cocktail with umbrella tropical"
    ],
    "music": [
        "electric guitar with lightning",
        "headphones with sound waves",
        "piano keys abstract art",
        "microphone with music notes",
        "drums set explosive",
        "vinyl DJ turntable spinning",
        "saxophone with jazz notes",
        "rock hand sign devil horns",
        "music equalizer bars",
        "concert crowd silhouette"
    ],
    "gaming": [
        "retro game controller pixel art",
        "gaming headset with RGB lights",
        "dice rolling tabletop",
        "chess pieces strategic",
        "poker cards royal flush",
        "arcade joystick classic",
        "gaming mouse and keyboard",
        "virtual reality headset",
        "level up text gaming",
        "respawn gaming text"
    ],
    "holidays": [
        "Christmas tree with ornaments",
        "Halloween pumpkin jack o lantern",
        "Easter bunny with eggs",
        "Thanksgiving turkey feast",
        "Valentine hearts and roses",
        "St Patrick shamrock lucky",
        "Fourth of July fireworks",
        "New Year countdown celebration",
        "Hanukkah menorah candles",
        "Day of the Dead calavera"
    ],
    "professions": [
        "nurse healthcare hero",
        "firefighter in action",
        "teacher inspiring minds",
        "chef cooking flames",
        "mechanic with tools",
        "programmer coding matrix",
        "doctor medical symbol",
        "police officer badge",
        "pilot aviator wings",
        "scientist laboratory"
    ]
}

# Style modifiers for variety
POD_STYLE_MODIFIERS = [
    "detailed illustration",
    "minimalist design",
    "watercolor painting",
    "vector art style",
    "vintage retro look",
    "neon glow effect",
    "hand drawn sketch",
    "geometric shapes",
    "graffiti street art",
    "psychedelic colors",
    "line art outline",
    "silhouette design",
    "comic book style",
    "abstract artistic",
    "realistic detailed"
]

# Color schemes
POD_COLOR_SCHEMES = [
    "vibrant rainbow colors",
    "black and white monochrome",
    "pastel soft colors",
    "neon bright colors",
    "earth tones natural",
    "sunset orange and purple",
    "ocean blue and teal",
    "forest green shades",
    "warm autumn colors",
    "cool winter blues",
    "gold and black luxury",
    "pink and purple gradient",
    "red and black bold",
    "tropical bright colors",
    "muted vintage palette"
]

# Seasonal themes
POD_SEASONAL = {
    "spring": ["blooming flowers", "butterflies", "rain showers", "baby animals", "fresh green"],
    "summer": ["beach vibes", "tropical", "sunshine", "vacation", "pool party"],
    "fall": ["autumn leaves", "pumpkin spice", "harvest", "cozy sweater", "halloween"],
    "winter": ["snowflakes", "cozy fireplace", "holiday spirit", "skiing", "hot cocoa"]
}

# Trending niches
POD_TRENDING = [
    "cottagecore aesthetic",
    "dark academia",
    "Y2K nostalgia",
    "goblincore nature",
    "vaporwave aesthetic",
    "witchy vibes",
    "plant parent",
    "book lover",
    "true crime obsessed",
    "astrology zodiac",
    "mental health awareness",
    "LGBTQ pride",
    "introvert life",
    "dog mom dog dad",
    "cat lover crazy"
]


def generate_auto_prompt(
    niche: str = None,
    style: str = None,
    color_scheme: str = None,
    season: str = None,
    trending: bool = False,
    count: int = 1
) -> list:
    """
    Generate automatic POD prompts based on parameters.

    Args:
        niche: Specific niche category (animals, nature, typography, etc.)
        style: Style modifier to apply
        color_scheme: Color scheme to use
        season: Seasonal theme (spring, summer, fall, winter)
        trending: Whether to include trending themes
        count: Number of prompts to generate

    Returns:
        List of generated prompts
    """
    prompts = []

    for _ in range(count):
        parts = []

        # Select subject based on niche or random
        if niche and niche.lower() in POD_SUBJECTS:
            subject = random.choice(POD_SUBJECTS[niche.lower()])
        else:
            # Random niche
            random_niche = random.choice(list(POD_SUBJECTS.keys()))
            subject = random.choice(POD_SUBJECTS[random_niche])

        parts.append(subject)

        # Add style modifier
        if style:
            parts.append(style)
        else:
            parts.append(random.choice(POD_STYLE_MODIFIERS))

        # Add color scheme
        if color_scheme:
            parts.append(color_scheme)
        else:
            # 50% chance to add color scheme
            if random.random() > 0.5:
                parts.append(random.choice(POD_COLOR_SCHEMES))

        # Add seasonal theme
        if season and season.lower() in POD_SEASONAL:
            seasonal_modifier = random.choice(POD_SEASONAL[season.lower()])
            parts.append(seasonal_modifier)

        # Add trending theme
        if trending:
            trend = random.choice(POD_TRENDING)
            parts.append(trend)

        prompt = ", ".join(parts)
        prompts.append(prompt)

    return prompts


def expand_prompt(base_prompt: str, variations: int = 5) -> list:
    """
    Expand a base prompt into multiple variations.

    Args:
        base_prompt: The base prompt to expand
        variations: Number of variations to generate

    Returns:
        List of prompt variations
    """
    expanded = []

    for _ in range(variations):
        parts = [base_prompt]

        # Add random style
        parts.append(random.choice(POD_STYLE_MODIFIERS))

        # Add random color scheme (50% chance)
        if random.random() > 0.5:
            parts.append(random.choice(POD_COLOR_SCHEMES))

        # Add random preset style (30% chance)
        if random.random() > 0.7:
            preset_name = random.choice(list(POD_STYLE_PRESETS.keys()))
            parts.append(POD_STYLE_PRESETS[preset_name])

        expanded.append(", ".join(parts))

    return expanded


def build_prompt_text(
    prompt: str,
    style: str = "",
    genre: str = "",
    preset: str = "",
    enhance_for_pod: bool = True,
    custom_suffix: str = ""
) -> str:
    """
    Build the full prompt text with optional style, genre, and POD enhancements.

    Args:
        prompt: Base prompt text
        style: Optional style descriptor (free text)
        genre: Optional genre descriptor
        preset: Optional preset name from POD_STYLE_PRESETS
        enhance_for_pod: Whether to add POD quality enhancement suffix
        custom_suffix: Optional custom suffix to append
    """
    parts = [prompt.strip()]

    # Add preset style if specified
    if preset and preset.lower() in POD_STYLE_PRESETS:
        parts.append(POD_STYLE_PRESETS[preset.lower()])
    elif style:
        parts.append(f"{style} style")

    if genre:
        parts.append(f"{genre} genre")

    if custom_suffix:
        parts.append(custom_suffix.strip())

    # Add POD quality enhancement
    if enhance_for_pod:
        parts.append(POD_QUALITY_SUFFIX)

    return ", ".join(part for part in parts if part)


def build_comfyui_workflow(
    prompt: str,
    seed: int | None = None,
    width: int = 1024,
    height: int = 1024,
    steps: int = 30,
    cfg_scale: float = 1.0,
    upscale: bool = True
) -> Dict[str, Any]:
    """Build a Flux workflow for ComfyUI optimized for POD quality.

    Args:
        prompt: The text prompt for image generation
        seed: Random seed (auto-generated if None)
        width: Base image width (default 1024)
        height: Base image height (default 1024)
        steps: Number of sampling steps (default 30 for Flux quality)
        cfg_scale: Classifier-free guidance scale (default 1.0 for Flux)
        upscale: Whether to 4x upscale for POD quality (default True)

    Returns:
        ComfyUI workflow dict. Output will be 4096x4096 if upscale=True.
    """
    if seed is None:
        seed = int.from_bytes(os.urandom(4), byteorder="little")

    # Flux-optimized workflow
    workflow = {
        "3": {
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg_scale,
                "sampler_name": "euler",
                "scheduler": "normal",
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
                "text": "",
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
        }
    }

    if upscale:
        # 4x upscale using built-in ImageScale (no extra models needed)
        # 1024x1024 -> 4096x4096 for POD quality
        workflow["10"] = {
            "inputs": {
                "upscale_method": "lanczos",
                "width": width * 4,
                "height": height * 4,
                "crop": "disabled",
                "image": ["8", 0]
            },
            "class_type": "ImageScale"
        }
        # Save upscaled image
        workflow["9"] = {
            "inputs": {
                "filename_prefix": "ComfyUI",
                "images": ["10", 0]
            },
            "class_type": "SaveImage"
        }
    else:
        # Save original resolution
        workflow["9"] = {
            "inputs": {
                "filename_prefix": "ComfyUI",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }

    return workflow


def download_and_save_image(image_data: str, filename: str | None = None, prompt: str = "") -> Tuple[str, str] | None:
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

        state_manager.add_image(image_id, filename, str(file_path), prompt=prompt)
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


def save_runpod_output_images(output: Dict[str, Any], prompt: str = "") -> List[Dict[str, str]]:
    """Save any images found in a RunPod output payload."""
    saved_images: List[Dict[str, str]] = []
    logger.info(f"Processing RunPod output keys: {list(output.keys()) if isinstance(output, dict) else type(output)}")
    payloads = extract_image_payloads(output)
    logger.info(f"Found {len(payloads)} image payloads to process")

    for i, payload in enumerate(payloads):
        logger.debug(f"Payload {i}: {list(payload.keys())}")
        image_data = (
            payload.get("url")
            or payload.get("data")
            or payload.get("image")
            or payload.get("base64")
        )
        if image_data:
            logger.info(f"Found image data (type: {'url' if image_data.startswith('http') else 'base64'}, len: {len(image_data)})")
            saved = download_and_save_image(image_data, prompt=prompt)
            if saved:
                image_id, file_path = saved
                logger.info(f"✓ Saved image: {image_id} -> {file_path}")
                saved_images.append({"id": image_id, "path": file_path})
            continue

        if payload.get("filename"):
            local_path = download_comfyui_image(payload)
            if local_path:
                image_id = Path(local_path).stem
                try:
                    state_manager.add_image(image_id, Path(local_path).name, local_path, prompt=prompt)
                except StateManagerError:
                    pass
                saved_images.append({"id": image_id, "path": local_path})

    logger.info(f"Total images saved: {len(saved_images)}")
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
        "style": "Optional style (free text)",
        "genre": "Optional genre",
        "preset": "Optional preset name (vintage, minimalist, bold, etc.)",
        "enhance_for_pod": true/false (default true),
        "custom_suffix": "Optional custom suffix to append"
    }
    """
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    style = (data.get("style") or "").strip()
    genre = (data.get("genre") or "").strip()
    preset = (data.get("preset") or "").strip()
    enhance_for_pod = data.get("enhance_for_pod", True)
    custom_suffix = (data.get("custom_suffix") or "").strip()

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    full_prompt = build_prompt_text(
        prompt, style, genre,
        preset=preset,
        enhance_for_pod=enhance_for_pod,
        custom_suffix=custom_suffix
    )
    logger.info(f"Using {'RunPod Serverless' if comfyui_client else 'direct ComfyUI'} for generation: {prompt[:50]}...")

    workflow = build_comfyui_workflow(
        full_prompt,
        seed=data.get("seed"),
        width=data.get("width", 1024),
        height=data.get("height", 1024),
        steps=data.get("steps", 30),
        cfg_scale=data.get("cfg_scale", 1.0),  # Flux uses CFG=1
        upscale=data.get("upscale", True)  # 4x upscale for POD quality by default
    )

    client_id = data.get("client_id") or f"pod-gateway-{uuid.uuid4().hex[:8]}"

    try:
        # Use RunPod serverless client if available, otherwise direct ComfyUI
        if comfyui_client:
            # RunPod serverless
            result = comfyui_client.submit_workflow(workflow, client_id, timeout=300)  # 5min for upscaling
            saved_images: List[Dict[str, str]] = []
            if result.get("status") == "COMPLETED":
                output = result.get("output", {})
                saved_images = save_runpod_output_images(output, prompt=full_prompt)

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

    # Use prompt as default title if available, otherwise fallback to image ID
    all_images = state_manager.get_all_images()
    image_state = all_images.get(image_id, {})
    prompt_title = image_state.get("prompt", "")

    # Get title from request, but prefer prompt if request title looks like a default
    request_title = request_data.get("title", "").strip()
    is_default_title = (
        not request_title or
        request_title.lower().startswith("design ") or
        request_title.lower() == "untitled"
    )

    if prompt_title and is_default_title:
        # Use the prompt as title (truncated and title-cased)
        title = prompt_title[:50].strip().title()
    elif request_title:
        title = request_title
    else:
        title = f"Design {image_id[:8]}"
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


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

@app.route('/api/batch/approve', methods=['POST'])
def batch_approve():
    """Approve multiple images at once."""
    try:
        data = request.get_json() or {}
        image_ids = data.get("image_ids", [])

        if not image_ids:
            return jsonify({"success": False, "error": "No image IDs provided"}), 400

        results = {"success": [], "failed": []}
        for image_id in image_ids:
            try:
                is_valid, error = validate_image_id(image_id)
                if not is_valid:
                    results["failed"].append({"id": image_id, "error": error})
                    continue
                state_manager.set_image_status(image_id, ImageStatus.APPROVED.value)
                results["success"].append(image_id)
            except Exception as e:
                results["failed"].append({"id": image_id, "error": str(e)})

        logger.info(f"Batch approve: {len(results['success'])} succeeded, {len(results['failed'])} failed")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Batch approve error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/batch/reject', methods=['POST'])
def batch_reject():
    """Reject multiple images at once."""
    try:
        data = request.get_json() or {}
        image_ids = data.get("image_ids", [])

        if not image_ids:
            return jsonify({"success": False, "error": "No image IDs provided"}), 400

        results = {"success": [], "failed": []}
        for image_id in image_ids:
            try:
                is_valid, error = validate_image_id(image_id)
                if not is_valid:
                    results["failed"].append({"id": image_id, "error": error})
                    continue
                state_manager.set_image_status(image_id, ImageStatus.REJECTED.value)
                results["success"].append(image_id)
            except Exception as e:
                results["failed"].append({"id": image_id, "error": str(e)})

        logger.info(f"Batch reject: {len(results['success'])} succeeded, {len(results['failed'])} failed")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Batch reject error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/batch/delete', methods=['POST'])
def batch_delete():
    """Delete multiple images at once."""
    try:
        data = request.get_json() or {}
        image_ids = data.get("image_ids", [])

        if not image_ids:
            return jsonify({"success": False, "error": "No image IDs provided"}), 400

        results = {"success": [], "failed": []}
        for image_id in image_ids:
            try:
                is_valid, error = validate_image_id(image_id)
                if not is_valid:
                    results["failed"].append({"id": image_id, "error": error})
                    continue

                # Delete image file
                image_path = Path(config.IMAGE_DIR) / f"{image_id}.png"
                if image_path.exists():
                    image_path.unlink()

                # Remove from state
                state_manager.delete_image(image_id)
                results["success"].append(image_id)
            except Exception as e:
                results["failed"].append({"id": image_id, "error": str(e)})

        logger.info(f"Batch delete: {len(results['success'])} succeeded, {len(results['failed'])} failed")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Batch delete error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/batch/publish', methods=['POST'])
def batch_publish():
    """Publish multiple approved images at once."""
    if not printify_client:
        return jsonify({"success": False, "error": "Printify not configured"}), 400

    try:
        data = request.get_json() or {}
        image_ids = data.get("image_ids", [])

        if not image_ids:
            return jsonify({"success": False, "error": "No image IDs provided"}), 400

        results = {"success": [], "failed": []}
        all_images = state_manager.get_all_images()

        for image_id in image_ids:
            try:
                is_valid, error = validate_image_id(image_id)
                if not is_valid:
                    results["failed"].append({"id": image_id, "error": error})
                    continue

                # Check if approved
                status = state_manager.get_image_status(image_id)
                if status not in [ImageStatus.APPROVED.value, ImageStatus.FAILED.value]:
                    results["failed"].append({"id": image_id, "error": f"Not approved (status: {status})"})
                    continue

                # Get image path
                image_path = os.path.join(config.IMAGE_DIR, f"{image_id}.png")
                if not os.path.exists(image_path):
                    results["failed"].append({"id": image_id, "error": "Image file not found"})
                    continue

                # Get title from prompt
                image_state = all_images.get(image_id, {})
                title = image_state.get("prompt", "")[:50].strip().title() or f"Design {image_id[:8]}"

                # Publish
                state_manager.set_image_status(image_id, ImageStatus.PUBLISHING.value)
                product_id = printify_client.create_and_publish(
                    image_path=image_path,
                    title=title,
                    blueprint_id=config.PRINTIFY_BLUEPRINT_ID,
                    provider_id=config.PRINTIFY_PROVIDER_ID,
                    price_cents=config.config.printify.default_price_cents
                )

                if product_id:
                    state_manager.set_image_status(image_id, ImageStatus.PUBLISHED.value, {
                        "product_id": product_id,
                        "title": title
                    })
                    results["success"].append({"id": image_id, "product_id": product_id, "title": title})
                else:
                    state_manager.set_image_status(image_id, ImageStatus.FAILED.value, {
                        "error_message": "Printify publish failed"
                    })
                    results["failed"].append({"id": image_id, "error": "Printify publish failed"})

            except Exception as e:
                logger.error(f"Batch publish error for {image_id}: {e}")
                try:
                    state_manager.set_image_status(image_id, ImageStatus.FAILED.value, {
                        "error_message": str(e)
                    })
                except Exception:
                    pass
                results["failed"].append({"id": image_id, "error": str(e)})

        logger.info(f"Batch publish: {len(results['success'])} succeeded, {len(results['failed'])} failed")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Batch publish error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/batch/reset', methods=['POST'])
def batch_reset():
    """Reset multiple images to pending status."""
    try:
        data = request.get_json() or {}
        image_ids = data.get("image_ids", [])

        if not image_ids:
            return jsonify({"success": False, "error": "No image IDs provided"}), 400

        results = {"success": [], "failed": []}
        for image_id in image_ids:
            try:
                is_valid, error = validate_image_id(image_id)
                if not is_valid:
                    results["failed"].append({"id": image_id, "error": error})
                    continue
                state_manager.set_image_status(image_id, ImageStatus.PENDING.value)
                results["success"].append(image_id)
            except Exception as e:
                results["failed"].append({"id": image_id, "error": str(e)})

        logger.info(f"Batch reset: {len(results['success'])} succeeded, {len(results['failed'])} failed")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Batch reset error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/batch/generate', methods=['POST'])
def batch_generate():
    """
    Generate multiple images from a list of prompts with flexible options.

    Expected JSON body:
    {
        "prompts": ["prompt1", "prompt2", ...] or [{"prompt": "...", "preset": "...", ...}, ...],
        "style": "global style (overridden by per-prompt)",
        "genre": "global genre",
        "preset": "global preset name",
        "enhance_for_pod": true/false (default true),
        "upscale": true/false (default true),
        "width": 1024,
        "height": 1024,
        "steps": 30,
        "variations": 1  // Generate N variations of each prompt with different seeds
    }
    """
    try:
        data = request.get_json() or {}
        prompts = data.get("prompts", [])

        # Global options (can be overridden per-prompt)
        global_style = (data.get("style") or "").strip()
        global_genre = (data.get("genre") or "").strip()
        global_preset = (data.get("preset") or "").strip()
        global_enhance = data.get("enhance_for_pod", True)
        global_upscale = data.get("upscale", True)
        global_width = data.get("width", 1024)
        global_height = data.get("height", 1024)
        global_steps = data.get("steps", 30)
        variations = min(data.get("variations", 1), 5)  # Max 5 variations per prompt

        if not prompts:
            return jsonify({"success": False, "error": "No prompts provided"}), 400

        # Calculate total generations (prompts * variations)
        total_jobs = len(prompts) * variations
        if total_jobs > 20:
            return jsonify({
                "success": False,
                "error": f"Maximum 20 total generations per batch (got {total_jobs}: {len(prompts)} prompts x {variations} variations)"
            }), 400

        results = {"success": [], "failed": [], "queued": []}

        for prompt_item in prompts:
            # Support both string prompts and object prompts with options
            if isinstance(prompt_item, dict):
                prompt_text = (prompt_item.get("prompt") or "").strip()
                style = (prompt_item.get("style") or global_style).strip()
                genre = (prompt_item.get("genre") or global_genre).strip()
                preset = (prompt_item.get("preset") or global_preset).strip()
                enhance = prompt_item.get("enhance_for_pod", global_enhance)
                upscale = prompt_item.get("upscale", global_upscale)
                width = prompt_item.get("width", global_width)
                height = prompt_item.get("height", global_height)
                steps = prompt_item.get("steps", global_steps)
                custom_suffix = (prompt_item.get("custom_suffix") or "").strip()
                seed = prompt_item.get("seed")  # Optional fixed seed
            else:
                prompt_text = str(prompt_item).strip()
                style = global_style
                genre = global_genre
                preset = global_preset
                enhance = global_enhance
                upscale = global_upscale
                width = global_width
                height = global_height
                steps = global_steps
                custom_suffix = ""
                seed = None

            if not prompt_text:
                results["failed"].append({"prompt": prompt_text, "error": "Empty prompt"})
                continue

            # Generate variations
            for var_idx in range(variations):
                try:
                    full_prompt = build_prompt_text(
                        prompt_text, style, genre,
                        preset=preset,
                        enhance_for_pod=enhance,
                        custom_suffix=custom_suffix
                    )

                    # Use provided seed or generate new one for each variation
                    variation_seed = seed if seed is not None else None

                    workflow = build_comfyui_workflow(
                        full_prompt,
                        seed=variation_seed,
                        width=width,
                        height=height,
                        steps=steps,
                        cfg_scale=1.0,
                        upscale=upscale
                    )

                    client_id = f"pod-gateway-batch-{uuid.uuid4().hex[:8]}"

                    if comfyui_client:
                        result = comfyui_client.submit_workflow(workflow, client_id, timeout=300)

                        if result.get("status") == "COMPLETED":
                            output = result.get("output", {})
                            saved_images = save_runpod_output_images(output, prompt=full_prompt)
                            results["success"].append({
                                "prompt": prompt_text,
                                "variation": var_idx + 1 if variations > 1 else None,
                                "preset": preset or None,
                                "images": saved_images
                            })
                        elif result.get("status") in ["IN_QUEUE", "IN_PROGRESS"]:
                            results["queued"].append({
                                "prompt": prompt_text,
                                "variation": var_idx + 1 if variations > 1 else None,
                                "job_id": result.get("job_id")
                            })
                        else:
                            results["failed"].append({
                                "prompt": prompt_text,
                                "variation": var_idx + 1 if variations > 1 else None,
                                "error": result.get("error", "Generation failed")
                            })
                    else:
                        results["failed"].append({
                            "prompt": prompt_text,
                            "error": "No generation client configured"
                        })

                except Exception as e:
                    logger.error(f"Batch generate error for prompt '{prompt_text[:30]}...': {e}")
                    results["failed"].append({
                        "prompt": prompt_text,
                        "variation": var_idx + 1 if variations > 1 else None,
                        "error": str(e)
                    })

        logger.info(f"Batch generate: {len(results['success'])} succeeded, {len(results['queued'])} queued, {len(results['failed'])} failed")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Batch generate error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/presets')
def list_presets():
    """List available POD style presets."""
    return jsonify({
        "presets": [
            {"name": name, "description": desc}
            for name, desc in POD_STYLE_PRESETS.items()
        ],
        "count": len(POD_STYLE_PRESETS)
    })


# ============================================================================
# AUTO-PROMPTING ENDPOINTS
# ============================================================================

@app.route('/api/auto-prompt', methods=['GET', 'POST'])
def auto_prompt():
    """
    Generate automatic POD prompts.

    Query params or JSON body:
        niche: Niche category (animals, nature, typography, etc.)
        style: Style modifier
        color_scheme: Color scheme
        season: Seasonal theme (spring, summer, fall, winter)
        trending: Include trending themes (true/false)
        count: Number of prompts to generate (default 1, max 20)

    Returns:
        JSON with generated prompts
    """
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args.to_dict()

    niche = data.get("niche")
    style = data.get("style")
    color_scheme = data.get("color_scheme")
    season = data.get("season")
    trending = str(data.get("trending", "false")).lower() == "true"
    count = min(int(data.get("count", 1)), 20)

    prompts = generate_auto_prompt(
        niche=niche,
        style=style,
        color_scheme=color_scheme,
        season=season,
        trending=trending,
        count=count
    )

    return jsonify({
        "prompts": prompts,
        "count": len(prompts),
        "options": {
            "niche": niche,
            "style": style,
            "color_scheme": color_scheme,
            "season": season,
            "trending": trending
        }
    })


@app.route('/api/auto-prompt/expand', methods=['POST'])
def expand_prompt_endpoint():
    """
    Expand a base prompt into multiple variations.

    JSON body:
        prompt: Base prompt to expand
        variations: Number of variations (default 5, max 10)

    Returns:
        JSON with expanded prompts
    """
    data = request.get_json() or {}
    base_prompt = (data.get("prompt") or "").strip()
    variations = min(int(data.get("variations", 5)), 10)

    if not base_prompt:
        return jsonify({"error": "Prompt is required"}), 400

    prompts = expand_prompt(base_prompt, variations)

    return jsonify({
        "base_prompt": base_prompt,
        "variations": prompts,
        "count": len(prompts)
    })


@app.route('/api/auto-prompt/niches')
def list_niches():
    """List available POD niches and their subjects."""
    return jsonify({
        "niches": {
            name: {
                "count": len(subjects),
                "examples": subjects[:3]
            }
            for name, subjects in POD_SUBJECTS.items()
        },
        "total_niches": len(POD_SUBJECTS)
    })


@app.route('/api/auto-prompt/options')
def list_prompt_options():
    """List all available auto-prompt options."""
    return jsonify({
        "niches": list(POD_SUBJECTS.keys()),
        "styles": POD_STYLE_MODIFIERS,
        "color_schemes": POD_COLOR_SCHEMES,
        "seasons": list(POD_SEASONAL.keys()),
        "trending": POD_TRENDING,
        "presets": list(POD_STYLE_PRESETS.keys())
    })


@app.route('/api/auto-prompt/generate-batch', methods=['POST'])
def auto_generate_batch():
    """
    Generate and immediately queue images from auto-generated prompts.

    JSON body:
        niche: Niche category
        style: Style modifier
        preset: Style preset name
        count: Number of images to generate (default 5, max 10)
        upscale: Whether to upscale (default true)
        enhance_for_pod: Add POD quality suffix (default true)

    Returns:
        JSON with generation results
    """
    data = request.get_json() or {}

    niche = data.get("niche")
    style = data.get("style")
    preset = data.get("preset", "")
    color_scheme = data.get("color_scheme")
    season = data.get("season")
    trending = data.get("trending", False)
    count = min(int(data.get("count", 5)), 10)
    upscale = data.get("upscale", True)
    enhance = data.get("enhance_for_pod", True)

    # Generate prompts
    prompts = generate_auto_prompt(
        niche=niche,
        style=style,
        color_scheme=color_scheme,
        season=season,
        trending=trending,
        count=count
    )

    # Use batch generate internally
    results = {"success": [], "failed": [], "queued": [], "prompts_generated": prompts}

    for prompt_text in prompts:
        try:
            full_prompt = build_prompt_text(
                prompt_text,
                preset=preset,
                enhance_for_pod=enhance
            )

            workflow = build_comfyui_workflow(
                full_prompt,
                seed=None,
                width=1024,
                height=1024,
                steps=30,
                cfg_scale=1.0,
                upscale=upscale
            )

            client_id = f"pod-gateway-auto-{uuid.uuid4().hex[:8]}"

            if comfyui_client:
                result = comfyui_client.submit_workflow(workflow, client_id, timeout=300)

                if result.get("status") == "COMPLETED":
                    output = result.get("output", {})
                    saved_images = save_runpod_output_images(output, prompt=full_prompt)
                    results["success"].append({
                        "prompt": prompt_text,
                        "images": saved_images
                    })
                elif result.get("status") in ["IN_QUEUE", "IN_PROGRESS"]:
                    results["queued"].append({
                        "prompt": prompt_text,
                        "job_id": result.get("job_id")
                    })
                else:
                    results["failed"].append({
                        "prompt": prompt_text,
                        "error": result.get("error", "Generation failed")
                    })
            else:
                results["failed"].append({
                    "prompt": prompt_text,
                    "error": "No generation client configured"
                })

        except Exception as e:
            logger.error(f"Auto-generate error: {e}")
            results["failed"].append({"prompt": prompt_text, "error": str(e)})

    logger.info(f"Auto-generate batch: {len(results['success'])} succeeded, {len(results['queued'])} queued, {len(results['failed'])} failed")
    return jsonify(results)


# ============================================================================
# BACKGROUND REMOVAL
# ============================================================================

def remove_background(image_path: str, output_path: str = None) -> str:
    """
    Remove background from an image using rembg.

    Args:
        image_path: Path to input image
        output_path: Path for output (defaults to input with _nobg suffix)

    Returns:
        Path to the output image with transparent background
    """
    if not REMBG_AVAILABLE:
        raise RuntimeError("rembg not installed. Run: pip install rembg[gpu]")

    input_path = Path(image_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Generate output path if not provided
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_nobg.png"

    # Read image, remove background, save
    with Image.open(image_path) as img:
        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Remove background
        output_img = remove_bg(img)

        # Save as PNG (supports transparency)
        output_img.save(output_path, 'PNG')

    return str(output_path)


@app.route('/api/remove-bg/<image_id>', methods=['POST'])
def remove_image_background(image_id):
    """
    Remove background from an image.

    Args:
        image_id: Image identifier

    Returns:
        JSON with new image info or error
    """
    if not REMBG_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "Background removal not available. Install rembg: pip install rembg[gpu]"
        }), 400

    # Validate image ID
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    # Get image path
    image_path = Path(config.IMAGE_DIR) / f"{image_id}.png"
    if not image_path.exists():
        return jsonify({"success": False, "error": "Image not found"}), 404

    try:
        # Check if already has _nobg version
        nobg_id = f"{image_id}_nobg"
        nobg_path = Path(config.IMAGE_DIR) / f"{nobg_id}.png"

        if nobg_path.exists():
            # Return existing nobg version
            return jsonify({
                "success": True,
                "message": "Background already removed",
                "original_id": image_id,
                "nobg_id": nobg_id,
                "nobg_path": f"/api/image/{nobg_id}"
            })

        # Remove background
        logger.info(f"Removing background from {image_id}...")
        output_path = remove_background(str(image_path), str(nobg_path))

        # Register the new image in state
        try:
            # Get original image state for prompt
            all_images = state_manager.get_all_images()
            original_state = all_images.get(image_id, {})
            original_prompt = original_state.get("prompt", "")

            state_manager.add_image(
                nobg_id,
                f"{nobg_id}.png",
                output_path,
                prompt=f"{original_prompt} (background removed)" if original_prompt else ""
            )
        except StateManagerError as e:
            logger.warning(f"Could not register nobg image in state: {e}")

        logger.info(f"Background removed: {image_id} -> {nobg_id}")
        return jsonify({
            "success": True,
            "message": "Background removed successfully",
            "original_id": image_id,
            "nobg_id": nobg_id,
            "nobg_path": f"/api/image/{nobg_id}"
        })

    except Exception as e:
        logger.error(f"Background removal failed for {image_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/batch/remove-bg', methods=['POST'])
def batch_remove_background():
    """Remove background from multiple images at once."""
    if not REMBG_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "Background removal not available. Install rembg: pip install rembg[gpu]"
        }), 400

    try:
        data = request.get_json() or {}
        image_ids = data.get("image_ids", [])

        if not image_ids:
            return jsonify({"success": False, "error": "No image IDs provided"}), 400

        results = {"success": [], "failed": [], "skipped": []}
        all_images = state_manager.get_all_images()

        for image_id in image_ids:
            try:
                # Validate
                is_valid, error = validate_image_id(image_id)
                if not is_valid:
                    results["failed"].append({"id": image_id, "error": error})
                    continue

                # Skip if already a _nobg image
                if image_id.endswith("_nobg"):
                    results["skipped"].append({"id": image_id, "reason": "Already a nobg image"})
                    continue

                image_path = Path(config.IMAGE_DIR) / f"{image_id}.png"
                if not image_path.exists():
                    results["failed"].append({"id": image_id, "error": "Image not found"})
                    continue

                # Check if nobg already exists
                nobg_id = f"{image_id}_nobg"
                nobg_path = Path(config.IMAGE_DIR) / f"{nobg_id}.png"

                if nobg_path.exists():
                    results["skipped"].append({"id": image_id, "nobg_id": nobg_id, "reason": "Already processed"})
                    continue

                # Remove background
                output_path = remove_background(str(image_path), str(nobg_path))

                # Register new image
                try:
                    original_state = all_images.get(image_id, {})
                    original_prompt = original_state.get("prompt", "")
                    state_manager.add_image(
                        nobg_id,
                        f"{nobg_id}.png",
                        output_path,
                        prompt=f"{original_prompt} (background removed)" if original_prompt else ""
                    )
                except StateManagerError:
                    pass

                results["success"].append({"id": image_id, "nobg_id": nobg_id})

            except Exception as e:
                logger.error(f"Batch remove-bg error for {image_id}: {e}")
                results["failed"].append({"id": image_id, "error": str(e)})

        logger.info(f"Batch remove-bg: {len(results['success'])} succeeded, {len(results['skipped'])} skipped, {len(results['failed'])} failed")
        return jsonify(results)

    except Exception as e:
        logger.error(f"Batch remove-bg error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/rembg-status')
def rembg_status():
    """Check if background removal is available."""
    return jsonify({
        "available": REMBG_AVAILABLE,
        "message": "rembg is installed and ready" if REMBG_AVAILABLE else "rembg not installed. Run: pip install rembg[gpu]"
    })


# ============================================================================
# PRODUCT TEMPLATES FOR MULTI-PRODUCT PUBLISHING
# ============================================================================

PRODUCT_TEMPLATES = {
    "tshirt": {
        "name": "T-Shirt",
        "blueprint_id": 3,
        "provider_id": 99,
        "description": "Classic unisex t-shirt"
    },
    "hoodie": {
        "name": "Hoodie",
        "blueprint_id": 165,
        "provider_id": 99,
        "description": "Pullover hoodie"
    },
    "tank": {
        "name": "Tank Top",
        "blueprint_id": 30,
        "provider_id": 99,
        "description": "Unisex tank top"
    },
    "longsleeve": {
        "name": "Long Sleeve",
        "blueprint_id": 4,
        "provider_id": 99,
        "description": "Long sleeve t-shirt"
    },
    "sweatshirt": {
        "name": "Sweatshirt",
        "blueprint_id": 82,
        "provider_id": 99,
        "description": "Crewneck sweatshirt"
    },
    "mug": {
        "name": "Mug",
        "blueprint_id": 68,
        "provider_id": 29,
        "description": "11oz ceramic mug"
    },
    "poster": {
        "name": "Poster",
        "blueprint_id": 117,
        "provider_id": 20,
        "description": "Museum quality poster"
    },
    "sticker": {
        "name": "Sticker",
        "blueprint_id": 505,
        "provider_id": 3,
        "description": "Die-cut sticker"
    },
    "tote": {
        "name": "Tote Bag",
        "blueprint_id": 71,
        "provider_id": 99,
        "description": "Canvas tote bag"
    },
    "pillow": {
        "name": "Throw Pillow",
        "blueprint_id": 83,
        "provider_id": 27,
        "description": "Decorative throw pillow"
    }
}


@app.route('/api/product-templates')
def list_product_templates():
    """List available product templates for multi-product publishing."""
    return jsonify({
        "templates": [
            {"id": key, **value}
            for key, value in PRODUCT_TEMPLATES.items()
        ],
        "count": len(PRODUCT_TEMPLATES)
    })


@app.route('/api/quick-publish/<image_id>', methods=['POST'])
def quick_publish(image_id):
    """
    One-click publish using default settings.
    Automatically approves if pending, then publishes with defaults.

    Args:
        image_id: Image identifier

    Returns:
        JSON with product ID or error
    """
    if not printify_client:
        return jsonify({"success": False, "error": "Printify not configured"}), 400

    # Validate image ID
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    # Get image path
    image_path = os.path.join(config.IMAGE_DIR, f"{image_id}.png")
    if not os.path.exists(image_path):
        return jsonify({"success": False, "error": "Image not found"}), 404

    try:
        # Get current status
        status = state_manager.get_image_status(image_id)

        # Auto-approve if pending
        if status == ImageStatus.PENDING.value:
            state_manager.set_image_status(image_id, ImageStatus.APPROVED.value)
            logger.info(f"Quick publish: auto-approved {image_id}")

        # Get image state for title
        all_images = state_manager.get_all_images()
        image_state = all_images.get(image_id, {})
        prompt = image_state.get("prompt", "")
        title = prompt[:50].strip().title() if prompt else f"Design {image_id[:8]}"

        # Mark as publishing
        state_manager.set_image_status(image_id, ImageStatus.PUBLISHING.value)

        # Publish with defaults
        product_id = printify_client.create_and_publish(
            image_path=image_path,
            title=title,
            blueprint_id=config.PRINTIFY_BLUEPRINT_ID,
            provider_id=config.PRINTIFY_PROVIDER_ID,
            price_cents=config.config.printify.default_price_cents
        )

        if product_id:
            state_manager.set_image_status(image_id, ImageStatus.PUBLISHED.value, {
                "product_id": product_id,
                "title": title
            })
            logger.info(f"Quick publish successful: {image_id} -> {product_id}")
            return jsonify({
                "success": True,
                "product_id": product_id,
                "title": title,
                "status": ImageStatus.PUBLISHED.value
            })
        else:
            state_manager.set_image_status(image_id, ImageStatus.FAILED.value, {
                "error_message": "Quick publish failed"
            })
            return jsonify({"success": False, "error": "Publish failed"}), 500

    except Exception as e:
        logger.error(f"Quick publish error for {image_id}: {e}", exc_info=True)
        try:
            state_manager.set_image_status(image_id, ImageStatus.FAILED.value, {
                "error_message": str(e)
            })
        except Exception:
            pass
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/multi-publish/<image_id>', methods=['POST'])
def multi_publish(image_id):
    """
    Publish the same image to multiple product types.

    Args:
        image_id: Image identifier

    Expected JSON body:
    {
        "products": ["tshirt", "hoodie", "mug"],  // Product template IDs
        "title": "Optional custom title",
        "price_cents": 1999  // Optional custom price
    }

    Returns:
        JSON with results for each product
    """
    if not printify_client:
        return jsonify({"success": False, "error": "Printify not configured"}), 400

    # Validate image ID
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    # Get image path
    image_path = os.path.join(config.IMAGE_DIR, f"{image_id}.png")
    if not os.path.exists(image_path):
        return jsonify({"success": False, "error": "Image not found"}), 404

    try:
        data = request.get_json() or {}
        product_ids = data.get("products", ["tshirt"])  # Default to t-shirt
        custom_title = data.get("title", "").strip()
        price_cents = data.get("price_cents", config.config.printify.default_price_cents)

        # Validate products
        valid_products = [p for p in product_ids if p in PRODUCT_TEMPLATES]
        if not valid_products:
            return jsonify({"success": False, "error": "No valid product types specified"}), 400

        # Get image state for title
        all_images = state_manager.get_all_images()
        image_state = all_images.get(image_id, {})
        prompt = image_state.get("prompt", "")
        base_title = custom_title or (prompt[:40].strip().title() if prompt else f"Design {image_id[:8]}")

        # Auto-approve if needed
        status = state_manager.get_image_status(image_id)
        if status == ImageStatus.PENDING.value:
            state_manager.set_image_status(image_id, ImageStatus.APPROVED.value)

        # Upload image once
        logger.info(f"Uploading image for multi-publish: {image_id}")
        printify_image_id = printify_client.upload_image(image_path, f"{image_id}.png")

        if not printify_image_id:
            return jsonify({"success": False, "error": "Failed to upload image"}), 500

        results = {"success": [], "failed": [], "image_id": image_id}

        for product_key in valid_products:
            template = PRODUCT_TEMPLATES[product_key]
            product_title = f"{base_title} - {template['name']}"

            try:
                logger.info(f"Creating {template['name']} product...")

                # Get variants for this blueprint/provider
                variants = printify_client.get_blueprint_variants(
                    template["blueprint_id"],
                    template["provider_id"]
                )
                variant_ids = [v.id for v in variants if v.is_available][:100]

                if not variant_ids:
                    results["failed"].append({
                        "product": product_key,
                        "name": template["name"],
                        "error": "No variants available"
                    })
                    continue

                # Create product
                product = printify_client.create_product(
                    title=product_title,
                    image_id=printify_image_id,
                    blueprint_id=template["blueprint_id"],
                    provider_id=template["provider_id"],
                    price_cents=price_cents,
                    variant_ids=variant_ids
                )

                if product and product.get("id"):
                    # Publish the product
                    publish_result = printify_client.publish_product(product["id"])
                    results["success"].append({
                        "product": product_key,
                        "name": template["name"],
                        "product_id": product["id"],
                        "title": product_title,
                        "published": publish_result
                    })
                else:
                    results["failed"].append({
                        "product": product_key,
                        "name": template["name"],
                        "error": "Failed to create product"
                    })

            except Exception as e:
                logger.error(f"Multi-publish error for {product_key}: {e}")
                results["failed"].append({
                    "product": product_key,
                    "name": template["name"],
                    "error": str(e)
                })

        # Update image status based on results
        if results["success"]:
            state_manager.set_image_status(image_id, ImageStatus.PUBLISHED.value, {
                "product_ids": [r["product_id"] for r in results["success"]],
                "title": base_title,
                "products": [r["product"] for r in results["success"]]
            })

        logger.info(f"Multi-publish: {len(results['success'])} succeeded, {len(results['failed'])} failed")
        return jsonify(results)

    except Exception as e:
        logger.error(f"Multi-publish error for {image_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# FAVORITES SYSTEM
# ============================================================================

@app.route('/api/favorite/<image_id>', methods=['POST'])
def toggle_favorite(image_id):
    """Toggle favorite status for an image."""
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    try:
        all_images = state_manager.get_all_images()
        image_state = all_images.get(image_id, {})

        # Toggle favorite
        is_favorite = not image_state.get("favorite", False)
        state_manager.set_image_status(
            image_id,
            image_state.get("status", ImageStatus.PENDING.value),
            {"favorite": is_favorite}
        )

        return jsonify({"success": True, "favorite": is_favorite, "id": image_id})
    except Exception as e:
        logger.error(f"Toggle favorite error for {image_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/favorites')
def list_favorites():
    """List all favorited images."""
    try:
        all_images = state_manager.get_all_images()
        favorites = [
            image_id for image_id, state in all_images.items()
            if state.get("favorite", False)
        ]
        return jsonify({"favorites": favorites, "count": len(favorites)})
    except Exception as e:
        logger.error(f"List favorites error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# TAGS SYSTEM
# ============================================================================

@app.route('/api/tags/<image_id>', methods=['GET', 'POST', 'DELETE'])
def manage_tags(image_id):
    """Manage tags for an image."""
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    try:
        all_images = state_manager.get_all_images()
        image_state = all_images.get(image_id, {})
        current_tags = image_state.get("tags", [])

        if request.method == 'GET':
            return jsonify({"tags": current_tags, "id": image_id})

        data = request.get_json() or {}

        if request.method == 'POST':
            # Add tags
            new_tags = data.get("tags", [])
            if isinstance(new_tags, str):
                new_tags = [t.strip() for t in new_tags.split(",") if t.strip()]

            # Merge and dedupe
            all_tags = list(set(current_tags + new_tags))[:20]  # Max 20 tags

            state_manager.set_image_status(
                image_id,
                image_state.get("status", ImageStatus.PENDING.value),
                {"tags": all_tags}
            )
            return jsonify({"success": True, "tags": all_tags, "id": image_id})

        elif request.method == 'DELETE':
            # Remove specific tags
            remove_tags = data.get("tags", [])
            if isinstance(remove_tags, str):
                remove_tags = [t.strip() for t in remove_tags.split(",") if t.strip()]

            remaining_tags = [t for t in current_tags if t not in remove_tags]

            state_manager.set_image_status(
                image_id,
                image_state.get("status", ImageStatus.PENDING.value),
                {"tags": remaining_tags}
            )
            return jsonify({"success": True, "tags": remaining_tags, "id": image_id})

    except Exception as e:
        logger.error(f"Manage tags error for {image_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/all-tags')
def list_all_tags():
    """List all unique tags across all images."""
    try:
        all_images = state_manager.get_all_images()
        all_tags = set()
        tag_counts = {}

        for image_id, state in all_images.items():
            tags = state.get("tags", [])
            for tag in tags:
                all_tags.add(tag)
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return jsonify({
            "tags": sorted(list(all_tags)),
            "counts": tag_counts,
            "total_unique": len(all_tags)
        })
    except Exception as e:
        logger.error(f"List all tags error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# NOTES SYSTEM
# ============================================================================

@app.route('/api/notes/<image_id>', methods=['GET', 'POST', 'DELETE'])
def manage_notes(image_id):
    """Manage notes for an image."""
    is_valid, error = validate_image_id(image_id)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    try:
        all_images = state_manager.get_all_images()
        image_state = all_images.get(image_id, {})

        if request.method == 'GET':
            return jsonify({
                "notes": image_state.get("notes", ""),
                "id": image_id
            })

        data = request.get_json() or {}

        if request.method == 'POST':
            note = (data.get("notes") or "").strip()[:1000]  # Max 1000 chars
            state_manager.set_image_status(
                image_id,
                image_state.get("status", ImageStatus.PENDING.value),
                {"notes": note}
            )
            return jsonify({"success": True, "notes": note, "id": image_id})

        elif request.method == 'DELETE':
            state_manager.set_image_status(
                image_id,
                image_state.get("status", ImageStatus.PENDING.value),
                {"notes": ""}
            )
            return jsonify({"success": True, "notes": "", "id": image_id})

    except Exception as e:
        logger.error(f"Manage notes error for {image_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

# In-memory storage for prompt templates (persisted via state manager)
def get_prompt_templates() -> List[Dict]:
    """Get saved prompt templates from state."""
    try:
        # Store templates in a special state entry
        all_state = state_manager.get_all_images()
        templates_data = all_state.get("__prompt_templates__", {})
        return templates_data.get("templates", [])
    except Exception:
        return []


def save_prompt_templates(templates: List[Dict]):
    """Save prompt templates to state."""
    try:
        state_manager.set_image_status("__prompt_templates__", "system", {
            "templates": templates
        })
    except Exception as e:
        logger.error(f"Failed to save templates: {e}")


@app.route('/api/prompt-templates', methods=['GET', 'POST'])
def prompt_templates():
    """List or create prompt templates."""
    if request.method == 'GET':
        templates = get_prompt_templates()
        return jsonify({"templates": templates, "count": len(templates)})

    try:
        data = request.get_json() or {}
        name = (data.get("name") or "").strip()
        prompt = (data.get("prompt") or "").strip()
        preset = data.get("preset", "")

        if not name or not prompt:
            return jsonify({"error": "Name and prompt are required"}), 400

        templates = get_prompt_templates()

        # Check for duplicate names
        if any(t["name"] == name for t in templates):
            return jsonify({"error": "Template name already exists"}), 400

        new_template = {
            "id": uuid.uuid4().hex[:8],
            "name": name,
            "prompt": prompt,
            "preset": preset,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        templates.append(new_template)
        save_prompt_templates(templates)

        return jsonify({"success": True, "template": new_template})
    except Exception as e:
        logger.error(f"Create template error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/prompt-templates/<template_id>', methods=['GET', 'DELETE'])
def manage_prompt_template(template_id):
    """Get or delete a specific prompt template."""
    templates = get_prompt_templates()
    template = next((t for t in templates if t["id"] == template_id), None)

    if not template:
        return jsonify({"error": "Template not found"}), 404

    if request.method == 'GET':
        return jsonify({"template": template})

    elif request.method == 'DELETE':
        templates = [t for t in templates if t["id"] != template_id]
        save_prompt_templates(templates)
        return jsonify({"success": True, "deleted": template_id})


# ============================================================================
# GENERATION HISTORY
# ============================================================================

@app.route('/api/generation-history')
def generation_history():
    """Get generation history with prompts and timestamps."""
    try:
        all_images = state_manager.get_all_images()
        history = []

        for image_id, state in all_images.items():
            if image_id.startswith("__"):  # Skip system entries
                continue

            prompt = state.get("prompt", "")
            if prompt:
                history.append({
                    "id": image_id,
                    "prompt": prompt,
                    "status": state.get("status", "pending"),
                    "created_at": state.get("created_at"),
                    "favorite": state.get("favorite", False),
                    "tags": state.get("tags", [])
                })

        # Sort by created_at descending
        history.sort(key=lambda x: x.get("created_at") or "", reverse=True)

        return jsonify({
            "history": history[:100],  # Last 100 entries
            "total": len(history)
        })
    except Exception as e:
        logger.error(f"Generation history error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# EXPORT FUNCTIONALITY
# ============================================================================

@app.route('/api/export/zip', methods=['POST'])
def export_zip():
    """
    Export selected images as a ZIP file.

    Expected JSON body:
    {
        "image_ids": ["id1", "id2", ...],
        "include_metadata": true/false
    }
    """
    import zipfile
    import io
    import json

    try:
        data = request.get_json() or {}
        image_ids = data.get("image_ids", [])
        include_metadata = data.get("include_metadata", True)

        if not image_ids:
            return jsonify({"error": "No image IDs provided"}), 400

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        all_images = state_manager.get_all_images()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            metadata = []

            for image_id in image_ids:
                is_valid, _ = validate_image_id(image_id)
                if not is_valid:
                    continue

                image_path = Path(config.IMAGE_DIR) / f"{image_id}.png"
                if not image_path.exists():
                    continue

                # Add image to ZIP
                zf.write(image_path, f"{image_id}.png")

                # Collect metadata
                if include_metadata:
                    state = all_images.get(image_id, {})
                    metadata.append({
                        "id": image_id,
                        "filename": f"{image_id}.png",
                        "prompt": state.get("prompt", ""),
                        "status": state.get("status", ""),
                        "tags": state.get("tags", []),
                        "created_at": state.get("created_at")
                    })

            # Add metadata JSON
            if include_metadata and metadata:
                zf.writestr("metadata.json", json.dumps(metadata, indent=2))

        zip_buffer.seek(0)

        from flask import send_file
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'pod_export_{time.strftime("%Y%m%d_%H%M%S")}.zip'
        )

    except Exception as e:
        logger.error(f"Export ZIP error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ENHANCED DASHBOARD STATS
# ============================================================================

@app.route('/api/dashboard')
def dashboard_stats():
    """Get comprehensive dashboard statistics."""
    try:
        all_images = state_manager.get_all_images()
        basic_stats = state_manager.get_statistics()

        # Count by status
        status_counts = {"pending": 0, "approved": 0, "published": 0, "rejected": 0, "failed": 0}
        favorites_count = 0
        tagged_count = 0
        with_notes_count = 0
        total_tags = set()
        prompts_used = set()

        for image_id, state in all_images.items():
            if image_id.startswith("__"):
                continue

            status = state.get("status", "pending")
            if status in status_counts:
                status_counts[status] += 1

            if state.get("favorite"):
                favorites_count += 1

            tags = state.get("tags", [])
            if tags:
                tagged_count += 1
                total_tags.update(tags)

            if state.get("notes"):
                with_notes_count += 1

            if state.get("prompt"):
                prompts_used.add(state["prompt"][:50])

        return jsonify({
            "overview": {
                "total_images": basic_stats.get("total", 0),
                "favorites": favorites_count,
                "tagged": tagged_count,
                "with_notes": with_notes_count,
                "unique_prompts": len(prompts_used),
                "unique_tags": len(total_tags)
            },
            "by_status": status_counts,
            "recent_tags": sorted(list(total_tags))[:10],
            "templates_count": len(get_prompt_templates()),
            "rembg_available": REMBG_AVAILABLE,
            "printify_configured": printify_client is not None,
            "runpod_configured": comfyui_client is not None
        })
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# IMAGE COLLECTIONS
# ============================================================================

def get_collections() -> List[Dict]:
    """Get saved collections from state."""
    try:
        all_state = state_manager.get_all_images()
        collections_data = all_state.get("__collections__", {})
        return collections_data.get("collections", [])
    except Exception:
        return []


def save_collections(collections: List[Dict]):
    """Save collections to state."""
    try:
        state_manager.set_image_status("__collections__", "system", {
            "collections": collections
        })
    except Exception as e:
        logger.error(f"Failed to save collections: {e}")


@app.route('/api/collections', methods=['GET', 'POST'])
def manage_collections():
    """List or create collections."""
    if request.method == 'GET':
        collections = get_collections()
        return jsonify({"collections": collections, "count": len(collections)})

    try:
        data = request.get_json() or {}
        name = (data.get("name") or "").strip()
        description = (data.get("description") or "").strip()

        if not name:
            return jsonify({"error": "Collection name is required"}), 400

        collections = get_collections()

        new_collection = {
            "id": uuid.uuid4().hex[:8],
            "name": name,
            "description": description,
            "image_ids": [],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        collections.append(new_collection)
        save_collections(collections)

        return jsonify({"success": True, "collection": new_collection})
    except Exception as e:
        logger.error(f"Create collection error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/collections/<collection_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_single_collection(collection_id):
    """Get, update, or delete a specific collection."""
    collections = get_collections()
    collection_idx = next((i for i, c in enumerate(collections) if c["id"] == collection_id), None)

    if collection_idx is None:
        return jsonify({"error": "Collection not found"}), 404

    if request.method == 'GET':
        return jsonify({"collection": collections[collection_idx]})

    elif request.method == 'DELETE':
        deleted = collections.pop(collection_idx)
        save_collections(collections)
        return jsonify({"success": True, "deleted": deleted["id"]})

    elif request.method == 'PUT':
        data = request.get_json() or {}

        # Update name/description if provided
        if "name" in data:
            collections[collection_idx]["name"] = data["name"].strip()
        if "description" in data:
            collections[collection_idx]["description"] = data["description"].strip()

        # Add images
        if "add_images" in data:
            current_ids = set(collections[collection_idx]["image_ids"])
            for img_id in data["add_images"]:
                is_valid, _ = validate_image_id(img_id)
                if is_valid:
                    current_ids.add(img_id)
            collections[collection_idx]["image_ids"] = list(current_ids)

        # Remove images
        if "remove_images" in data:
            remove_set = set(data["remove_images"])
            collections[collection_idx]["image_ids"] = [
                img_id for img_id in collections[collection_idx]["image_ids"]
                if img_id not in remove_set
            ]

        save_collections(collections)
        return jsonify({"success": True, "collection": collections[collection_idx]})


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


@app.route('/api/debug/config')
def debug_config():
    """
    Debug endpoint to diagnose configuration issues.
    Shows key lengths and prefixes (not full keys) to help identify
    placeholder vs real API keys.

    Returns:
        JSON with configuration diagnostics
    """
    def mask_key(key: str, show_prefix: int = 10, show_suffix: int = 4) -> dict:
        """Return info about a key without exposing the full value."""
        if not key:
            return {"length": 0, "prefix": "", "suffix": "", "is_placeholder": True}
        is_placeholder = key.startswith("your-") or key in ["", "placeholder", "test"]
        return {
            "length": len(key),
            "prefix": key[:show_prefix] if len(key) > show_prefix else key[:3] + "...",
            "suffix": key[-show_suffix:] if len(key) > show_suffix else "",
            "is_placeholder": is_placeholder
        }

    # Check which .env files exist
    project_root = Path(__file__).parent.parent.parent
    env_files = {
        "project_root/.env": (project_root / ".env").exists(),
        "gateway/.env": (project_root / "gateway" / ".env").exists(),
        "gateway/app/.env": (project_root / "gateway" / "app" / ".env").exists(),
    }

    return jsonify({
        "env_files_found": env_files,
        "printify": {
            "api_key": mask_key(config.PRINTIFY_API_KEY or ""),
            "shop_id": config.PRINTIFY_SHOP_ID,
            "blueprint_id": config.PRINTIFY_BLUEPRINT_ID,
            "provider_id": config.PRINTIFY_PROVIDER_ID,
            "client_initialized": printify_client is not None
        },
        "runpod": {
            "api_key": mask_key(config.RUNPOD_API_KEY or ""),
            "endpoint_id": config.RUNPOD_ENDPOINT_ID,
            "client_initialized": comfyui_client is not None
        },
        "paths": {
            "image_dir": config.IMAGE_DIR,
            "image_dir_exists": os.path.exists(config.IMAGE_DIR),
            "state_file": config.STATE_FILE,
            "state_file_exists": os.path.exists(config.STATE_FILE)
        }
    })


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

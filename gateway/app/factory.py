"""
Flask Application Factory

Creates and configures the Flask application with all services and routes.
"""
import logging
import os
from pathlib import Path
from typing import Optional

from flask import Flask, render_template
from dotenv import load_dotenv

from app.state import StateManager
from app.printify_client import RetryConfig
from app.clients import create_generation_client
from app.services.generation import GenerationService
from app.services.image import ImageService
from app.services.publishing import create_publishing_service
from app.routes import api_bp, health_bp

logger = logging.getLogger(__name__)


def load_environment() -> None:
    """Load environment variables from .env files"""
    # Load from project root first (contains API keys)
    project_root = Path(__file__).parent.parent.parent
    root_env = project_root / ".env"
    if root_env.exists():
        load_dotenv(root_env)

    # Also load from current dir but don't override
    load_dotenv(override=False)


def get_config() -> dict:
    """
    Build configuration from environment variables.

    Returns:
        Configuration dictionary
    """
    # RunPod configuration
    runpod_endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
    runpod_api_key = os.getenv("RUNPOD_API_KEY")

    # Build ComfyUI/RunPod URL
    if runpod_endpoint_id and runpod_api_key:
        api_url = f"https://api.runpod.ai/v2/{runpod_endpoint_id}/runsync"
    else:
        api_url = os.getenv("COMFYUI_API_URL", "http://localhost:8188")

    return {
        # Filesystem
        "IMAGE_DIR": os.getenv("POD_IMAGE_DIR", "/workspace/comfyui/output"),
        "STATE_FILE": os.getenv("POD_STATE_FILE", "/workspace/gateway/state.json"),
        "ARCHIVE_DIR": os.getenv("POD_ARCHIVE_DIR", "/workspace/gateway/archive"),

        # Flask
        "HOST": os.getenv("FLASK_HOST", "0.0.0.0"),
        "PORT": int(os.getenv("FLASK_PORT", "5000")),
        "DEBUG": os.getenv("FLASK_DEBUG", "false").lower() == "true",

        # ComfyUI / RunPod
        "COMFYUI_API_URL": api_url,
        "RUNPOD_API_KEY": runpod_api_key,
        "RUNPOD_ENDPOINT_ID": runpod_endpoint_id,

        # Printify
        "PRINTIFY_API_KEY": os.getenv("PRINTIFY_API_KEY"),
        "PRINTIFY_SHOP_ID": os.getenv("PRINTIFY_SHOP_ID"),
        "PRINTIFY_BLUEPRINT_ID": int(os.getenv("PRINTIFY_BLUEPRINT_ID", "77")),
        "PRINTIFY_PROVIDER_ID": int(os.getenv("PRINTIFY_PROVIDER_ID", "39")),

        # Retry
        "MAX_RETRIES": int(os.getenv("API_MAX_RETRIES", "3")),
        "INITIAL_BACKOFF": float(os.getenv("API_INITIAL_BACKOFF_SECONDS", "1.0")),
        "MAX_BACKOFF": float(os.getenv("API_MAX_BACKOFF_SECONDS", "30.0")),
        "BACKOFF_MULTIPLIER": float(os.getenv("API_BACKOFF_MULTIPLIER", "2.0")),

        # Logging
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO").upper(),
    }


def create_app(config_override: Optional[dict] = None) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config_override: Optional configuration overrides for testing

    Returns:
        Configured Flask application
    """
    # Load environment variables
    load_environment()

    # Get configuration
    config = get_config()
    if config_override:
        config.update(config_override)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config["LOG_LEVEL"]),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create Flask app
    app = Flask(
        __name__,
        template_folder="../templates"
    )

    # Store config in app
    app.config.update(config)

    # Ensure directories exist
    Path(config["IMAGE_DIR"]).mkdir(parents=True, exist_ok=True)
    Path(config["STATE_FILE"]).parent.mkdir(parents=True, exist_ok=True)

    # Initialize services
    _init_services(app, config)

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(health_bp)

    # Register index route
    @app.route("/")
    def index():
        return render_template("gallery.html")

    # Register error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal error: {e}", exc_info=True)
        return {"error": "Internal server error"}, 500

    return app


def _init_services(app: Flask, config: dict) -> None:
    """Initialize all application services"""

    # State manager
    state_manager = StateManager(config["STATE_FILE"])

    # Image service
    comfyui_url = config["COMFYUI_API_URL"] if "api.runpod.ai" not in config["COMFYUI_API_URL"] else None
    image_service = ImageService(
        image_dir=config["IMAGE_DIR"],
        state_manager=state_manager,
        comfyui_url=comfyui_url
    )
    app.config["image_service"] = image_service

    # Generation client and service
    generation_client = None
    try:
        if config["COMFYUI_API_URL"]:
            generation_client = create_generation_client(
                api_url=config["COMFYUI_API_URL"],
                runpod_api_key=config["RUNPOD_API_KEY"]
            )
            logger.info(f"Generation client: {generation_client.name}")
    except ValueError as e:
        logger.warning(f"Generation client not configured: {e}")
    except Exception as e:
        logger.error(f"Failed to create generation client: {e}")

    generation_service = GenerationService(
        client=generation_client,
        image_service=image_service
    )
    app.config["generation_service"] = generation_service

    # Publishing service
    retry_config = RetryConfig(
        max_retries=config["MAX_RETRIES"],
        initial_backoff=config["INITIAL_BACKOFF"],
        max_backoff=config["MAX_BACKOFF"],
        backoff_multiplier=config["BACKOFF_MULTIPLIER"]
    )

    publishing_service = create_publishing_service(
        api_key=config["PRINTIFY_API_KEY"],
        shop_id=config["PRINTIFY_SHOP_ID"],
        image_service=image_service,
        retry_config=retry_config
    )
    app.config["publishing_service"] = publishing_service

    # Log service status
    logger.info("Services initialized:")
    logger.info(f"  - Image service: {config['IMAGE_DIR']}")
    logger.info(f"  - Generation: {generation_service.backend_name}")
    logger.info(f"  - Publishing: {'Printify' if publishing_service.is_available else 'disabled'}")

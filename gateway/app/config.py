"""
Gateway Configuration
Loads and validates settings from environment variables with type safety
"""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import sys


@dataclass
class FilesystemConfig:
    """Filesystem paths configuration"""
    image_dir: Path
    state_file: Path
    archive_dir: Path

    def validate(self) -> None:
        """Ensure all directories exist"""
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class FlaskConfig:
    """Flask server configuration"""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False

    def validate(self) -> None:
        """Validate Flask configuration"""
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Invalid port number: {self.port}")
        if self.debug:
            print("⚠️  WARNING: Debug mode is enabled. Do not use in production!")


@dataclass
class PrintifyConfig:
    """Printify API configuration"""
    api_key: Optional[str]
    shop_id: Optional[str]
    blueprint_id: int = 77  # Gildan 18500 Heavy Blend Hoodie (most popular POD product)
    provider_id: int = 39  # SwiftPOD (US-based, reliable, fast shipping)
    default_price_cents: int = 3499  # $34.99 (typical hoodie price)

    def validate(self) -> None:
        """Validate Printify configuration"""
        # Skip validation for placeholder/unset values
        if self.api_key and self.api_key.startswith('your-'):
            return
        if self.shop_id and self.shop_id.startswith('your-'):
            return

        if self.api_key and len(self.api_key) < 10:
            raise ValueError("Invalid Printify API key")
        if self.shop_id and not self.shop_id.isdigit():
            raise ValueError("Invalid Printify Shop ID (must be numeric)")
        if self.default_price_cents < 0:
            raise ValueError("Price must be non-negative")

    def is_configured(self) -> bool:
        """Check if Printify is fully configured"""
        return bool(self.api_key and self.shop_id)

    # Blueprint ID to product type mapping (for auto-titles)
    BLUEPRINT_TYPES = {
        3: "Tee",
        5: "Tee",
        77: "Hoodie",
        145: "Sweatshirt",
        6: "Poster",
        384: "Canvas",
        12: "Tank Top",
        19: "Long Sleeve"
    }

    def get_product_type(self, blueprint_id: int = None) -> str:
        """Get product type name from blueprint ID"""
        bid = blueprint_id if blueprint_id else self.blueprint_id
        return self.BLUEPRINT_TYPES.get(bid, "Hoodie")


@dataclass
class ShopifyConfig:
    """Shopify store configuration (optional)"""
    store_url: Optional[str]
    access_token: Optional[str]

    def is_configured(self) -> bool:
        """Check if Shopify is configured"""
        return bool(self.store_url and self.access_token)


@dataclass
class RetryConfig:
    """Retry configuration for API calls"""
    max_retries: int = 3
    initial_backoff_seconds: float = 1.0
    max_backoff_seconds: float = 30.0
    backoff_multiplier: float = 2.0

    def validate(self) -> None:
        """Validate retry configuration"""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.initial_backoff_seconds <= 0:
            raise ValueError("initial_backoff_seconds must be positive")
        if self.max_backoff_seconds < self.initial_backoff_seconds:
            raise ValueError("max_backoff_seconds must be >= initial_backoff_seconds")
        if self.backoff_multiplier <= 1:
            raise ValueError("backoff_multiplier must be > 1")


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def validate(self) -> None:
        """Validate logging configuration"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {self.level}. Must be one of {valid_levels}")


@dataclass
class ComfyUIConfig:
    """ComfyUI API configuration"""
    api_url: str
    runpod_api_key: Optional[str] = None

    def validate(self) -> None:
        """Validate ComfyUI configuration"""
        if not self.api_url:
            raise ValueError("COMFYUI_API_URL must be set")

    def is_runpod_serverless(self) -> bool:
        """Check if this is a RunPod serverless endpoint"""
        return "api.runpod.ai" in self.api_url or "runsync" in self.api_url


class GatewayConfig:
    """Main configuration class that aggregates all config sections"""

    def __init__(self):
        self.filesystem = FilesystemConfig(
            image_dir=Path(os.getenv("POD_IMAGE_DIR", "/workspace/comfyui/output")),
            state_file=Path(os.getenv("POD_STATE_FILE", "/workspace/gateway/state.json")),
            archive_dir=Path(os.getenv("POD_ARCHIVE_DIR", "/workspace/gateway/archive"))
        )

        self.flask = FlaskConfig(
            host=os.getenv("FLASK_HOST", "0.0.0.0"),
            port=int(os.getenv("FLASK_PORT", "5000")),
            debug=os.getenv("FLASK_DEBUG", "false").lower() == "true"
        )

        self.printify = PrintifyConfig(
            api_key=os.getenv("PRINTIFY_API_KEY"),
            shop_id=os.getenv("PRINTIFY_SHOP_ID"),
            blueprint_id=int(os.getenv("PRINTIFY_BLUEPRINT_ID", "77")),  # Gildan 18500 Heavy Blend Hoodie
            provider_id=int(os.getenv("PRINTIFY_PROVIDER_ID", "39")),  # SwiftPOD
            default_price_cents=int(os.getenv("PRINTIFY_DEFAULT_PRICE_CENTS", "3499"))  # $34.99
        )

        self.shopify = ShopifyConfig(
            store_url=os.getenv("SHOPIFY_STORE_URL"),
            access_token=os.getenv("SHOPIFY_ACCESS_TOKEN")
        )

        self.retry = RetryConfig(
            max_retries=int(os.getenv("API_MAX_RETRIES", "3")),
            initial_backoff_seconds=float(os.getenv("API_INITIAL_BACKOFF_SECONDS", "1.0")),
            max_backoff_seconds=float(os.getenv("API_MAX_BACKOFF_SECONDS", "30.0")),
            backoff_multiplier=float(os.getenv("API_BACKOFF_MULTIPLIER", "2.0"))
        )

        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO").upper(),
            format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        self.comfyui = ComfyUIConfig(
            api_url=os.getenv("COMFYUI_API_URL", "http://localhost:8188"),
            runpod_api_key=os.getenv("RUNPOD_API_KEY")
        )

    def validate_all(self) -> None:
        """Validate all configuration sections"""
        try:
            self.filesystem.validate()
            self.flask.validate()
            self.printify.validate()
            self.retry.validate()
            self.logging.validate()
            self.comfyui.validate()
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}", file=sys.stderr)
            raise

    def print_summary(self) -> None:
        """Print configuration summary"""
        print("=" * 60)
        print("POD GATEWAY CONFIGURATION")
        print("=" * 60)
        print(f"📁 Image Directory:    {self.filesystem.image_dir}")
        print(f"💾 State File:         {self.filesystem.state_file}")
        print(f"📦 Archive Directory:  {self.filesystem.archive_dir}")
        print(f"🌐 Flask Host:Port:    {self.flask.host}:{self.flask.port}")
        print(f"🐛 Debug Mode:         {self.flask.debug}")
        print(f"🔌 Printify:           {'✓ Configured' if self.printify.is_configured() else '✗ Not configured'}")
        print(f"🛒 Shopify:            {'✓ Configured' if self.shopify.is_configured() else '✗ Not configured'}")
        print(f"🔄 Max Retries:        {self.retry.max_retries}")
        print(f"📊 Log Level:          {self.logging.level}")
        print(f"🧠 ComfyUI API:        {self.comfyui.api_url}")
        print("=" * 60)


# Create and validate global config instance
config = GatewayConfig()
config.validate_all()


# Legacy compatibility: expose individual config values as module-level variables
IMAGE_DIR = str(config.filesystem.image_dir)
STATE_FILE = str(config.filesystem.state_file)
ARCHIVE_DIR = str(config.filesystem.archive_dir)
FLASK_HOST = config.flask.host
FLASK_PORT = config.flask.port
FLASK_DEBUG = config.flask.debug
PRINTIFY_API_KEY = config.printify.api_key
PRINTIFY_SHOP_ID = config.printify.shop_id
PRINTIFY_BLUEPRINT_ID = config.printify.blueprint_id
PRINTIFY_PROVIDER_ID = config.printify.provider_id
SHOPIFY_STORE_URL = config.shopify.store_url
SHOPIFY_ACCESS_TOKEN = config.shopify.access_token
COMFYUI_API_URL = config.comfyui.api_url

"""
Gateway Configuration
Loads settings from environment variables
"""
import os
from pathlib import Path

# Filesystem
IMAGE_DIR = os.getenv("POD_IMAGE_DIR", "/workspace/comfyui/output")
STATE_FILE = os.getenv("POD_STATE_FILE", "/workspace/gateway/state.json")
ARCHIVE_DIR = os.getenv("POD_ARCHIVE_DIR", "/workspace/gateway/archive")

# Flask
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# Printify API
PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")
PRINTIFY_BLUEPRINT_ID = int(os.getenv("PRINTIFY_BLUEPRINT_ID", "3"))  # T-shirt
PRINTIFY_PROVIDER_ID = int(os.getenv("PRINTIFY_PROVIDER_ID", "99"))  # SwiftPOD

# Shopify (optional)
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

# Ensure directories exist
Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)
Path(ARCHIVE_DIR).mkdir(parents=True, exist_ok=True)
Path(STATE_FILE).parent.mkdir(parents=True, exist_ok=True)

"""
POD Dashboard Configuration
Unified configuration for all POD tools
"""
import os
from pathlib import Path

# Flask
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# Claude API (for prompter)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

# Printify (for gateway)
PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")
PRINTIFY_BLUEPRINT_ID = int(os.getenv("PRINTIFY_BLUEPRINT_ID", "3"))
PRINTIFY_PROVIDER_ID = int(os.getenv("PRINTIFY_PROVIDER_ID", "99"))

# Storage paths
IMAGE_DIR = os.getenv("POD_IMAGE_DIR", "/workspace/comfyui/output")
STATE_FILE = os.getenv("POD_STATE_FILE", "/workspace/dashboard/state.json")
ARCHIVE_DIR = os.getenv("POD_ARCHIVE_DIR", "/workspace/dashboard/archive")
PROMPTS_DIR = os.getenv("PROMPTER_OUTPUT_DIR", "/workspace/prompts")

# ComfyUI (optional)
COMFYUI_API_URL = os.getenv("COMFYUI_API_URL", "http://localhost:8188")

# Ensure directories exist
Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)
Path(ARCHIVE_DIR).mkdir(parents=True, exist_ok=True)
Path(PROMPTS_DIR).mkdir(parents=True, exist_ok=True)
Path(STATE_FILE).parent.mkdir(parents=True, exist_ok=True)

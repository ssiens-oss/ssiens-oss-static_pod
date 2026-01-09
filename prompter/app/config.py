"""
AI Prompter Configuration
"""
import os
from pathlib import Path

# Flask
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

# ComfyUI (optional)
COMFYUI_API_URL = os.getenv("COMFYUI_API_URL", "http://localhost:8188")

# Output
OUTPUT_DIR = os.getenv("PROMPTER_OUTPUT_DIR", "/workspace/prompts")
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

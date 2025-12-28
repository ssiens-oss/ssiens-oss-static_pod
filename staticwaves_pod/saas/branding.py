"""
White-Label Branding Configuration

Allows SaaS resellers to customize branding via environment variables.
"""

import os
import sys
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

log = get_logger("BRANDING")

# Default branding
DEFAULT_BRAND = "StaticWaves"
DEFAULT_COLOR = "#7F5BFF"
DEFAULT_LOGO = "/logo.png"


def brand() -> Dict[str, str]:
    """
    Get current branding configuration.

    Reads from environment variables:
    - SAAS_BRAND: Product name
    - SAAS_COLOR: Primary brand color (hex)
    - SAAS_LOGO: Logo path/URL

    Returns:
        Dictionary with branding config
    """
    config = {
        "name": os.getenv("SAAS_BRAND", DEFAULT_BRAND),
        "primary_color": os.getenv("SAAS_COLOR", DEFAULT_COLOR),
        "logo": os.getenv("SAAS_LOGO", DEFAULT_LOGO),
        "tagline": os.getenv("SAAS_TAGLINE", "TikTok POD Engine"),
        "support_email": os.getenv("SAAS_SUPPORT_EMAIL", "support@staticwaves.io"),
        "docs_url": os.getenv("SAAS_DOCS_URL", "https://docs.staticwaves.io")
    }

    log.debug(f"🎨 Loaded branding: {config['name']}")
    return config


def get_theme() -> Dict[str, str]:
    """
    Get UI theme colors.

    Returns:
        Dictionary of theme colors
    """
    primary = os.getenv("SAAS_COLOR", DEFAULT_COLOR)

    return {
        "primary": primary,
        "secondary": os.getenv("SAAS_SECONDARY_COLOR", "#F97316"),
        "accent": os.getenv("SAAS_ACCENT_COLOR", "#10B981"),
        "background": os.getenv("SAAS_BG_COLOR", "#FFFFFF"),
        "text": os.getenv("SAAS_TEXT_COLOR", "#1F2937")
    }


def get_footer_text() -> str:
    """
    Get customizable footer text.

    Returns:
        Footer text string
    """
    brand_name = os.getenv("SAAS_BRAND", DEFAULT_BRAND)
    year = os.getenv("SAAS_YEAR", "2025")

    return os.getenv(
        "SAAS_FOOTER",
        f"© {year} {brand_name}. All rights reserved."
    )


if __name__ == "__main__":
    import json

    print("\n🎨 Current Branding Configuration:\n")
    print(json.dumps(brand(), indent=2))

    print("\n🎨 Theme Colors:\n")
    print(json.dumps(get_theme(), indent=2))

    print(f"\n{get_footer_text()}\n")

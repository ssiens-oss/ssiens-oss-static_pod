"""
SaaS Bootstrap Module

Initializes and validates SaaS environment on startup.
Checks licensing, branding, and required configuration.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger
from saas.license import check_license
from saas.branding import brand

log = get_logger("BOOTSTRAP")


def init() -> bool:
    """
    Initialize SaaS environment.

    Validates:
    - License key
    - Required environment variables
    - Branding configuration

    Returns:
        True if initialization successful

    Raises:
        RuntimeError if critical configuration missing
    """
    log.info("🚀 Initializing SaaS environment...")

    # Check license
    if not os.environ.get("LICENSE_KEY"):
        raise RuntimeError(
            "❌ LICENSE_KEY not set. "
            "Generate a key with: python -m staticwaves_pod.saas.license generate"
        )

    if not check_license():
        raise RuntimeError("❌ Invalid LICENSE_KEY")

    log.info("✅ License validated")

    # Load branding
    branding = brand()
    log.info(f"✅ Branding loaded: {branding['name']}")

    # Check TikTok credentials
    if not os.environ.get("TIKTOK_CLIENT_ID"):
        log.warning("⚠️  TIKTOK_CLIENT_ID not set")

    if not os.environ.get("TIKTOK_CLIENT_SECRET"):
        log.warning("⚠️  TIKTOK_CLIENT_SECRET not set")

    log.info("✅ SaaS environment initialized")
    return True


def health_check() -> dict:
    """
    Perform health check on SaaS environment.

    Returns:
        Dictionary with health status
    """
    status = {
        "license": False,
        "tiktok_oauth": False,
        "branding": False,
        "overall": "unhealthy"
    }

    # License check
    try:
        status["license"] = check_license()
    except Exception as e:
        log.error(f"License check failed: {e}")

    # TikTok OAuth check
    status["tiktok_oauth"] = bool(
        os.environ.get("TIKTOK_CLIENT_ID") and
        os.environ.get("TIKTOK_CLIENT_SECRET")
    )

    # Branding check
    try:
        branding = brand()
        status["branding"] = bool(branding.get("name"))
    except Exception as e:
        log.error(f"Branding check failed: {e}")

    # Overall status
    if all([status["license"], status["tiktok_oauth"], status["branding"]]):
        status["overall"] = "healthy"
    elif status["license"]:
        status["overall"] = "degraded"
    else:
        status["overall"] = "unhealthy"

    return status


if __name__ == "__main__":
    import json

    try:
        init()
        print("\n✅ SaaS initialized successfully\n")

        health = health_check()
        print("📊 Health Status:")
        print(json.dumps(health, indent=2))
        print()

    except Exception as e:
        print(f"\n❌ Initialization failed: {e}\n")
        sys.exit(1)

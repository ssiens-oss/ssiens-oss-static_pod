"""
StaticWaves Printify Auto-Publisher - Production POD Engine

Features:
1. Auto-pricing = cost + margin
2. TikTok-safe validator (pre-publish)
3. Telegram/Discord alerts per SKU
4. Multi-product templates (tee, hoodie, crewneck, poster)
5. Immortal daemon with heartbeat

Queue-based: Drop PNG → 4 SKUs published automatically
"""

import os
import time
import json
import shutil
import requests
from pathlib import Path
from typing import Dict, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

log = get_logger("PRINTIFY-AUTOPUBLISH")

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY", "")
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID", "")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

# Paths
BASE = Path(os.getenv("PRINTIFY_QUEUE_DIR", "/opt/staticwaves_printify/queue"))
PENDING = BASE / "pending"
PUBLISHED = BASE / "published"
FAILED = BASE / "failed"

# API Headers
HEADERS = {
    "Authorization": f"Bearer {PRINTIFY_API_KEY}",
    "Content-Type": "application/json"
}

# ─────────────────────────────────────────────
# Product Templates (Blueprint IDs from Printify)
# ─────────────────────────────────────────────
PRODUCT_TEMPLATES = {
    "tee": {
        "name": "Unisex Heavy Cotton Tee",
        "blueprint_id": 384,
        "provider_id": 1,  # Printify Choice (auto-routing)
        "variant_id": 1,
        "base_cost": 1200,  # $12.00
        "margin": 0.55  # 55% markup
    },
    "hoodie": {
        "name": "Unisex Heavy Blend Hoodie",
        "blueprint_id": 521,
        "provider_id": 1,
        "variant_id": 1,
        "base_cost": 2600,  # $26.00
        "margin": 0.60  # 60% markup
    },
    "crewneck": {
        "name": "Unisex Crewneck Sweatshirt",
        "blueprint_id": 521,
        "provider_id": 1,
        "variant_id": 1,
        "base_cost": 2200,  # $22.00
        "margin": 0.58  # 58% markup
    },
    "poster": {
        "name": "Museum Quality Poster",
        "blueprint_id": 12,
        "provider_id": 1,
        "variant_id": 1,
        "base_cost": 800,  # $8.00
        "margin": 0.65  # 65% markup (high margin, low cost)
    }
}


# ─────────────────────────────────────────────
# 1️⃣ Auto-Pricing Engine
# ─────────────────────────────────────────────
def calc_price(base_cost_cents: int, margin: float = 0.55) -> int:
    """
    Calculate sale price with margin and TikTok-safe rounding.

    Args:
        base_cost_cents: Base cost in cents
        margin: Markup margin (0.55 = 55%)

    Returns:
        Price in cents, rounded to X.99
    """
    raw = base_cost_cents * (1 + margin)
    # Round to nearest $X.99
    rounded = int((raw // 100) * 100 + 99)
    # TikTok minimum safety
    return max(1299, rounded)  # Minimum $12.99


# ─────────────────────────────────────────────
# 2️⃣ TikTok-Safe Validator
# ─────────────────────────────────────────────
def tiktok_validate(payload: Dict) -> None:
    """
    Validate product payload against TikTok Shop rules.

    Raises:
        Exception: If validation fails
    """
    errors = []

    # Variant limit
    if len(payload.get("variants", [])) > 50:
        errors.append("Too many variants (max 50)")

    # Price validation
    for v in payload.get("variants", []):
        if v.get("price", 0) < 500:  # $5.00 minimum
            errors.append("Price too low (min $5.00)")

    # Visibility
    if not payload.get("visible", False):
        errors.append("Product not visible")

    # Title length
    if len(payload.get("title", "")) > 120:
        errors.append("Title too long (max 120 chars)")

    if errors:
        raise Exception(f"TikTok validation failed: {', '.join(errors)}")

    log.debug("✅ TikTok validation passed")


# ─────────────────────────────────────────────
# 3️⃣ Notification System (Telegram/Discord)
# ─────────────────────────────────────────────
def notify(msg: str, level: str = "info") -> None:
    """
    Send notification via Telegram or Discord.

    Args:
        msg: Message to send
        level: Notification level (info, error)
    """
    emoji = "✅" if level == "info" else "❌"
    full_msg = f"{emoji} {msg}"

    try:
        # Discord
        if DISCORD_WEBHOOK_URL:
            requests.post(
                DISCORD_WEBHOOK_URL,
                json={"content": full_msg},
                timeout=5
            )
            log.debug(f"Discord notification sent: {msg}")

        # Telegram
        elif TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(
                url,
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": full_msg
                },
                timeout=5
            )
            log.debug(f"Telegram notification sent: {msg}")

    except Exception as e:
        log.error(f"Notification failed: {e}")


# ─────────────────────────────────────────────
# Image Upload
# ─────────────────────────────────────────────
def upload_image(image_path: Path) -> str:
    """
    Upload image to Printify.

    Args:
        image_path: Path to image file

    Returns:
        Image ID string
    """
    log.info(f"⬆️  Uploading image: {image_path.name}")

    with open(image_path, "rb") as f:
        r = requests.post(
            "https://api.printify.com/v1/uploads/images.json",
            headers={"Authorization": f"Bearer {PRINTIFY_API_KEY}"},
            files={"file": f},
            timeout=60
        )

    r.raise_for_status()
    image_id = r.json()["id"]

    log.info(f"✅ Image uploaded: {image_id}")
    return image_id


# ─────────────────────────────────────────────
# 4️⃣ Multi-Template Publisher
# ─────────────────────────────────────────────
def publish_product(
    image_id: str,
    title: str,
    template_key: str,
    template: Dict
) -> str:
    """
    Publish product to Printify using template.

    Args:
        image_id: Printify image ID
        title: Product title
        template_key: Template key (tee, hoodie, etc.)
        template: Template configuration

    Returns:
        Product ID
    """
    # Calculate price
    price = calc_price(template["base_cost"], template["margin"])

    # Build payload
    payload = {
        "title": f"{title} – {template['name']}",
        "description": "StaticWaves Limited Drop",
        "blueprint_id": template["blueprint_id"],
        "print_provider_id": template["provider_id"],
        "variants": [{
            "id": template["variant_id"],
            "price": price,
            "is_enabled": True
        }],
        "print_areas": [{
            "variant_ids": [template["variant_id"]],
            "placeholders": [{
                "position": "front",
                "images": [{
                    "id": image_id,
                    "x": 0.5,
                    "y": 0.5,
                    "scale": 1,
                    "angle": 0
                }]
            }]
        }],
        "visible": True
    }

    # Validate for TikTok
    tiktok_validate(payload)

    # Publish
    log.info(f"📦 Publishing {template_key}: {payload['title']}")

    r = requests.post(
        f"https://api.printify.com/v1/shops/{PRINTIFY_SHOP_ID}/products.json",
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    r.raise_for_status()
    product_id = r.json()["id"]

    log.info(f"✅ Published {template_key}: {product_id}")

    # Send notification
    notify(f"Published {template_key}: {payload['title']} (${price/100:.2f})")

    return product_id


def publish_all_templates(image_path: Path) -> Dict[str, str]:
    """
    Publish image across all product templates.

    Args:
        image_path: Path to image file

    Returns:
        Dictionary of template_key -> product_id
    """
    log.info(f"🚀 Publishing {image_path.name} across all templates")

    # Upload image once
    image_id = upload_image(image_path)

    # Title from filename
    title = image_path.stem.replace("_", " ").title()

    # Publish to each template
    results = {}

    for template_key, template in PRODUCT_TEMPLATES.items():
        try:
            product_id = publish_product(
                image_id=image_id,
                title=title,
                template_key=template_key,
                template=template
            )
            results[template_key] = product_id

        except Exception as e:
            log.error(f"❌ Failed to publish {template_key}: {e}")
            notify(f"Failed {template_key}: {e}", level="error")
            results[template_key] = None

    return results


# ─────────────────────────────────────────────
# Queue Processor
# ─────────────────────────────────────────────
def process_queue() -> bool:
    """
    Process all images in pending queue.

    Returns:
        True if work was done, False if queue empty
    """
    # Create queue directories if needed
    for d in (PENDING, PUBLISHED, FAILED):
        d.mkdir(parents=True, exist_ok=True)

    # Find pending images
    images = list(PENDING.glob("*.png")) + list(PENDING.glob("*.jpg"))

    if not images:
        return False

    log.info(f"📥 Processing {len(images)} image(s)")

    for img in images:
        try:
            # Publish across all templates
            results = publish_all_templates(img)

            # Check if any succeeded
            successes = [k for k, v in results.items() if v is not None]

            if successes:
                log.info(f"✅ Published {len(successes)} products from {img.name}")
                shutil.move(str(img), PUBLISHED / img.name)
            else:
                log.error(f"❌ All templates failed for {img.name}")
                shutil.move(str(img), FAILED / img.name)

        except Exception as e:
            log.error(f"❌ Fatal error processing {img.name}: {e}")
            notify(f"Fatal error: {img.name} - {e}", level="error")
            shutil.move(str(img), FAILED / img.name)

    return True


# ─────────────────────────────────────────────
# 5️⃣ Main Daemon Loop (Immortal)
# ─────────────────────────────────────────────
def run_daemon():
    """
    Main daemon loop - never exits.
    """
    log.info("🚀 StaticWaves Printify Autopublisher daemon started")

    # Validate config
    if not PRINTIFY_API_KEY or not PRINTIFY_SHOP_ID:
        raise RuntimeError("Missing PRINTIFY_API_KEY or PRINTIFY_SHOP_ID")

    notify("🚀 Printify Autopublisher started")

    while True:
        try:
            worked = process_queue()

            if worked:
                log.info("❤️ heartbeat: publish cycle complete")
            else:
                log.debug("❤️ heartbeat: alive, queue empty")

            time.sleep(60)

        except Exception as e:
            log.error(f"🔥 FATAL LOOP ERROR: {e}")
            notify(f"🔥 Engine error: {e}", level="error")
            time.sleep(30)


if __name__ == "__main__":
    run_daemon()

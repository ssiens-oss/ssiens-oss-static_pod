#!/usr/bin/env python3
"""
TikTok Shop Feed Generator
Creates XLSX/CSV feeds for TikTok Shop bulk upload
"""
import sys
import uuid
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.logger import setup_logger

log = setup_logger("TIKTOK-FEED", "logs/tiktok_feed.log")

# Configuration
PRODUCTS_DIR = Path("queues/published")
OUT_DIR = Path("exports")
BASE_PRICE = 49.99
INVENTORY = 999
CATEGORY = "Apparel & Accessories > Clothing > Hoodies"
BRAND = "StaticWaves"

def generate_feed():
    """Generate TikTok Shop product feed"""

    OUT_DIR.mkdir(exist_ok=True)
    rows = []

    # Process all product images
    for img in PRODUCTS_DIR.glob("*.png"):
        sku = f"SW-{uuid.uuid4().hex[:8].upper()}"

        rows.append({
            "product_name": f"StaticWaves Hoodie – {img.stem}",
            "description": "Premium StaticWaves hoodie. Limited drop.",
            "price": int(BASE_PRICE),
            "quantity": INVENTORY,
            "sku": sku,
            "image_url": f"https://cdn.staticwaves.ai/{img.name}",
            "category": CATEGORY,
            "shipping_weight": "0.5",
            "brand": BRAND,
            "condition": "New"
        })

    if not rows:
        log.warning("No products found to export")
        return

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Export XLSX and CSV
    xlsx_path = OUT_DIR / "tiktok_shop_feed.xlsx"
    csv_path = OUT_DIR / "tiktok_shop_feed.csv"

    df.to_excel(xlsx_path, index=False)
    df.to_csv(csv_path, index=False)

    log.info(f"✅ Generated {len(rows)} products")
    log.info(f"📁 XLSX: {xlsx_path}")
    log.info(f"📁 CSV: {csv_path}")

if __name__ == "__main__":
    generate_feed()

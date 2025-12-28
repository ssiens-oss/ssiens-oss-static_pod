"""
TikTok Product Feed Generator
==============================
Automated XLSX + CSV feed generation from POD design queue.

Scans published design assets and generates TikTok-optimized
product feeds with:
- Price A/B bucket assignment
- SKU generation
- Category mapping
- Image URL resolution
- Multi-format export (XLSX + CSV)

Usage:
    python tools/tiktok_feed_generator.py
    python tools/tiktok_feed_generator.py --source queues/published --output exports
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import uuid
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pandas as pd
except ImportError:
    print("❌ pandas not installed. Run: pip install pandas openpyxl")
    sys.exit(1)

from tools.tiktok_price_ab import choose_price
from tools.tiktok_variant_expander import expand_variants, get_safe_mode_status
from tools.tiktok_firewall import apply_firewall_to_feed
from core.logger import get_logger, log_performance

log = get_logger("FEED-GENERATOR")

# Configuration
DEFAULT_SOURCE_DIR = Path("queues/published")
DEFAULT_OUTPUT_DIR = Path("exports")
CDN_BASE_URL = os.getenv("CDN_BASE_URL", "https://cdn.staticwaves.ai")
BRAND_NAME = os.getenv("BRAND_NAME", "StaticWaves")

# TikTok category mapping (US market)
CATEGORIES = {
    "hoodie": "Apparel & Accessories > Clothing > Hoodies & Sweatshirts",
    "tshirt": "Apparel & Accessories > Clothing > Shirts & Tops",
    "tee": "Apparel & Accessories > Clothing > Shirts & Tops",
    "sweatshirt": "Apparel & Accessories > Clothing > Hoodies & Sweatshirts",
    "tank": "Apparel & Accessories > Clothing > Shirts & Tops",
    "longsleeve": "Apparel & Accessories > Clothing > Shirts & Tops",
}


def detect_category(filename: str) -> str:
    """
    Auto-detect TikTok category from filename.

    Args:
        filename: Design filename

    Returns:
        TikTok product category path

    Example:
        >>> detect_category("glitch-hoodie-v2.png")
        "Apparel & Accessories > Clothing > Hoodies & Sweatshirts"
    """
    filename_lower = filename.lower()

    for keyword, category in CATEGORIES.items():
        if keyword in filename_lower:
            return category

    # Default fallback
    return "Apparel & Accessories > Clothing > Shirts & Tops"


def generate_product_title(filename: str) -> str:
    """
    Generate TikTok-optimized product title.

    TikTok's algorithm favors:
    - Brand name first
    - Product type
    - Key descriptors
    - Under 60 characters

    Args:
        filename: Design filename

    Returns:
        Optimized product title

    Example:
        >>> generate_product_title("glitch-wave-001.png")
        "StaticWaves Glitch Wave Hoodie"
    """
    # Extract base name without extension
    base_name = Path(filename).stem

    # Clean up filename artifacts
    clean_name = (
        base_name
        .replace("-", " ")
        .replace("_", " ")
        .title()
    )

    # Detect product type
    product_type = "Hoodie"  # Default
    if "tee" in base_name.lower() or "tshirt" in base_name.lower():
        product_type = "T-Shirt"
    elif "tank" in base_name.lower():
        product_type = "Tank Top"
    elif "sweatshirt" in base_name.lower():
        product_type = "Sweatshirt"

    return f"{BRAND_NAME} {clean_name} {product_type}"[:60]


def generate_description(title: str) -> str:
    """
    Generate TikTok-optimized product description.

    TikTok favors:
    - Under 500 characters
    - Benefit-focused (not feature-focused)
    - Call to action
    - Emojis (sparingly)

    Args:
        title: Product title

    Returns:
        Optimized description
    """
    descriptions = [
        f"{title} - Premium print-on-demand streetwear. "
        "Made to order with eco-friendly inks. "
        "Express yourself with bold, unique designs. "
        "Perfect for casual wear, gifts, or making a statement. "
        "TikTok exclusive. Limited availability. Ships worldwide.",

        f"Premium {title.split()[-1].lower()} featuring exclusive {BRAND_NAME} design. "
        "High-quality print that won't fade or crack. "
        "Comfortable, breathable fabric for all-day wear. "
        "Stand out from the crowd with unique streetwear. "
        "Order now - made fresh just for you.",
    ]

    import random
    return random.choice(descriptions)


@log_performance(log, "feed_generation")
def generate_feed(
    source_dir: Path,
    output_dir: Path,
    price_tier: str = "standard"
) -> Dict[str, Any]:
    """
    Generate TikTok product feed from design assets.

    Args:
        source_dir: Directory containing published designs
        output_dir: Directory for XLSX/CSV output
        price_tier: Price tier (standard/premium/budget)

    Returns:
        Dictionary with generation stats

    Example:
        >>> generate_feed(Path("queues/published"), Path("exports"))
        {"products_generated": 42, "xlsx_path": "exports/tiktok_feed.xlsx"}
    """
    # Ensure directories exist
    source_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find design assets
    design_files = list(source_dir.glob("*.png")) + list(source_dir.glob("*.jpg"))

    if not design_files:
        log.warning(f"⚠️  No design files found in {source_dir}")
        log.info("💡 Add PNG/JPG files to queues/published/ directory")
        return {
            "products_generated": 0,
            "xlsx_path": None,
            "csv_path": None
        }

    log.info(f"📁 Found {len(design_files)} design files")

    # Generate product rows
    products = []

    for design_file in design_files:
        # Generate unique SKU
        sku = f"SW-{uuid.uuid4().hex[:8].upper()}"

        # Price selection
        price = choose_price(price_tier)

        # Product details
        title = generate_product_title(design_file.name)
        description = generate_description(title)
        category = detect_category(design_file.name)
        image_url = f"{CDN_BASE_URL}/{design_file.name}"

        # Get variants (SAFE MODE aware)
        variants = expand_variants(price, sku)

        # Base product
        product = {
            "product_name": title,
            "description": description,
            "price": price,
            "quantity": 999,
            "sku": sku,
            "image_url": image_url,
            "category": category,
            "shipping_weight": "0.5",
            "brand": BRAND_NAME,
            "condition": "New",
            "shipping_time": "5-7 business days",
            "material": "Cotton/Polyester Blend",
            "care_instructions": "Machine wash cold, tumble dry low",
            "made_in": "USA",
            "tags": "streetwear,pod,custom,unique,tiktok-exclusive",
            "variants": variants
        }

        products.append(product)

    # Apply inventory firewall
    log.info("🛡️  Applying inventory firewall")
    protected_products = apply_firewall_to_feed(products)

    # Flatten for CSV/XLSX (single variant per row in SAFE MODE)
    safe_mode_status = get_safe_mode_status()
    log.info(
        f"⚙️  Safe Mode: {'ENABLED' if safe_mode_status['safe_mode_enabled'] else 'DISABLED'}"
    )

    rows = []
    for product in protected_products:
        # In SAFE MODE, one row per product
        # In FULL MODE, one row per variant
        if safe_mode_status['safe_mode_enabled']:
            rows.append({
                "product_name": product["product_name"],
                "description": product["description"],
                "price": product["price"],
                "quantity": product["quantity"],
                "sku": product["sku"],
                "image_url": product["image_url"],
                "category": product["category"],
                "shipping_weight": product["shipping_weight"],
                "brand": product["brand"],
                "condition": product["condition"],
                "shipping_time": product.get("shipping_time", "5-7 business days"),
                "material": product.get("material", "Cotton Blend"),
                "tags": product.get("tags", ""),
            })
        else:
            # Expand variants into separate rows
            for variant in product.get("variants", []):
                rows.append({
                    "product_name": f"{product['product_name']} - {variant['variant_name']}",
                    "description": product["description"],
                    "price": variant["price"],
                    "quantity": variant["quantity"],
                    "sku": variant["variant_sku"],
                    "variant_name": variant["variant_name"],
                    "image_url": product["image_url"],
                    "category": product["category"],
                    "shipping_weight": product["shipping_weight"],
                    "brand": product["brand"],
                    "condition": product["condition"],
                    "shipping_time": product.get("shipping_time", "5-7 business days"),
                    "material": product.get("material", "Cotton Blend"),
                    "tags": product.get("tags", ""),
                })

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Export to XLSX
    xlsx_path = output_dir / "tiktok_feed.xlsx"
    df.to_excel(xlsx_path, index=False, engine='openpyxl')
    log.info(f"✅ XLSX exported: {xlsx_path}")

    # Export to CSV
    csv_path = output_dir / "tiktok_feed.csv"
    df.to_csv(csv_path, index=False)
    log.info(f"✅ CSV exported: {csv_path}")

    return {
        "products_generated": len(products),
        "rows_exported": len(rows),
        "xlsx_path": str(xlsx_path),
        "csv_path": str(csv_path),
        "safe_mode": safe_mode_status['safe_mode_enabled']
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate TikTok product feeds from POD designs"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="Source directory for designs"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for feeds"
    )
    parser.add_argument(
        "--tier",
        choices=["standard", "premium", "budget"],
        default="standard",
        help="Price tier"
    )

    args = parser.parse_args()

    log.info("🚀 TikTok Feed Generator v2")
    log.info("=" * 60)

    result = generate_feed(args.source, args.output, args.tier)

    log.info("=" * 60)
    log.info(f"📦 Products Generated: {result['products_generated']}")
    log.info(f"📊 Rows Exported: {result['rows_exported']}")
    log.info(f"🛡️  Safe Mode: {result['safe_mode']}")

    if result['products_generated'] > 0:
        log.info(f"📁 XLSX: {result['xlsx_path']}")
        log.info(f"📁 CSV: {result['csv_path']}")
        log.info("✅ Feed generation complete!")
    else:
        log.warning("⚠️  No products generated. Check source directory.")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
TikTok Variant Expansion Engine
================================
Safe multi-size variant generation with TikTok API compliance.

CRITICAL: TikTok penalizes new seller accounts for complex variant matrices.
SAFE MODE defaults to single-variant listings until account reputation matures.

Disable SAFE MODE only after:
- 30+ days of selling history
- 50+ completed orders
- 4.5+ seller rating
- Zero policy violations
"""

import os
from typing import List, Dict, Any

# TikTok Safe Mode (prevents account flags on new accounts)
SAFE_MODE = os.getenv("TIKTOK_SAFE_MODE", "1") == "1"

# Standard apparel sizes (US market)
SIZES = ["S", "M", "L", "XL", "2XL"]

# Extended sizes (activate when SAFE_MODE=0)
EXTENDED_SIZES = ["XS", "S", "M", "L", "XL", "2XL", "3XL"]

# Size-based price adjustments (USD)
SIZE_PRICE_DELTA = {
    "XS": 0,
    "S": 0,
    "M": 0,
    "L": 0,
    "XL": 3,
    "2XL": 5,
    "3XL": 7
}


def expand_variants(
    base_price: int,
    base_sku: str = "",
    use_extended: bool = False,
    custom_sizes: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Generate size variants with TikTok-safe defaults.

    Args:
        base_price: Base product price in USD
        base_sku: Optional SKU prefix for variants
        use_extended: Use extended size range (ignored if SAFE_MODE=1)
        custom_sizes: Override default size list

    Returns:
        List of variant dictionaries ready for TikTok API

    Behavior:
        - SAFE_MODE=1: Returns single "One Size" variant
        - SAFE_MODE=0: Returns full size matrix with price adjustments

    Example:
        >>> expand_variants(49, "SW-HOODIE")
        [{"variant_name": "One Size", "price": 49, "quantity": 999, ...}]
    """

    # SAFE MODE: Single variant only (TikTok new account protection)
    if SAFE_MODE:
        return [{
            "variant_name": "One Size",
            "variant_sku": f"{base_sku}-OS" if base_sku else "OS",
            "price": base_price,
            "quantity": 999,
            "inventory_policy": "deny",
            "fulfillment_service": "manual",
            "requires_shipping": True,
            "taxable": True,
            "barcode": "",
            "weight": 500,  # grams
            "weight_unit": "g"
        }]

    # FULL MODE: Multi-variant expansion
    size_list = custom_sizes or (EXTENDED_SIZES if use_extended else SIZES)
    variants = []

    for size in size_list:
        price_adjustment = SIZE_PRICE_DELTA.get(size, 0)
        variant_price = base_price + price_adjustment

        variants.append({
            "variant_name": size,
            "variant_sku": f"{base_sku}-{size}" if base_sku else size,
            "price": variant_price,
            "quantity": 999,
            "inventory_policy": "deny",
            "fulfillment_service": "manual",
            "requires_shipping": True,
            "taxable": True,
            "barcode": "",
            "weight": 500,
            "weight_unit": "g",
            "size": size
        })

    return variants


def get_safe_mode_status() -> Dict[str, Any]:
    """
    Check current TikTok Safe Mode configuration.

    Returns:
        Dictionary with mode status and recommendations
    """
    return {
        "safe_mode_enabled": SAFE_MODE,
        "variant_count": 1 if SAFE_MODE else len(SIZES),
        "recommendation": (
            "SAFE MODE ACTIVE - Single variant only. "
            "Disable after 30+ days selling history."
        ) if SAFE_MODE else (
            "FULL MODE ACTIVE - Multi-variant enabled. "
            "Monitor account health metrics."
        ),
        "risk_level": "LOW" if SAFE_MODE else "MEDIUM"
    }


def toggle_safe_mode(enable: bool) -> bool:
    """
    Programmatically toggle SAFE MODE.

    Note: This modifies environment variable for current process only.
    For persistent changes, update .env file.

    Args:
        enable: True to enable SAFE MODE, False to disable

    Returns:
        New SAFE MODE state
    """
    global SAFE_MODE
    os.environ["TIKTOK_SAFE_MODE"] = "1" if enable else "0"
    SAFE_MODE = enable
    return SAFE_MODE


if __name__ == "__main__":
    print("🛡️ TikTok Variant Expander Test")
    print("=" * 60)

    status = get_safe_mode_status()
    print(f"\n⚙️  Safe Mode: {'ENABLED' if status['safe_mode_enabled'] else 'DISABLED'}")
    print(f"📦 Variant Count: {status['variant_count']}")
    print(f"💡 Recommendation: {status['recommendation']}")

    print("\n📋 SAFE MODE Variants (base=$49):")
    safe_variants = expand_variants(49, "SW-TEST")
    for v in safe_variants:
        print(f"  {v['variant_name']:10} ${v['price']} | SKU: {v['variant_sku']}")

    print("\n📋 FULL MODE Simulation (SAFE_MODE=0):")
    os.environ["TIKTOK_SAFE_MODE"] = "0"
    full_variants = expand_variants(49, "SW-TEST", use_extended=False)
    for v in full_variants:
        print(f"  {v['variant_name']:10} ${v['price']} | SKU: {v['variant_sku']}")

    print("\n📋 EXTENDED Size Range:")
    extended_variants = expand_variants(49, "SW-TEST", use_extended=True)
    for v in extended_variants:
        print(f"  {v['variant_name']:10} ${v['price']} | SKU: {v['variant_sku']}")

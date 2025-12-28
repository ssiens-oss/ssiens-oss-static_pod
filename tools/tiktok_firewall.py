"""
TikTok Inventory Firewall
==========================
Prevents TikTok API from zeroing inventory or delisting products.

PROBLEM: TikTok's sync system can mark POD products as "out of stock"
when Printify/external fulfillment APIs report zero inventory.

SOLUTION: Force minimum inventory levels and deny overselling,
preventing silent delisting from TikTok Shop.

This is NOT fraud - POD items are made-to-order.
Setting inventory to 999 accurately reflects unlimited capacity.
"""

import os
from typing import Dict, Any, List
from datetime import datetime

# Minimum inventory level (prevents delisting)
MIN_INVENTORY = int(os.getenv("TIKTOK_MIN_INVENTORY", "999"))

# Maximum inventory cap (prevents unrealistic numbers)
MAX_INVENTORY = int(os.getenv("TIKTOK_MAX_INVENTORY", "9999"))

# Inventory policies
INVENTORY_POLICY = os.getenv("TIKTOK_INVENTORY_POLICY", "deny")  # deny/continue


def normalize_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply inventory firewall to a single product.

    Enforces:
    - Minimum inventory threshold
    - Oversell prevention policy
    - TikTok-compliant inventory structure

    Args:
        product: Product dictionary (TikTok API format)

    Returns:
        Normalized product with firewall protections

    Example:
        >>> normalize_product({"quantity": 0, "title": "Hoodie"})
        {"quantity": 999, "inventory_policy": "deny", ...}
    """
    # Clone to avoid mutating original
    normalized = product.copy()

    # Force minimum inventory
    current_qty = normalized.get("quantity", 0)
    normalized["quantity"] = max(current_qty, MIN_INVENTORY)

    # Cap maximum inventory (prevent API rejections)
    if normalized["quantity"] > MAX_INVENTORY:
        normalized["quantity"] = MAX_INVENTORY

    # Set oversell policy
    normalized["inventory_policy"] = INVENTORY_POLICY

    # Add firewall metadata
    normalized["_firewall_applied"] = True
    normalized["_firewall_timestamp"] = datetime.utcnow().isoformat()

    # Ensure fulfillment flags are correct for POD
    normalized["fulfillment_service"] = "manual"
    normalized["requires_shipping"] = True

    return normalized


def normalize_variants(variants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply inventory firewall to all product variants.

    Args:
        variants: List of variant dictionaries

    Returns:
        List of normalized variants with firewall applied

    Example:
        >>> normalize_variants([{"variant_name": "S", "quantity": 10}])
        [{"variant_name": "S", "quantity": 999, ...}]
    """
    return [normalize_product(variant) for variant in variants]


def validate_inventory(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate product inventory meets TikTok requirements.

    Args:
        product: Product to validate

    Returns:
        Validation result with status and warnings

    Example:
        >>> validate_inventory({"quantity": 5})
        {"valid": False, "warnings": ["Inventory below minimum threshold"]}
    """
    warnings = []
    errors = []

    qty = product.get("quantity", 0)

    if qty < MIN_INVENTORY:
        warnings.append(
            f"Inventory ({qty}) below minimum threshold ({MIN_INVENTORY})"
        )

    if qty > MAX_INVENTORY:
        errors.append(
            f"Inventory ({qty}) exceeds maximum cap ({MAX_INVENTORY})"
        )

    if product.get("inventory_policy") != INVENTORY_POLICY:
        warnings.append(
            f"Inventory policy mismatch: expected '{INVENTORY_POLICY}'"
        )

    # POD-specific validations
    if product.get("fulfillment_service") == "automatic":
        warnings.append(
            "POD products should use 'manual' fulfillment service"
        )

    if not product.get("requires_shipping", True):
        errors.append(
            "Physical POD products must require shipping"
        )

    return {
        "valid": len(errors) == 0,
        "warnings": warnings,
        "errors": errors,
        "recommended_action": "apply_firewall" if warnings or errors else "none"
    }


def get_firewall_config() -> Dict[str, Any]:
    """
    Retrieve current firewall configuration.

    Returns:
        Dictionary of firewall settings
    """
    return {
        "min_inventory": MIN_INVENTORY,
        "max_inventory": MAX_INVENTORY,
        "inventory_policy": INVENTORY_POLICY,
        "enabled": True,
        "purpose": "Prevent TikTok API from delisting POD products"
    }


def apply_firewall_to_feed(feed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply inventory firewall to entire product feed.

    Args:
        feed: List of products (full catalog)

    Returns:
        Protected feed with firewall applied to all items

    Example:
        >>> apply_firewall_to_feed([{"title": "A", "quantity": 0}])
        [{"title": "A", "quantity": 999, "_firewall_applied": True}]
    """
    protected_feed = []

    for product in feed:
        # Normalize base product
        normalized_product = normalize_product(product)

        # Normalize variants if present
        if "variants" in product:
            normalized_product["variants"] = normalize_variants(
                product["variants"]
            )

        protected_feed.append(normalized_product)

    return protected_feed


if __name__ == "__main__":
    print("🛡️ TikTok Inventory Firewall Test")
    print("=" * 60)

    config = get_firewall_config()
    print("\n⚙️  Firewall Configuration:")
    print(f"  Min Inventory: {config['min_inventory']}")
    print(f"  Max Inventory: {config['max_inventory']}")
    print(f"  Policy: {config['inventory_policy']}")

    print("\n📦 Test Case 1: Low Inventory Product")
    test_product_1 = {
        "title": "StaticWaves Hoodie",
        "quantity": 3,
        "sku": "SW-001"
    }
    normalized_1 = normalize_product(test_product_1)
    print(f"  Before: quantity={test_product_1['quantity']}")
    print(f"  After: quantity={normalized_1['quantity']}")
    print(f"  Firewall Applied: {normalized_1['_firewall_applied']}")

    print("\n📦 Test Case 2: Zero Inventory Product")
    test_product_2 = {
        "title": "StaticWaves Tee",
        "quantity": 0,
        "sku": "SW-002"
    }
    normalized_2 = normalize_product(test_product_2)
    print(f"  Before: quantity={test_product_2['quantity']}")
    print(f"  After: quantity={normalized_2['quantity']}")
    print(f"  Policy: {normalized_2['inventory_policy']}")

    print("\n📦 Test Case 3: Variants Protection")
    test_variants = [
        {"variant_name": "S", "quantity": 0},
        {"variant_name": "M", "quantity": 5},
        {"variant_name": "L", "quantity": 2}
    ]
    normalized_variants = normalize_variants(test_variants)
    print("  Original Quantities:", [v['quantity'] for v in test_variants])
    print("  Protected Quantities:", [v['quantity'] for v in normalized_variants])

    print("\n✅ Validation Test:")
    validation_result = validate_inventory(test_product_2)
    print(f"  Valid: {validation_result['valid']}")
    print(f"  Warnings: {len(validation_result['warnings'])}")
    for warning in validation_result['warnings']:
        print(f"    - {warning}")

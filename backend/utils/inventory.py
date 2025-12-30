"""
Inventory Utilities
Normalize inventory quantities across platforms
"""
from typing import Union
from loguru import logger


def normalize_inventory(
    quantity: Union[int, str, None],
    max_value: int = 9999,
    default: int = 100,
) -> int:
    """
    Normalize inventory quantity to safe values for all platforms

    Handles common issues:
    - Printify's 999999999 (unlimited stock)
    - Missing/None values
    - String values
    - Negative values

    Args:
        quantity: Raw inventory quantity from supplier
        max_value: Maximum allowed value (default: 9999 for TikTok)
        default: Default value if quantity is invalid

    Returns:
        Normalized integer quantity
    """
    try:
        # Handle None/empty
        if quantity is None or quantity == "":
            logger.warning(f"Empty inventory quantity, using default: {default}")
            return default

        # Convert to int
        qty = int(quantity)

        # Handle negative
        if qty < 0:
            logger.warning(f"Negative inventory ({qty}), using 0")
            return 0

        # Handle unlimited/very large (Printify's 999999999)
        if qty >= 100000:  # Anything over 100k is probably "unlimited"
            logger.info(f"Large inventory ({qty:,}) detected, capping at {max_value}")
            return max_value

        # Handle exceeds max
        if qty > max_value:
            logger.warning(f"Inventory ({qty}) exceeds max ({max_value}), capping")
            return max_value

        # Valid quantity
        return qty

    except (ValueError, TypeError) as e:
        logger.error(f"Invalid inventory quantity '{quantity}': {e}, using default: {default}")
        return default


def get_platform_max_inventory(platform: str) -> int:
    """
    Get maximum inventory for specific platform

    Platform limits:
    - TikTok Shop: 9,999 (hard limit)
    - Shopify: No limit, but recommend 9,999 for consistency
    - Amazon: 999,999
    - Facebook/Instagram: 100,000

    Args:
        platform: Platform name (tiktok, shopify, amazon, meta)

    Returns:
        Maximum inventory quantity for platform
    """
    limits = {
        "tiktok": 9999,
        "shopify": 9999,  # Match TikTok for consistency
        "amazon": 999999,
        "meta": 100000,
        "facebook": 100000,
        "instagram": 100000,
    }

    return limits.get(platform.lower(), 9999)  # Default to TikTok limit


def normalize_for_platform(quantity: Union[int, str, None], platform: str) -> int:
    """
    Normalize inventory for specific platform

    Args:
        quantity: Raw inventory quantity
        platform: Target platform

    Returns:
        Normalized quantity for platform
    """
    max_value = get_platform_max_inventory(platform)
    return normalize_inventory(quantity, max_value=max_value)


# Platform-specific normalization shortcuts
def normalize_for_tiktok(quantity: Union[int, str, None]) -> int:
    """Normalize for TikTok Shop (max: 9,999)"""
    return normalize_inventory(quantity, max_value=9999)


def normalize_for_shopify(quantity: Union[int, str, None]) -> int:
    """Normalize for Shopify (recommended max: 9,999)"""
    return normalize_inventory(quantity, max_value=9999)


def normalize_for_printify(quantity: Union[int, str, None]) -> int:
    """
    Normalize Printify inventory
    Printify uses 999999999 for unlimited stock
    """
    if quantity and int(quantity) >= 999999999:
        logger.info("Printify unlimited stock detected, setting to 9,999")
        return 9999

    return normalize_inventory(quantity, max_value=9999)


# Batch normalization
def normalize_variants(variants: list, platform: str = "shopify") -> list:
    """
    Normalize inventory for all variants in a product

    Args:
        variants: List of variant dicts with inventory_quantity
        platform: Target platform

    Returns:
        Variants with normalized inventory
    """
    for variant in variants:
        if "inventory_quantity" in variant:
            original = variant["inventory_quantity"]
            normalized = normalize_for_platform(original, platform)

            if original != normalized:
                logger.info(
                    f"Normalized variant inventory: {original:,} → {normalized:,}"
                )

            variant["inventory_quantity"] = normalized

    return variants


# Example usage and tests
if __name__ == "__main__":
    # Test cases
    test_cases = [
        (999999999, "Printify unlimited"),
        (100000, "Large stock"),
        (5000, "Normal stock"),
        (0, "Out of stock"),
        (-10, "Negative"),
        (None, "None value"),
        ("", "Empty string"),
        ("500", "String number"),
    ]

    print("\n" + "="*60)
    print("INVENTORY NORMALIZATION TESTS")
    print("="*60 + "\n")

    for value, description in test_cases:
        normalized = normalize_inventory(value)
        print(f"{description:20} | {str(value):12} → {normalized:5}")

    print("\n" + "="*60)
    print("PLATFORM-SPECIFIC NORMALIZATION")
    print("="*60 + "\n")

    platforms = ["tiktok", "shopify", "amazon", "meta"]
    test_value = 999999999

    for platform in platforms:
        normalized = normalize_for_platform(test_value, platform)
        print(f"{platform:10} | {test_value:,} → {normalized:,}")

    print("\n" + "="*60)

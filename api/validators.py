"""
TikTok-Safe Product Validators
Critical validation rules for marketplace compliance
"""

import re
from pathlib import Path

def validate_product(product_data):
    """
    Validate product data before publication

    Raises:
        ValueError: If validation fails
    """

    # Title validation
    validate_title(product_data.get("title"))

    # Description validation
    validate_description(product_data.get("description", ""))

    # Inventory validation
    validate_inventory(product_data.get("inventory", 0))

    # Image validation
    if "image" in product_data:
        validate_image(product_data["image"])

    # Price validation
    if "price" in product_data:
        validate_price(product_data["price"])

    # Type validation
    validate_product_type(product_data.get("type"))

    return True

def validate_title(title):
    """
    TikTok Shop title requirements:
    - Must exist
    - Max 60 characters
    - No special prohibited words
    """
    if not title:
        raise ValueError("Product title is required")

    if len(title) > 60:
        raise ValueError(f"Title too long: {len(title)} chars (max 60)")

    # Prohibited words (example list)
    prohibited = ["free", "giveaway", "replica", "fake"]
    title_lower = title.lower()

    for word in prohibited:
        if word in title_lower:
            raise ValueError(f"Prohibited word in title: '{word}'")

    return True

def validate_description(description):
    """
    Description validation
    - Max 5000 characters
    - No prohibited content
    """
    if len(description) > 5000:
        raise ValueError(f"Description too long: {len(description)} chars (max 5000)")

    return True

def validate_inventory(inventory):
    """
    Inventory must be positive integer
    """
    if not isinstance(inventory, int) or inventory < 0:
        raise ValueError(f"Invalid inventory: {inventory} (must be positive integer)")

    if inventory == 0:
        raise ValueError("Inventory cannot be zero")

    return True

def validate_image(image_path):
    """
    Image validation:
    - Must be PNG or JPG
    - Must exist (if path provided)
    """
    valid_extensions = [".png", ".jpg", ".jpeg"]

    if isinstance(image_path, str):
        path = Path(image_path)

        if not any(image_path.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"Invalid image format: {image_path} (must be PNG or JPG)")

    return True

def validate_price(price):
    """
    Price validation:
    - Must be positive number
    - Reasonable range ($5 - $500)
    """
    if not isinstance(price, (int, float)) or price <= 0:
        raise ValueError(f"Invalid price: {price} (must be positive number)")

    if price < 5.00:
        raise ValueError(f"Price too low: ${price} (minimum $5.00)")

    if price > 500.00:
        raise ValueError(f"Price too high: ${price} (maximum $500.00)")

    return True

def validate_product_type(product_type):
    """
    Validate product type is supported
    """
    valid_types = ["hoodie", "tee", "poster", "mug", "tank", "sweatshirt"]

    if not product_type:
        raise ValueError("Product type is required")

    if product_type.lower() not in valid_types:
        raise ValueError(f"Invalid product type: {product_type} (valid: {', '.join(valid_types)})")

    return True

def validate_tiktok_compliance(product_data):
    """
    TikTok Shop specific compliance checks
    """

    # Check for banned categories
    banned_categories = ["weapons", "drugs", "tobacco", "adult"]
    category = product_data.get("category", "").lower()

    if any(banned in category for banned in banned_categories):
        raise ValueError(f"Banned category: {category}")

    # Check brand compliance (no trademark violations)
    title = product_data.get("title", "").lower()
    description = product_data.get("description", "").lower()

    # Protected brands (example list - expand in production)
    protected_brands = ["nike", "adidas", "supreme", "gucci", "louis vuitton"]

    for brand in protected_brands:
        if brand in title or brand in description:
            raise ValueError(f"Potential trademark violation: '{brand}'")

    return True

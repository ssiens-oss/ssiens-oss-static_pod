"""
Input Validation Utilities

Centralized validation functions for API inputs.
"""
import os
import re
from typing import Tuple

from PIL import Image


def validate_image_id(image_id: str) -> Tuple[bool, str]:
    """
    Validate image ID format.

    Args:
        image_id: Image identifier to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not image_id:
        return False, "Image ID is required"

    # Allow alphanumeric, hyphens, underscores (prevent path traversal)
    if not re.match(r'^[a-zA-Z0-9_-]+$', image_id):
        return False, "Invalid image ID format"

    if len(image_id) > 255:
        return False, "Image ID too long"

    return True, ""


def validate_title(title: str) -> Tuple[bool, str]:
    """
    Validate product title.

    Args:
        title: Product title to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not title:
        return False, "Title is required"

    if len(title) < 3:
        return False, "Title must be at least 3 characters"

    if len(title) > 200:
        return False, "Title must be less than 200 characters"

    # Check for suspicious patterns (basic XSS prevention)
    if re.search(r'[<>\"\'`]', title):
        return False, "Title contains invalid characters"

    return True, ""


def validate_image_file(image_path: str) -> Tuple[bool, str]:
    """
    Validate image file exists and is a valid image.

    Args:
        image_path: Path to image file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(image_path):
        return False, "Image file not found"

    # Check file size (max 20MB)
    file_size = os.path.getsize(image_path)
    max_size = 20 * 1024 * 1024  # 20MB
    if file_size > max_size:
        return False, f"Image file too large (max {max_size / 1024 / 1024}MB)"

    # Verify it's a valid image using Pillow
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True, ""
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


def validate_positive_int(value: int, name: str, min_val: int = 1) -> Tuple[bool, str]:
    """
    Validate a positive integer.

    Args:
        value: Value to validate
        name: Field name for error messages
        min_val: Minimum allowed value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, int):
        return False, f"{name} must be an integer"
    if value < min_val:
        return False, f"{name} must be at least {min_val}"
    return True, ""


def validate_price(price_cents: int) -> Tuple[bool, str]:
    """
    Validate price in cents.

    Args:
        price_cents: Price in cents

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(price_cents, int):
        return False, "Price must be an integer"
    if price_cents < 0:
        return False, "Price cannot be negative"
    if price_cents > 99999999:  # $999,999.99 max
        return False, "Price exceeds maximum allowed"
    return True, ""

"""
TikTok Appeal-Safe Listing Generator

Generates product descriptions that comply with TikTok Shop policies:
- No exaggerated claims
- No urgency triggers
- No guarantee language
- Professional, factual descriptions

Safe for audits, reviews, and appeals.
"""

from typing import List
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

log = get_logger("APPEAL-SAFE-COPY")

# Pre-approved safe phrases
SAFE_PHRASES = [
    "Premium quality apparel",
    "Comfort-focused design",
    "Unique graphic style",
    "Limited production run",
    "Everyday wear",
    "Carefully crafted materials",
    "Contemporary design",
    "Versatile styling",
    "Durable construction",
    "Classic fit"
]

# Banned phrases that trigger reviews
BANNED = [
    "guaranteed",
    "guarantee",
    "viral",
    "best seller",
    "bestseller",
    "limited time only",
    "act now",
    "don't miss out",
    "once in a lifetime",
    "exclusive deal",
    "special offer",
    "hurry",
    "last chance",
    "selling fast",
    "going viral",
    "trending now",
    "#1 seller",
    "most popular",
    "everyone is buying",
    "you won't believe",
    "insane deal",
    "crazy price",
    "unbelievable"
]


def generate(name: str, product_type: str = "hoodie", features: List[str] = None) -> str:
    """
    Generate an appeal-safe product description.

    Args:
        name: Product name/title
        product_type: Type of product (hoodie, t-shirt, etc.)
        features: Optional list of specific product features

    Returns:
        Policy-compliant description
    """
    if features is None:
        features = ["unique graphic style", "carefully produced materials"]

    feature_text = " and ".join(features)

    desc = (
        f"{name} is a premium-quality {product_type} designed for comfort "
        f"and everyday wear. Featuring {feature_text}. "
        f"Contemporary design with durable construction."
    )

    # Remove any banned phrases (case-insensitive)
    for banned in BANNED:
        pattern = re.compile(re.escape(banned), re.IGNORECASE)
        desc = pattern.sub("", desc)

    # Clean up extra spaces
    desc = re.sub(r'\s+', ' ', desc).strip()

    log.debug(f"✅ Generated safe copy for: {name}")
    return desc


def validate_copy(text: str) -> tuple[bool, List[str]]:
    """
    Validate if copy is appeal-safe.

    Args:
        text: Product description to validate

    Returns:
        Tuple of (is_safe, list_of_violations)
    """
    violations = []

    for banned in BANNED:
        pattern = re.compile(re.escape(banned), re.IGNORECASE)
        if pattern.search(text):
            violations.append(banned)

    is_safe = len(violations) == 0

    if is_safe:
        log.info("✅ Copy is appeal-safe")
    else:
        log.warning(f"⚠️  Found {len(violations)} policy violations: {violations}")

    return (is_safe, violations)


def sanitize_copy(text: str) -> str:
    """
    Remove banned phrases from existing copy.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text
    """
    sanitized = text

    for banned in BANNED:
        pattern = re.compile(re.escape(banned), re.IGNORECASE)
        sanitized = pattern.sub("", sanitized)

    # Clean up extra spaces
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()

    log.info("🧹 Copy sanitized")
    return sanitized


def generate_title(base_name: str, variant: str = None) -> str:
    """
    Generate a policy-safe product title.

    Args:
        base_name: Base product name
        variant: Optional variant (color, size, etc.)

    Returns:
        Safe product title
    """
    if variant:
        title = f"{base_name} - {variant}"
    else:
        title = base_name

    # Remove banned phrases
    title = sanitize_copy(title)

    # Keep it concise (TikTok recommends < 34 chars for visibility)
    if len(title) > 34:
        log.warning(f"⚠️  Title length {len(title)} exceeds recommended 34 chars")

    return title


if __name__ == "__main__":
    # Demo usage
    print("\n📝 Generating safe copy...\n")

    # Example 1: Basic hoodie
    desc1 = generate(
        "Midnight Waves Hoodie",
        product_type="hoodie",
        features=["unique graphic design", "soft cotton blend"]
    )
    print(f"Description 1:\n{desc1}\n")

    # Example 2: Validate unsafe copy
    unsafe = "This is the BEST SELLER hoodie - ACT NOW! Limited time only! Guaranteed quality!"
    is_safe, violations = validate_copy(unsafe)
    print(f"Unsafe copy violations: {violations}\n")

    # Example 3: Sanitize unsafe copy
    safe = sanitize_copy(unsafe)
    print(f"Sanitized: {safe}\n")

    # Example 4: Generate title
    title = generate_title("Premium Cotton Hoodie", "Black")
    print(f"Title: {title}")

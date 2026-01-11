"""Verification modules for ensuring execution correctness."""

from antigravity.verification.playwright_verifier import (
    verify_product_live,
    verify_shopify_product,
    capture_screenshot,
)

__all__ = [
    "verify_product_live",
    "verify_shopify_product",
    "capture_screenshot",
]

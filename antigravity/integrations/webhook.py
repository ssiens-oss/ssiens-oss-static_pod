"""Webhook integration for external services."""

import os
import requests
from typing import Optional, Dict, Any


def emit_webhook(
    url: Optional[str],
    payload: Dict[str, Any],
    method: str = "POST",
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10,
) -> bool:
    """
    Send webhook notification to external service.

    Args:
        url: Webhook URL (uses WEBHOOK_URL env var if not provided)
        payload: Data to send
        method: HTTP method (default: POST)
        headers: Optional custom headers
        timeout: Request timeout in seconds

    Returns:
        True if successful, False otherwise
    """
    webhook_url = url or os.environ.get("WEBHOOK_URL")

    if not webhook_url:
        print("Warning: WEBHOOK_URL not configured, skipping webhook")
        return False

    try:
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Antigravity-POD-System/1.0",
        }

        if headers:
            default_headers.update(headers)

        response = requests.request(
            method=method,
            url=webhook_url,
            json=payload,
            headers=default_headers,
            timeout=timeout,
        )

        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        print(f"Webhook emission failed: {e}")
        return False


def emit_webhook_with_retry(
    url: Optional[str],
    payload: Dict[str, Any],
    max_retries: int = 3,
    retry_delay: float = 2.0,
) -> bool:
    """
    Send webhook with automatic retry on failure.

    Args:
        url: Webhook URL
        payload: Data to send
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        True if successful, False if all retries failed
    """
    import time

    for attempt in range(max_retries):
        if emit_webhook(url, payload):
            return True

        if attempt < max_retries - 1:
            print(f"Webhook failed, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_delay)
            retry_delay *= 1.5  # Exponential backoff

    print(f"Webhook failed after {max_retries} attempts")
    return False


def emit_multiple_webhooks(
    urls: list[str],
    payload: Dict[str, Any],
) -> Dict[str, bool]:
    """
    Send the same payload to multiple webhooks.

    Args:
        urls: List of webhook URLs
        payload: Data to send

    Returns:
        Dict mapping URL to success status
    """
    results = {}

    for url in urls:
        results[url] = emit_webhook(url, payload)

    return results

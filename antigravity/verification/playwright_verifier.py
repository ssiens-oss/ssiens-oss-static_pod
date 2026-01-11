"""Playwright-based verification for POD products."""

from typing import Optional, Dict, Any, List
from pathlib import Path
import time

try:
    from playwright.sync_api import sync_playwright, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None
    Page = None


class VerificationError(Exception):
    """Raised when verification fails."""
    pass


def verify_product_live(
    url: str,
    expected_title: Optional[str] = None,
    expected_price: Optional[float] = None,
    timeout: int = 30000,
    headless: bool = True,
    screenshot_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Verify that a product page is live and correct.

    Args:
        url: Product URL to verify
        expected_title: Expected product title (optional)
        expected_price: Expected price (optional)
        timeout: Page load timeout in milliseconds
        headless: Run browser in headless mode
        screenshot_path: Path to save screenshot (optional)

    Returns:
        Dict with verification results

    Raises:
        VerificationError: If verification fails
    """
    if not PLAYWRIGHT_AVAILABLE:
        raise RuntimeError(
            "Playwright not installed. Install with: pip install playwright && playwright install"
        )

    results = {
        "url": url,
        "success": False,
        "title": None,
        "price": None,
        "checks_passed": [],
        "checks_failed": [],
        "screenshot": screenshot_path,
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()

            # Navigate to product page
            print(f"🌐 Loading {url}...")
            response = page.goto(url, timeout=timeout, wait_until="networkidle")

            if not response or not response.ok:
                raise VerificationError(f"Failed to load page: HTTP {response.status if response else 'no response'}")

            results["checks_passed"].append("Page loaded successfully")

            # Wait for content to render
            time.sleep(2)

            # Take screenshot if requested
            if screenshot_path:
                Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"   📸 Screenshot saved: {screenshot_path}")

            # Verify title
            if expected_title:
                actual_title = _extract_product_title(page)
                results["title"] = actual_title

                if actual_title and expected_title.lower() in actual_title.lower():
                    results["checks_passed"].append(f"Title verified: {actual_title}")
                    print(f"   ✅ Title verified")
                else:
                    results["checks_failed"].append(f"Title mismatch: expected '{expected_title}', got '{actual_title}'")
                    print(f"   ❌ Title mismatch")

            # Verify price
            if expected_price is not None:
                actual_price = _extract_product_price(page)
                results["price"] = actual_price

                if actual_price and abs(actual_price - expected_price) < 0.01:
                    results["checks_passed"].append(f"Price verified: ${actual_price}")
                    print(f"   ✅ Price verified: ${actual_price}")
                else:
                    results["checks_failed"].append(f"Price mismatch: expected ${expected_price}, got ${actual_price}")
                    print(f"   ❌ Price mismatch")

            # Verify product is not showing error state
            error_indicators = [
                "404",
                "not found",
                "page not found",
                "product not found",
                "unavailable",
            ]

            page_text = page.inner_text("body").lower()
            has_error = any(indicator in page_text for indicator in error_indicators)

            if has_error:
                results["checks_failed"].append("Error state detected on page")
                print(f"   ❌ Error state detected")
            else:
                results["checks_passed"].append("No error state detected")

            browser.close()

            # Overall success
            results["success"] = len(results["checks_failed"]) == 0

            return results

    except Exception as e:
        results["checks_failed"].append(f"Verification exception: {str(e)}")
        results["success"] = False
        return results


def verify_shopify_product(
    store_url: str,
    product_handle: str,
    expected_title: Optional[str] = None,
    expected_price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Verify a Shopify product is live.

    Args:
        store_url: Shopify store URL (e.g., "mystore.myshopify.com")
        product_handle: Product handle/slug
        expected_title: Expected title
        expected_price: Expected price

    Returns:
        Verification results
    """
    # Clean store URL
    store_url = store_url.replace("https://", "").replace("http://", "")

    product_url = f"https://{store_url}/products/{product_handle}"

    return verify_product_live(
        url=product_url,
        expected_title=expected_title,
        expected_price=expected_price,
    )


def _extract_product_title(page: Page) -> Optional[str]:
    """Extract product title from page."""
    # Try common selectors for product titles
    selectors = [
        "h1",
        "[data-product-title]",
        ".product-title",
        ".product__title",
        "h1.title",
        "h1[itemprop='name']",
    ]

    for selector in selectors:
        try:
            element = page.query_selector(selector)
            if element:
                text = element.inner_text().strip()
                if text:
                    return text
        except Exception:
            continue

    return None


def _extract_product_price(page: Page) -> Optional[float]:
    """Extract product price from page."""
    # Try common selectors for product price
    selectors = [
        "[data-product-price]",
        ".product-price",
        ".price",
        ".product__price",
        "span.money",
        "[itemprop='price']",
    ]

    for selector in selectors:
        try:
            element = page.query_selector(selector)
            if element:
                text = element.inner_text().strip()
                # Extract numeric price from text
                price = _parse_price(text)
                if price is not None:
                    return price
        except Exception:
            continue

    return None


def _parse_price(price_text: str) -> Optional[float]:
    """Parse price from text string."""
    import re

    # Remove currency symbols and extract number
    # Handles formats like: $49.99, 49.99, $49,99, etc.
    cleaned = re.sub(r'[^\d.,]', '', price_text)
    cleaned = cleaned.replace(',', '.')

    try:
        return float(cleaned)
    except ValueError:
        return None


def capture_screenshot(
    url: str,
    output_path: str,
    full_page: bool = True,
    headless: bool = True,
) -> bool:
    """
    Capture screenshot of a URL.

    Args:
        url: URL to capture
        output_path: Path to save screenshot
        full_page: Capture full page or just viewport
        headless: Run browser in headless mode

    Returns:
        True if successful, False otherwise
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("Warning: Playwright not available")
        return False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()

            page.goto(url, wait_until="networkidle")
            time.sleep(2)  # Allow dynamic content to load

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=output_path, full_page=full_page)

            browser.close()

            print(f"📸 Screenshot saved: {output_path}")
            return True

    except Exception as e:
        print(f"Screenshot failed: {e}")
        return False


def batch_verify(
    urls: List[str],
    screenshot_dir: Optional[str] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Verify multiple product URLs.

    Args:
        urls: List of URLs to verify
        screenshot_dir: Directory to save screenshots (optional)

    Returns:
        Dict mapping URL to verification results
    """
    results = {}

    for i, url in enumerate(urls, 1):
        print(f"\n🔍 Verifying {i}/{len(urls)}: {url}")

        screenshot_path = None
        if screenshot_dir:
            screenshot_path = str(Path(screenshot_dir) / f"verify_{i}.png")

        try:
            result = verify_product_live(url, screenshot_path=screenshot_path)
            results[url] = result
        except Exception as e:
            results[url] = {
                "success": False,
                "error": str(e),
            }

    success_count = sum(1 for r in results.values() if r.get("success"))
    print(f"\n✅ Verification complete: {success_count}/{len(urls)} successful")

    return results


def verify_zazzle_product(
    product_id: str,
    expected_title: Optional[str] = None,
    expected_price: Optional[float] = None,
    store_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Verify a Zazzle product is live.

    Args:
        product_id: Zazzle product ID
        expected_title: Expected product title
        expected_price: Expected price
        store_id: Optional store ID

    Returns:
        Verification results
    """
    # Build Zazzle product URL
    if store_id:
        product_url = f"https://www.zazzle.com/store/{store_id}/products/{product_id}"
    else:
        product_url = f"https://www.zazzle.com/pd/{product_id}"

    return verify_product_live(
        url=product_url,
        expected_title=expected_title,
        expected_price=expected_price,
    )


def verify_zazzle_store(
    store_id: str,
    screenshot_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Verify a Zazzle store is accessible.

    Args:
        store_id: Zazzle store ID
        screenshot_path: Path to save screenshot

    Returns:
        Verification results
    """
    store_url = f"https://www.zazzle.com/store/{store_id}"

    if not PLAYWRIGHT_AVAILABLE:
        return {
            "success": False,
            "error": "Playwright not available",
        }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(store_url, wait_until="networkidle")
            time.sleep(2)

            # Check if store page loaded
            page_text = page.inner_text("body").lower()
            has_error = "not found" in page_text or "404" in page_text

            if screenshot_path:
                Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=screenshot_path, full_page=True)

            browser.close()

            return {
                "url": store_url,
                "success": not has_error,
                "checks_passed": ["Store page loaded"] if not has_error else [],
                "checks_failed": ["Store not found"] if has_error else [],
                "screenshot": screenshot_path,
            }

    except Exception as e:
        return {
            "url": store_url,
            "success": False,
            "error": str(e),
        }

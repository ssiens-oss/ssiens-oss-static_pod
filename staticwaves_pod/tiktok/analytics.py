"""
TikTok SKU Analytics Engine

Tracks per-SKU performance metrics across multiple price points:
- Impressions
- Clicks
- Orders
- Conversion Rate (CVR)

Used to identify winning prices and inform price optimization decisions.
"""

import json
from pathlib import Path
from typing import Literal
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

log = get_logger("TIKTOK-ANALYTICS")
DATA = Path("staticwaves_pod/data/tiktok_metrics.json")

EventType = Literal["impressions", "clicks", "orders"]


def record_event(sku: str, price: float, event: EventType):
    """
    Record a performance event for a SKU at a specific price point.

    Args:
        sku: SKU identifier
        price: Price point being tested
        event: Event type ('impressions', 'clicks', 'orders')
    """
    DATA.parent.mkdir(parents=True, exist_ok=True)

    data = json.loads(DATA.read_text()) if DATA.exists() else {}

    sku_data = data.setdefault(sku, {"prices": {}})
    price_key = str(price)

    p = sku_data["prices"].setdefault(price_key, {
        "impressions": 0,
        "clicks": 0,
        "orders": 0,
        "cvr": 0.0
    })

    p[event] += 1

    DATA.write_text(json.dumps(data, indent=2))
    log.debug(f"📊 Recorded {event} for {sku} @ ${price}")


def compute_cvr():
    """
    Compute conversion rates (CVR) for all SKU/price combinations.

    CVR = orders / clicks
    Updates metrics file with calculated CVR values.
    """
    if not DATA.exists():
        log.warning("⚠️  No metrics data to compute CVR")
        return

    data = json.loads(DATA.read_text())

    for sku, s in data.items():
        for price, m in s["prices"].items():
            clicks = max(m["clicks"], 1)  # Avoid division by zero
            m["cvr"] = round(m["orders"] / clicks, 4)

    DATA.write_text(json.dumps(data, indent=2))
    log.info("📈 CVR computed for all SKUs")


def get_sku_stats(sku: str) -> dict:
    """
    Get performance statistics for a specific SKU.

    Args:
        sku: SKU identifier

    Returns:
        Dictionary of price points and their metrics
    """
    if not DATA.exists():
        return {}

    data = json.loads(DATA.read_text())
    return data.get(sku, {}).get("prices", {})


def get_best_price(sku: str) -> tuple[float, dict]:
    """
    Get the best performing price for a SKU based on CVR.

    Args:
        sku: SKU identifier

    Returns:
        Tuple of (best_price, metrics_dict)
    """
    stats = get_sku_stats(sku)

    if not stats:
        raise ValueError(f"No stats available for SKU: {sku}")

    # Sort by CVR descending
    best_price = max(stats.items(), key=lambda x: x[1].get("cvr", 0))

    return (float(best_price[0]), best_price[1])


def get_all_metrics() -> dict:
    """
    Get all metrics across all SKUs.

    Returns:
        Complete metrics dictionary
    """
    if not DATA.exists():
        return {}

    return json.loads(DATA.read_text())


def reset_metrics(sku: str = None):
    """
    Reset metrics for a specific SKU or all SKUs.

    Args:
        sku: Optional SKU to reset. If None, resets all metrics.
    """
    if not DATA.exists():
        return

    if sku is None:
        DATA.write_text("{}")
        log.info("🔄 All metrics reset")
    else:
        data = json.loads(DATA.read_text())
        if sku in data:
            del data[sku]
            DATA.write_text(json.dumps(data, indent=2))
            log.info(f"🔄 Metrics reset for {sku}")


if __name__ == "__main__":
    # Demo usage
    record_event("HOODIE-001", 29.99, "impressions")
    record_event("HOODIE-001", 29.99, "clicks")
    record_event("HOODIE-001", 29.99, "orders")

    record_event("HOODIE-001", 39.99, "impressions")
    record_event("HOODIE-001", 39.99, "clicks")

    compute_cvr()

    print("📊 Metrics:", json.dumps(get_all_metrics(), indent=2))

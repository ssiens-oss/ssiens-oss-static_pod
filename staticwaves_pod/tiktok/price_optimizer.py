"""
TikTok Price Optimizer - Auto-Kill Losing Buckets

Automatically removes underperforming price points based on:
- Minimum impression threshold
- Minimum conversion rate (CVR)

This prevents wasting impressions on prices that don't convert.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

log = get_logger("PRICE-OPTIMIZER")
DATA = Path("staticwaves_pod/data/tiktok_metrics.json")

# Thresholds for price pruning
MIN_IMPRESSIONS = 500  # Minimum impressions before evaluating CVR
MIN_CVR = 0.01  # 1% minimum conversion rate


def prune_prices(min_impressions: int = MIN_IMPRESSIONS, min_cvr: float = MIN_CVR) -> dict:
    """
    Remove underperforming price buckets across all SKUs.

    A price bucket is removed if:
    - It has >= min_impressions AND
    - Its CVR < min_cvr

    Args:
        min_impressions: Minimum impressions before evaluating
        min_cvr: Minimum acceptable conversion rate

    Returns:
        Dictionary of removed prices by SKU
    """
    if not DATA.exists():
        log.warning("⚠️  No metrics data to prune")
        return {}

    data = json.loads(DATA.read_text())
    removed = {}

    for sku, stats in data.items():
        removed[sku] = []

        for price, m in list(stats["prices"].items()):
            impressions = m.get("impressions", 0)
            cvr = m.get("cvr", 0)

            # Only evaluate prices with sufficient data
            if impressions >= min_impressions and cvr < min_cvr:
                del stats["prices"][price]
                removed[sku].append(price)
                log.info(f"❌ Killed price ${price} for {sku} (CVR: {cvr:.2%}, Impressions: {impressions})")

    # Clean up SKUs with no remaining prices
    for sku in list(data.keys()):
        if not data[sku]["prices"]:
            log.warning(f"⚠️  {sku} has no remaining price buckets")

    DATA.write_text(json.dumps(data, indent=2))

    total_removed = sum(len(prices) for prices in removed.values())
    log.info(f"🧹 Pruned {total_removed} underperforming price buckets")

    return removed


def lock_winning_price(sku: str, min_orders: int = 10) -> float | None:
    """
    Lock in the best performing price for a SKU.

    Only locks if the winning price has sufficient order volume.

    Args:
        sku: SKU identifier
        min_orders: Minimum orders required to lock price

    Returns:
        Locked price or None if insufficient data
    """
    if not DATA.exists():
        return None

    data = json.loads(DATA.read_text())

    if sku not in data:
        log.warning(f"⚠️  SKU {sku} not found in metrics")
        return None

    prices = data[sku]["prices"]

    if not prices:
        log.warning(f"⚠️  No price data for {sku}")
        return None

    # Find best price by CVR with minimum order threshold
    qualified = {
        price: metrics
        for price, metrics in prices.items()
        if metrics.get("orders", 0) >= min_orders
    }

    if not qualified:
        log.warning(f"⚠️  No prices meet minimum order threshold ({min_orders}) for {sku}")
        return None

    best_price = max(qualified.items(), key=lambda x: x[1].get("cvr", 0))
    locked_price = float(best_price[0])

    log.info(
        f"🔒 Locked price ${locked_price} for {sku} "
        f"(CVR: {best_price[1]['cvr']:.2%}, Orders: {best_price[1]['orders']})"
    )

    return locked_price


def get_price_report() -> dict:
    """
    Generate a report of all price buckets and their performance.

    Returns:
        Formatted report dictionary
    """
    if not DATA.exists():
        return {}

    data = json.loads(DATA.read_text())
    report = {}

    for sku, stats in data.items():
        report[sku] = {
            "total_price_buckets": len(stats["prices"]),
            "prices": []
        }

        for price, metrics in stats["prices"].items():
            report[sku]["prices"].append({
                "price": float(price),
                "impressions": metrics.get("impressions", 0),
                "clicks": metrics.get("clicks", 0),
                "orders": metrics.get("orders", 0),
                "cvr": metrics.get("cvr", 0)
            })

        # Sort by CVR descending
        report[sku]["prices"].sort(key=lambda x: x["cvr"], reverse=True)

    return report


if __name__ == "__main__":
    # Demo: Prune underperforming prices
    removed = prune_prices()
    print(f"\n📊 Removed prices: {json.dumps(removed, indent=2)}")

    # Generate report
    report = get_price_report()
    print(f"\n📈 Price Report: {json.dumps(report, indent=2)}")

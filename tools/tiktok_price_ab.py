"""
TikTok Price A/B Testing System
================================
Algorithmic price bucket rotation for maximum TikTok discovery.

TikTok's algorithm favors price diversity across similar SKUs.
This module automatically rotates between tested price points
to boost organic reach and conversion testing.
"""

import random
from typing import List

# Price buckets optimized for apparel POD on TikTok
# Based on competitive analysis and platform-specific conversion data
PRICE_BUCKETS: List[int] = [39, 44, 49, 54]

# Premium tier buckets (activate for designer collaborations)
PREMIUM_BUCKETS: List[int] = [59, 64, 69, 74]

# Budget tier buckets (activate for flash sales)
BUDGET_BUCKETS: List[int] = [29, 34, 37]


def choose_price(tier: str = "standard") -> int:
    """
    Select a price from the appropriate bucket tier.

    Args:
        tier: Price tier - "standard", "premium", or "budget"

    Returns:
        Integer price in USD

    Example:
        >>> choose_price()
        44
        >>> choose_price("premium")
        69
    """
    buckets_map = {
        "standard": PRICE_BUCKETS,
        "premium": PREMIUM_BUCKETS,
        "budget": BUDGET_BUCKETS
    }

    buckets = buckets_map.get(tier, PRICE_BUCKETS)
    return random.choice(buckets)


def get_price_with_variance(base_price: int, variance: float = 0.1) -> int:
    """
    Add controlled randomness to a base price.

    Args:
        base_price: Starting price point
        variance: Percentage variance (0.1 = ±10%)

    Returns:
        Price with applied variance, rounded to nearest dollar

    Example:
        >>> get_price_with_variance(50, 0.15)
        47  # (50 ± 15%)
    """
    variance_amount = base_price * variance
    min_price = base_price - variance_amount
    max_price = base_price + variance_amount

    return round(random.uniform(min_price, max_price))


def get_all_buckets() -> dict:
    """
    Retrieve all configured price buckets.

    Returns:
        Dictionary of all tier configurations
    """
    return {
        "standard": PRICE_BUCKETS,
        "premium": PREMIUM_BUCKETS,
        "budget": BUDGET_BUCKETS
    }


if __name__ == "__main__":
    print("🎯 TikTok Price A/B System Test")
    print("=" * 50)

    print("\n📊 Standard Tier Prices (10 samples):")
    for i in range(10):
        print(f"  ${choose_price('standard')}")

    print("\n💎 Premium Tier Prices (5 samples):")
    for i in range(5):
        print(f"  ${choose_price('premium')}")

    print("\n💰 Budget Tier Prices (5 samples):")
    for i in range(5):
        print(f"  ${choose_price('budget')}")

    print("\n🎲 Variance Test (base=$50, ±15%):")
    for i in range(5):
        print(f"  ${get_price_with_variance(50, 0.15)}")

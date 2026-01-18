"""
Product Performance Analytics & Scoring

Tracks product metrics and calculates performance scores for:
- Auto-disabling low performers
- Auto-expanding bestsellers
- Profit-aware decisions
"""
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProductMetrics:
    """Product performance metrics"""
    product_id: str
    sku: str
    platform: str  # shopify, etsy, tiktok
    views: int = 0
    favorites: int = 0
    add_to_carts: int = 0
    sales: int = 0
    revenue_cents: int = 0
    days_live: int = 0

    # Cost structure
    fulfillment_cost_cents: int = 0
    platform_fee_pct: float = 0.0
    ad_spend_cents: int = 0

    # Trend signals
    daily_views: int = 0
    avg_7d_views: float = 0.0
    conversion_rate: float = 0.0


def calculate_performance_score(
    views: int,
    favorites: int,
    add_to_carts: int,
    sales: int
) -> float:
    """
    Calculate basic performance score (revenue-weighted)

    Args:
        views: Total views
        favorites: Total favorites/likes
        add_to_carts: Add to cart actions
        sales: Completed sales

    Returns:
        Performance score (higher is better)
    """
    return (
        sales * 5.0 +
        add_to_carts * 2.0 +
        favorites * 1.0 +
        views * 0.1
    )


def calculate_net_profit(
    revenue_cents: int,
    fulfillment_cost_cents: int,
    platform_fee_pct: float,
    ad_spend_cents: int = 0
) -> int:
    """
    Calculate net profit after all costs

    Args:
        revenue_cents: Total revenue in cents
        fulfillment_cost_cents: Cost of fulfillment
        platform_fee_pct: Platform fee percentage (0.0-1.0)
        ad_spend_cents: Total ad spend

    Returns:
        Net profit in cents
    """
    platform_fees = int(revenue_cents * platform_fee_pct)
    return revenue_cents - fulfillment_cost_cents - platform_fees - ad_spend_cents


def calculate_profit_score(
    sales: int,
    net_profit_cents: int,
    conversion_rate: float,
    views: int
) -> float:
    """
    Calculate profit-weighted performance score

    Prioritizes profit margin over raw revenue

    Args:
        sales: Number of sales
        net_profit_cents: Net profit after all costs
        conversion_rate: Conversion rate (0.0-1.0)
        views: Total views

    Returns:
        Profit score (higher is better)
    """
    # Convert cents to dollars for scoring
    profit_dollars = net_profit_cents / 100.0

    return (
        sales * profit_dollars +
        conversion_rate * 50.0 +
        views * 0.05
    )


def should_auto_disable(
    days_live: int,
    sales: int,
    performance_score: float,
    min_days: int = 14,
    min_score: float = 10.0
) -> bool:
    """
    Determine if product should be auto-disabled

    Args:
        days_live: Days since product went live
        sales: Total sales
        performance_score: Current performance score
        min_days: Minimum days before considering disable
        min_score: Minimum score threshold

    Returns:
        True if product should be disabled
    """
    # Never disable if has sales
    if sales > 0:
        return False

    # Must be live for minimum period
    if days_live < min_days:
        return False

    # Disable if score too low
    return performance_score < min_score


def should_auto_disable_profit_aware(
    days_live: int,
    sales: int,
    net_profit_cents: int,
    min_days: int = 14
) -> bool:
    """
    Profit-aware auto-disable logic

    Args:
        days_live: Days since product went live
        sales: Total sales
        net_profit_cents: Net profit after costs
        min_days: Minimum days before considering disable

    Returns:
        True if product should be disabled
    """
    # Must be live for minimum period
    if days_live < min_days:
        return False

    # Disable if no sales and in the red
    return sales == 0 and net_profit_cents <= 0


def is_bestseller(
    sales: int,
    conversion_rate: float,
    min_sales: int = 5,
    min_conversion: float = 0.03
) -> bool:
    """
    Detect if product is a bestseller

    Args:
        sales: Total sales
        conversion_rate: Conversion rate
        min_sales: Minimum sales threshold
        min_conversion: Minimum conversion rate

    Returns:
        True if product qualifies as bestseller
    """
    return sales >= min_sales and conversion_rate >= min_conversion


def calculate_trend_velocity(
    today_views: int,
    avg_7d_views: float
) -> float:
    """
    Calculate view trend velocity

    Args:
        today_views: Views today
        avg_7d_views: 7-day average views

    Returns:
        Velocity multiplier (>1 = trending up, <1 = trending down)
    """
    if avg_7d_views == 0:
        return 0.0
    return today_views / avg_7d_views


def detect_trend_status(
    velocity: float,
    sales_delta: int
) -> str:
    """
    Detect product trend status

    Args:
        velocity: View velocity multiplier
        sales_delta: Change in sales (recent vs average)

    Returns:
        Trend status: viral, rising, stable, declining
    """
    if velocity >= 2.5 and sales_delta > 0:
        return "viral"
    elif velocity >= 1.5:
        return "rising"
    elif velocity >= 0.7:
        return "stable"
    else:
        return "declining"


def calculate_conversion_rate(
    sales: int,
    views: int
) -> float:
    """
    Calculate conversion rate

    Args:
        sales: Total sales
        views: Total views

    Returns:
        Conversion rate (0.0-1.0)
    """
    if views == 0:
        return 0.0
    return sales / views


# Platform fee structures (default values)
PLATFORM_FEES = {
    "shopify": 0.029,  # 2.9% + 30¢ per transaction (simplified)
    "etsy": 0.065,     # 6.5% transaction fee
    "tiktok": 0.05,    # 5% commission
}


# Fulfillment costs (estimated cents, by product type)
FULFILLMENT_COSTS = {
    "hoodie": 2500,      # $25.00
    "tee": 1200,         # $12.00
    "sticker": 200,      # $2.00
    "poster": 800,       # $8.00
    "blanket": 3000,     # $30.00
    "mug": 600,          # $6.00
    "tote_bag": 700,     # $7.00
    "phone_case": 800,   # $8.00
}


def get_platform_fee(platform: str) -> float:
    """Get platform fee percentage"""
    return PLATFORM_FEES.get(platform.lower(), 0.05)


def get_fulfillment_cost(product_type: str) -> int:
    """Get fulfillment cost in cents"""
    return FULFILLMENT_COSTS.get(product_type.lower(), 1500)


def should_promote_with_ads(
    performance_score: float,
    min_score: float = 25.0
) -> bool:
    """
    Determine if product should be promoted with paid ads

    Args:
        performance_score: Current performance score
        min_score: Minimum score to qualify for promotion

    Returns:
        True if product should be promoted
    """
    return performance_score >= min_score

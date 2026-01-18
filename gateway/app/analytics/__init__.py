"""
Analytics and Performance Tracking
"""
from .performance import (
    ProductMetrics,
    calculate_performance_score,
    calculate_net_profit,
    calculate_profit_score,
    should_auto_disable,
    should_auto_disable_profit_aware,
    is_bestseller,
    calculate_trend_velocity,
    detect_trend_status,
    calculate_conversion_rate,
    get_platform_fee,
    get_fulfillment_cost,
    should_promote_with_ads,
    PLATFORM_FEES,
    FULFILLMENT_COSTS
)

__all__ = [
    'ProductMetrics',
    'calculate_performance_score',
    'calculate_net_profit',
    'calculate_profit_score',
    'should_auto_disable',
    'should_auto_disable_profit_aware',
    'is_bestseller',
    'calculate_trend_velocity',
    'detect_trend_status',
    'calculate_conversion_rate',
    'get_platform_fee',
    'get_fulfillment_cost',
    'should_promote_with_ads',
    'PLATFORM_FEES',
    'FULFILLMENT_COSTS',
]

"""
Pricing Engine
Cost + margin calculations with configurable rules
"""

import json
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"

def price_product(product_data):
    """
    Calculate product price based on cost + margin rules

    Args:
        product_data: dict with 'base_cost' and 'type'

    Returns:
        float: Final price
    """
    base_cost = product_data.get("base_cost", 30.00)
    product_type = product_data.get("type", "default")

    # Load pricing rules
    pricing_rules = load_pricing_rules()

    # Get margin multiplier for product type
    margin = pricing_rules.get(product_type, pricing_rules.get("default", 1.8))

    # Calculate final price
    price = round(base_cost * margin, 2)

    return price

def load_pricing_rules():
    """
    Load pricing rules from config
    Falls back to defaults if config doesn't exist
    """
    pricing_file = CONFIG_DIR / "pricing.json"

    # Default pricing rules
    defaults = {
        "hoodie": 1.8,      # 80% markup
        "tee": 1.9,         # 90% markup
        "poster": 2.0,      # 100% markup
        "mug": 1.85,        # 85% markup
        "default": 1.8      # 80% default
    }

    try:
        if pricing_file.exists():
            with open(pricing_file) as f:
                return json.load(f)
    except Exception:
        pass

    return defaults

def calculate_profit(product_data):
    """Calculate profit margin"""
    base_cost = product_data.get("base_cost", 30.00)
    price = product_data.get("price", price_product(product_data))

    profit = price - base_cost
    margin_percent = (profit / price) * 100

    return {
        "profit": round(profit, 2),
        "margin_percent": round(margin_percent, 2)
    }

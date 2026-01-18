"""
Smart Pricing Service
Intelligent pricing recommendations based on product type, complexity, and market analysis
"""
import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PricingStrategy:
    """Pricing strategy result"""
    base_price_cents: int
    suggested_price_cents: int
    min_price_cents: int
    max_price_cents: int
    profit_margin: float
    reasoning: str


class SmartPricingService:
    """
    Intelligent pricing service for POD products

    Features:
    - Product type-based pricing
    - Complexity adjustments
    - Market positioning
    - Profit margin optimization
    """

    # Base costs per product type (in cents)
    BASE_COSTS = {
        "tshirt": 1000,      # $10.00 base cost
        "hoodie": 2000,      # $20.00 base cost
        "sweatshirt": 1800,  # $18.00 base cost
        "tank_top": 900,     # $9.00 base cost
        "long_sleeve": 1400, # $14.00 base cost
        "poster": 800,       # $8.00 base cost
        "canvas": 2500,      # $25.00 base cost
        "mug": 800,          # $8.00 base cost
        "phone_case": 1200,  # $12.00 base cost
        "tote_bag": 1000,    # $10.00 base cost
        "pillow": 1500,      # $15.00 base cost
        "sticker": 200,      # $2.00 base cost
    }

    # Market positioning multipliers
    POSITIONING = {
        "budget": 1.5,       # 50% markup
        "standard": 2.0,     # 100% markup (2x cost)
        "premium": 2.5,      # 150% markup
        "luxury": 3.5,       # 250% markup
    }

    # Complexity multipliers
    COMPLEXITY_MULTIPLIERS = {
        "simple": 1.0,       # No adjustment
        "moderate": 1.15,    # +15%
        "detailed": 1.3,     # +30%
        "complex": 1.5,      # +50%
    }

    def __init__(self, default_positioning: str = "standard"):
        """
        Initialize pricing service

        Args:
            default_positioning: Default market positioning (budget, standard, premium, luxury)
        """
        self.default_positioning = default_positioning
        logger.info(f"Smart Pricing Service initialized (positioning: {default_positioning})")

    def calculate_price(
        self,
        product_type: str,
        complexity: str = "moderate",
        positioning: Optional[str] = None,
        custom_adjustments: Optional[Dict[str, float]] = None
    ) -> PricingStrategy:
        """
        Calculate intelligent pricing for a product

        Args:
            product_type: Type of product (tshirt, hoodie, etc.)
            complexity: Design complexity (simple, moderate, detailed, complex)
            positioning: Market positioning (budget, standard, premium, luxury)
            custom_adjustments: Optional custom multipliers {"shipping": 1.1, "seasonal": 0.9}

        Returns:
            PricingStrategy with recommended pricing
        """
        # Get base cost
        product_type_lower = product_type.lower().replace(" ", "_")
        base_cost = self.BASE_COSTS.get(product_type_lower, 1500)  # Default $15 if unknown

        # Apply positioning multiplier
        positioning = positioning or self.default_positioning
        positioning_multiplier = self.POSITIONING.get(positioning, 2.0)

        # Apply complexity multiplier
        complexity_multiplier = self.COMPLEXITY_MULTIPLIERS.get(complexity, 1.15)

        # Calculate base price
        base_price = int(base_cost * positioning_multiplier)

        # Apply complexity adjustment
        suggested_price = int(base_price * complexity_multiplier)

        # Apply custom adjustments
        if custom_adjustments:
            for adjustment_name, multiplier in custom_adjustments.items():
                suggested_price = int(suggested_price * multiplier)
                logger.debug(f"Applied {adjustment_name} adjustment: {multiplier}x")

        # Round to nearest 99 cents (psychological pricing)
        suggested_price = self._round_to_99(suggested_price)

        # Calculate range
        min_price = max(base_cost, int(suggested_price * 0.85))  # Never below cost, max 15% discount
        max_price = int(suggested_price * 1.5)  # Up to 50% premium

        # Calculate profit margin
        profit_margin = ((suggested_price - base_cost) / suggested_price) * 100

        # Build reasoning
        reasoning = self._build_reasoning(
            product_type, base_cost, complexity, positioning,
            suggested_price, profit_margin
        )

        return PricingStrategy(
            base_price_cents=base_price,
            suggested_price_cents=suggested_price,
            min_price_cents=min_price,
            max_price_cents=max_price,
            profit_margin=profit_margin,
            reasoning=reasoning
        )

    def _round_to_99(self, price_cents: int) -> int:
        """
        Round price to psychological pricing (.99)

        Args:
            price_cents: Price in cents

        Returns:
            Rounded price ending in 99
        """
        # Convert to dollars
        dollars = price_cents / 100

        # Round to nearest dollar
        rounded_dollars = round(dollars)

        # Subtract 1 cent for .99 ending
        return int((rounded_dollars * 100) - 1)

    def _build_reasoning(
        self,
        product_type: str,
        base_cost: int,
        complexity: str,
        positioning: str,
        suggested_price: int,
        profit_margin: float
    ) -> str:
        """Build human-readable pricing reasoning"""
        return (
            f"${suggested_price / 100:.2f} based on: "
            f"{product_type} (${base_cost / 100:.2f} base), "
            f"{complexity} complexity, "
            f"{positioning} positioning. "
            f"Profit margin: {profit_margin:.1f}%"
        )

    def get_product_recommendations(self, product_type: str) -> Dict:
        """
        Get pricing recommendations for different positioning strategies

        Args:
            product_type: Product type

        Returns:
            Dict with pricing for each positioning strategy
        """
        recommendations = {}

        for positioning in ["budget", "standard", "premium", "luxury"]:
            strategy = self.calculate_price(
                product_type=product_type,
                complexity="moderate",
                positioning=positioning
            )
            recommendations[positioning] = {
                "price_cents": strategy.suggested_price_cents,
                "price_usd": strategy.suggested_price_cents / 100,
                "profit_margin": strategy.profit_margin,
                "reasoning": strategy.reasoning
            }

        return recommendations

    def adjust_for_seasonal(
        self,
        base_strategy: PricingStrategy,
        season: str
    ) -> PricingStrategy:
        """
        Adjust pricing for seasonal demand

        Args:
            base_strategy: Base pricing strategy
            season: Season (spring, summer, fall, winter, holiday)

        Returns:
            Adjusted pricing strategy
        """
        seasonal_multipliers = {
            "spring": 1.0,
            "summer": 0.95,  # Lower demand for hoodies/sweaters
            "fall": 1.05,    # Higher demand begins
            "winter": 1.1,   # Peak season for apparel
            "holiday": 1.15, # Premium holiday pricing
        }

        multiplier = seasonal_multipliers.get(season.lower(), 1.0)
        adjusted_price = int(base_strategy.suggested_price_cents * multiplier)
        adjusted_price = self._round_to_99(adjusted_price)

        # Recalculate profit margin
        base_cost = int(base_strategy.suggested_price_cents / (1 + base_strategy.profit_margin / 100))
        profit_margin = ((adjusted_price - base_cost) / adjusted_price) * 100

        return PricingStrategy(
            base_price_cents=base_strategy.base_price_cents,
            suggested_price_cents=adjusted_price,
            min_price_cents=base_strategy.min_price_cents,
            max_price_cents=base_strategy.max_price_cents,
            profit_margin=profit_margin,
            reasoning=f"{base_strategy.reasoning} | Seasonal adjustment ({season}): {multiplier}x"
        )

    def bulk_pricing(self, quantity: int, unit_price_cents: int) -> int:
        """
        Calculate bulk order pricing

        Args:
            quantity: Number of units
            unit_price_cents: Regular unit price

        Returns:
            Discounted unit price for bulk
        """
        if quantity >= 100:
            return int(unit_price_cents * 0.80)  # 20% discount
        elif quantity >= 50:
            return int(unit_price_cents * 0.85)  # 15% discount
        elif quantity >= 25:
            return int(unit_price_cents * 0.90)  # 10% discount
        elif quantity >= 10:
            return int(unit_price_cents * 0.95)  # 5% discount
        else:
            return unit_price_cents

"""POD offer generation and variant creation."""

import random
from typing import List, Dict, Any
from antigravity.models import PODOffer


class OfferFactory:
    """Factory for generating POD product offer variants."""

    # Price points for testing
    PRICE_TIERS = {
        "tshirt": [19.99, 24.99, 29.99],
        "hoodie": [39.99, 44.99, 49.99, 54.99],
    }

    # Headline templates
    HEADLINE_TEMPLATES = [
        "{brand} {product_type}",
        "Limited Drop: {brand} {product_type}",
        "{brand} - {style} {product_type}",
        "Exclusive {brand} {product_type} Release",
        "{style} {product_type} by {brand}",
    ]

    # Style descriptors
    STYLES = [
        "Streetwear",
        "Urban",
        "AI-Generated",
        "Limited Edition",
        "Exclusive",
        "Artist Series",
    ]

    def __init__(
        self,
        default_brand: str = "StaticWaves",
        enable_ab_testing: bool = True,
    ):
        """
        Initialize offer factory.

        Args:
            default_brand: Default brand name
            enable_ab_testing: If True, generate multiple variants for A/B testing
        """
        self.default_brand = default_brand
        self.enable_ab_testing = enable_ab_testing

    def generate_offer(
        self,
        product_type: str,
        brand: str = None,
        base_price: float = None,
        style: str = None,
    ) -> PODOffer:
        """
        Generate a single offer.

        Args:
            product_type: Type of product (tshirt, hoodie)
            brand: Brand name
            base_price: Base price (uses random from tier if not provided)
            style: Style descriptor

        Returns:
            PODOffer
        """
        brand = brand or self.default_brand
        style = style or random.choice(self.STYLES)

        # Get price
        if base_price:
            price = base_price
        else:
            price_tier = self.PRICE_TIERS.get(product_type.lower(), [29.99])
            price = random.choice(price_tier)

        # Generate headline
        headline_template = random.choice(self.HEADLINE_TEMPLATES)
        headline = headline_template.format(
            brand=brand,
            product_type=product_type.title(),
            style=style,
        )

        # Generate description
        description = self._generate_description(
            product_type=product_type,
            brand=brand,
            style=style,
        )

        # Generate tags
        tags = self._generate_tags(product_type, brand, style)

        return PODOffer(
            price=price,
            headline=headline,
            description=description,
            tags=tags,
            brand=brand,
        )

    def generate_variants(
        self,
        product_type: str,
        count: int = 3,
        brand: str = None,
    ) -> List[PODOffer]:
        """
        Generate multiple offer variants for A/B testing.

        Args:
            product_type: Type of product
            count: Number of variants to generate
            brand: Brand name

        Returns:
            List of PODOffer variants
        """
        if not self.enable_ab_testing:
            return [self.generate_offer(product_type, brand)]

        variants = []
        brand = brand or self.default_brand

        # Generate variants with different prices and headlines
        price_tier = self.PRICE_TIERS.get(product_type.lower(), [29.99])

        for i in range(min(count, len(price_tier))):
            style = self.STYLES[i % len(self.STYLES)]
            variants.append(
                self.generate_offer(
                    product_type=product_type,
                    brand=brand,
                    base_price=price_tier[i],
                    style=style,
                )
            )

        return variants

    def _generate_description(
        self,
        product_type: str,
        brand: str,
        style: str,
    ) -> str:
        """Generate product description."""
        templates = [
            f"{style} {product_type} from {brand}. Premium quality, unique design.",
            f"Exclusive {brand} {product_type}. {style} aesthetic with comfort in mind.",
            f"{brand} brings you this {style.lower()} {product_type}. Limited quantities available.",
            f"Stand out with this {style.lower()} {product_type} by {brand}. Designed for individuality.",
        ]
        return random.choice(templates)

    def _generate_tags(
        self,
        product_type: str,
        brand: str,
        style: str,
    ) -> List[str]:
        """Generate product tags."""
        base_tags = [
            brand.lower(),
            product_type.lower(),
            style.lower().replace(" ", ""),
        ]

        additional_tags = [
            "streetwear",
            "fashion",
            "style",
            "limited",
            "exclusive",
            "apparel",
        ]

        return base_tags + random.sample(additional_tags, 3)


def compare_offers(offers: List[PODOffer]) -> Dict[str, Any]:
    """
    Compare multiple offers and provide analysis.

    Args:
        offers: List of offers to compare

    Returns:
        Comparison analysis
    """
    if not offers:
        return {}

    prices = [o.price for o in offers]

    return {
        "count": len(offers),
        "price_range": {
            "min": min(prices),
            "max": max(prices),
            "avg": sum(prices) / len(prices),
        },
        "brands": list(set(o.brand for o in offers)),
        "unique_headlines": len(set(o.headline for o in offers)),
    }

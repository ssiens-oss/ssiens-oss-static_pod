"""
Product Catalog for POD Publishing

Defines available product types for each platform with their configurations.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class ProductCategory(Enum):
    """Product categories"""
    APPAREL = "apparel"
    HOME_LIVING = "home_living"
    ACCESSORIES = "accessories"
    STATIONERY = "stationery"


@dataclass
class ProductType:
    """Product type definition"""
    id: str
    name: str
    category: ProductCategory
    description: str
    blueprint_id: Optional[int] = None  # Printify blueprint ID
    provider_id: Optional[int] = None   # Printify provider ID
    default_price_cents: int = 1999
    min_resolution: tuple = (1024, 1024)
    recommended_resolution: tuple = (2400, 2400)
    platform_configs: Dict = None  # Platform-specific configs

    def __post_init__(self):
        if self.platform_configs is None:
            self.platform_configs = {}


# Printify Product Catalog
# Blueprint IDs and Provider IDs from Printify API
# Provider 99 = Printify Choice (automatic best provider)

PRINTIFY_PRODUCTS = {
    # APPAREL - T-Shirts
    "mens_tshirt": ProductType(
        id="mens_tshirt",
        name="Men's T-Shirt",
        category=ProductCategory.APPAREL,
        description="Classic unisex t-shirt",
        blueprint_id=5,  # Bella+Canvas 3001 Unisex Jersey
        provider_id=99,
        default_price_cents=1999,
        min_resolution=(2400, 2400),
        recommended_resolution=(4500, 5400)
    ),
    "womens_tshirt": ProductType(
        id="womens_tshirt",
        name="Women's T-Shirt",
        category=ProductCategory.APPAREL,
        description="Women's fitted t-shirt",
        blueprint_id=6,  # Bella+Canvas 6004 Women's
        provider_id=99,
        default_price_cents=1999,
        min_resolution=(2400, 2400),
        recommended_resolution=(4500, 5400)
    ),
    "premium_tshirt": ProductType(
        id="premium_tshirt",
        name="Premium T-Shirt",
        category=ProductCategory.APPAREL,
        description="Premium quality t-shirt",
        blueprint_id=4,  # Next Level 3600
        provider_id=99,
        default_price_cents=2299,
        min_resolution=(2400, 2400),
        recommended_resolution=(4500, 5400)
    ),

    # APPAREL - Hoodies & Sweatshirts
    "hoodie": ProductType(
        id="hoodie",
        name="Hoodie",
        category=ProductCategory.APPAREL,
        description="Gildan Heavy Blend Hoodie",
        blueprint_id=77,  # Gildan 18500 Heavy Blend Hoodie
        provider_id=99,
        default_price_cents=3499,
        min_resolution=(2400, 2400),
        recommended_resolution=(4500, 5400)
    ),
    "crewneck_sweatshirt": ProductType(
        id="crewneck_sweatshirt",
        name="Crewneck Sweatshirt",
        category=ProductCategory.APPAREL,
        description="Classic crewneck sweatshirt",
        blueprint_id=53,  # Gildan 18000 Crewneck
        provider_id=99,
        default_price_cents=2999,
        min_resolution=(2400, 2400),
        recommended_resolution=(4500, 5400)
    ),
    "zip_hoodie": ProductType(
        id="zip_hoodie",
        name="Zip Hoodie",
        category=ProductCategory.APPAREL,
        description="Full-zip hoodie",
        blueprint_id=78,  # Gildan 18600 Zip Hoodie
        provider_id=99,
        default_price_cents=3999,
        min_resolution=(2400, 2400),
        recommended_resolution=(4500, 5400)
    ),

    # APPAREL - Long Sleeve & Tank Tops
    "long_sleeve": ProductType(
        id="long_sleeve",
        name="Long Sleeve T-Shirt",
        category=ProductCategory.APPAREL,
        description="Long sleeve shirt",
        blueprint_id=7,  # Bella+Canvas 3501 Long Sleeve
        provider_id=99,
        default_price_cents=2499,
        min_resolution=(2400, 2400),
        recommended_resolution=(4500, 5400)
    ),
    "tank_top": ProductType(
        id="tank_top",
        name="Tank Top",
        category=ProductCategory.APPAREL,
        description="Sleeveless tank top",
        blueprint_id=8,  # Bella+Canvas 3480 Tank
        provider_id=99,
        default_price_cents=1899,
        min_resolution=(2400, 2400),
        recommended_resolution=(4500, 5400)
    ),

    # HOME & LIVING - Wall Art
    "poster": ProductType(
        id="poster",
        name="Poster",
        category=ProductCategory.HOME_LIVING,
        description="Premium poster print",
        blueprint_id=1,  # Poster
        provider_id=99,
        default_price_cents=1499,
        min_resolution=(2400, 3000),
        recommended_resolution=(4800, 6000)
    ),
    "canvas": ProductType(
        id="canvas",
        name="Canvas Print",
        category=ProductCategory.HOME_LIVING,
        description="Stretched canvas wall art",
        blueprint_id=2,  # Canvas
        provider_id=99,
        default_price_cents=3999,
        min_resolution=(2400, 2400),
        recommended_resolution=(4800, 4800)
    ),
    "framed_poster": ProductType(
        id="framed_poster",
        name="Framed Poster",
        category=ProductCategory.HOME_LIVING,
        description="Poster with frame",
        blueprint_id=84,  # Framed Poster
        provider_id=99,
        default_price_cents=4999,
        min_resolution=(2400, 3000),
        recommended_resolution=(4800, 6000)
    ),

    # HOME & LIVING - Textiles
    "throw_pillow": ProductType(
        id="throw_pillow",
        name="Throw Pillow",
        category=ProductCategory.HOME_LIVING,
        description="Decorative throw pillow",
        blueprint_id=27,  # Throw Pillow
        provider_id=99,
        default_price_cents=2499,
        min_resolution=(2400, 2400),
        recommended_resolution=(4800, 4800)
    ),
    "fleece_blanket": ProductType(
        id="fleece_blanket",
        name="Fleece Blanket",
        category=ProductCategory.HOME_LIVING,
        description="Soft fleece blanket",
        blueprint_id=28,  # Fleece Blanket
        provider_id=99,
        default_price_cents=3999,
        min_resolution=(3000, 3000),
        recommended_resolution=(6000, 6000)
    ),
    "tapestry": ProductType(
        id="tapestry",
        name="Wall Tapestry",
        category=ProductCategory.HOME_LIVING,
        description="Wall hanging tapestry",
        blueprint_id=171,  # Tapestry
        provider_id=99,
        default_price_cents=2999,
        min_resolution=(2400, 2400),
        recommended_resolution=(4800, 4800)
    ),

    # HOME & LIVING - Drinkware
    "mug": ProductType(
        id="mug",
        name="Coffee Mug",
        category=ProductCategory.HOME_LIVING,
        description="Ceramic coffee mug",
        blueprint_id=12,  # 11oz Mug
        provider_id=99,
        default_price_cents=1499,
        min_resolution=(2400, 1200),
        recommended_resolution=(4800, 2400)
    ),
    "travel_mug": ProductType(
        id="travel_mug",
        name="Travel Mug",
        category=ProductCategory.HOME_LIVING,
        description="Insulated travel mug",
        blueprint_id=242,  # Travel Mug
        provider_id=99,
        default_price_cents=2499,
        min_resolution=(2400, 1200),
        recommended_resolution=(4800, 2400)
    ),

    # ACCESSORIES - Bags
    "tote_bag": ProductType(
        id="tote_bag",
        name="Tote Bag",
        category=ProductCategory.ACCESSORIES,
        description="Canvas tote bag",
        blueprint_id=26,  # Tote Bag
        provider_id=99,
        default_price_cents=1799,
        min_resolution=(2400, 2400),
        recommended_resolution=(4800, 4800)
    ),
    "backpack": ProductType(
        id="backpack",
        name="Backpack",
        category=ProductCategory.ACCESSORIES,
        description="All-over print backpack",
        blueprint_id=333,  # Backpack
        provider_id=99,
        default_price_cents=4999,
        min_resolution=(2400, 2400),
        recommended_resolution=(4800, 4800)
    ),
    "drawstring_bag": ProductType(
        id="drawstring_bag",
        name="Drawstring Bag",
        category=ProductCategory.ACCESSORIES,
        description="Drawstring backpack",
        blueprint_id=385,  # Drawstring Bag
        provider_id=99,
        default_price_cents=1499,
        min_resolution=(2400, 2400),
        recommended_resolution=(4800, 4800)
    ),

    # ACCESSORIES - Phone & Tech
    "phone_case": ProductType(
        id="phone_case",
        name="Phone Case",
        category=ProductCategory.ACCESSORIES,
        description="Protective phone case",
        blueprint_id=45,  # Phone Case
        provider_id=99,
        default_price_cents=1999,
        min_resolution=(1800, 3000),
        recommended_resolution=(3600, 6000)
    ),
    "laptop_sleeve": ProductType(
        id="laptop_sleeve",
        name="Laptop Sleeve",
        category=ProductCategory.ACCESSORIES,
        description="Padded laptop sleeve",
        blueprint_id=386,  # Laptop Sleeve
        provider_id=99,
        default_price_cents=2999,
        min_resolution=(2400, 1800),
        recommended_resolution=(4800, 3600)
    ),

    # ACCESSORIES - Wearables
    "cap": ProductType(
        id="cap",
        name="Baseball Cap",
        category=ProductCategory.ACCESSORIES,
        description="Embroidered baseball cap",
        blueprint_id=206,  # Dad Hat
        provider_id=99,
        default_price_cents=2299,
        min_resolution=(1500, 1500),
        recommended_resolution=(3000, 3000)
    ),
    "beanie": ProductType(
        id="beanie",
        name="Beanie",
        category=ProductCategory.ACCESSORIES,
        description="Knit beanie hat",
        blueprint_id=380,  # Beanie
        provider_id=99,
        default_price_cents=1999,
        min_resolution=(2400, 2400),
        recommended_resolution=(4800, 4800)
    ),
    "socks": ProductType(
        id="socks",
        name="Socks",
        category=ProductCategory.ACCESSORIES,
        description="All-over print socks",
        blueprint_id=423,  # Socks
        provider_id=99,
        default_price_cents=1499,
        min_resolution=(2400, 2400),
        recommended_resolution=(4800, 4800)
    ),

    # STATIONERY
    "sticker": ProductType(
        id="sticker",
        name="Sticker",
        category=ProductCategory.STATIONERY,
        description="Die-cut vinyl sticker",
        blueprint_id=407,  # Kiss Cut Stickers
        provider_id=99,
        default_price_cents=299,
        min_resolution=(1500, 1500),
        recommended_resolution=(3000, 3000)
    ),
    "notebook": ProductType(
        id="notebook",
        name="Spiral Notebook",
        category=ProductCategory.STATIONERY,
        description="Hardcover spiral notebook",
        blueprint_id=388,  # Spiral Notebook
        provider_id=99,
        default_price_cents=1499,
        min_resolution=(2400, 3000),
        recommended_resolution=(4800, 6000)
    ),
    "greeting_card": ProductType(
        id="greeting_card",
        name="Greeting Card",
        category=ProductCategory.STATIONERY,
        description="Folded greeting card",
        blueprint_id=756,  # Greeting Card
        provider_id=99,
        default_price_cents=499,
        min_resolution=(2400, 1800),
        recommended_resolution=(4800, 3600)
    ),
}


def get_products_by_category(category: ProductCategory) -> List[ProductType]:
    """Get all products in a category"""
    return [p for p in PRINTIFY_PRODUCTS.values() if p.category == category]


def get_product(product_id: str) -> Optional[ProductType]:
    """Get product by ID"""
    return PRINTIFY_PRODUCTS.get(product_id)


def get_all_products() -> Dict[str, ProductType]:
    """Get all available products"""
    return PRINTIFY_PRODUCTS


def get_popular_products() -> List[ProductType]:
    """Get most popular products for quick selection"""
    popular_ids = [
        "mens_tshirt",
        "hoodie",
        "poster",
        "sticker",
        "mug",
        "tote_bag",
        "phone_case",
        "canvas"
    ]
    return [PRINTIFY_PRODUCTS[pid] for pid in popular_ids if pid in PRINTIFY_PRODUCTS]


def validate_image_resolution(product_id: str, width: int, height: int) -> tuple[bool, str]:
    """
    Validate if image resolution meets product requirements

    Args:
        product_id: Product type ID
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Tuple of (is_valid, error_message)
    """
    product = get_product(product_id)
    if not product:
        return False, f"Unknown product type: {product_id}"

    min_w, min_h = product.min_resolution
    rec_w, rec_h = product.recommended_resolution

    # Check minimum resolution
    if width < min_w or height < min_h:
        return False, f"Resolution too low ({width}x{height}). Minimum required: {min_w}x{min_h}"

    # Warn if below recommended
    if width < rec_w or height < rec_h:
        return True, f"Warning: Resolution {width}x{height} is below recommended {rec_w}x{rec_h}. Quality may vary."

    return True, ""

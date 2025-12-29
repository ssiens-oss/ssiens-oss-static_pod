"""
Printify Product Templates

Configurable blueprint definitions for multi-product publishing.
"""

from typing import Dict, List


# Blueprint IDs from Printify API
# Find more at: https://developers.printify.com/#blueprints
BLUEPRINTS = {
    "tee": 384,
    "hoodie": 521,
    "crewneck": 521,
    "tank": 12,
    "sweatshirt": 521,
    "poster": 12,
    "canvas": 12,
    "mug": 265,
    "phone_case": 380,
    "tote_bag": 285,
    "sticker": 285,
    "pillow": 6,
    "blanket": 763,
    "beanie": 374
}


def get_template(name: str) -> Dict:
    """
    Get product template by name.

    Args:
        name: Template name (tee, hoodie, etc.)

    Returns:
        Template configuration dictionary
    """
    templates = {
        "tee": {
            "name": "Unisex Heavy Cotton Tee",
            "blueprint_id": BLUEPRINTS["tee"],
            "provider_id": 1,
            "variant_id": 1,
            "base_cost": 1200,  # $12.00
            "margin": 0.55,  # 55%
            "print_areas": ["front"]
        },
        "hoodie": {
            "name": "Unisex Heavy Blend Hoodie",
            "blueprint_id": BLUEPRINTS["hoodie"],
            "provider_id": 1,
            "variant_id": 1,
            "base_cost": 2600,  # $26.00
            "margin": 0.60,  # 60%
            "print_areas": ["front"]
        },
        "crewneck": {
            "name": "Unisex Crewneck Sweatshirt",
            "blueprint_id": BLUEPRINTS["crewneck"],
            "provider_id": 1,
            "variant_id": 1,
            "base_cost": 2200,  # $22.00
            "margin": 0.58,  # 58%
            "print_areas": ["front"]
        },
        "poster": {
            "name": "Museum Quality Poster",
            "blueprint_id": BLUEPRINTS["poster"],
            "provider_id": 1,
            "variant_id": 1,
            "base_cost": 800,  # $8.00
            "margin": 0.65,  # 65%
            "print_areas": ["front"]
        },
        "canvas": {
            "name": "Premium Canvas",
            "blueprint_id": BLUEPRINTS["canvas"],
            "provider_id": 1,
            "variant_id": 1,
            "base_cost": 1400,  # $14.00
            "margin": 0.70,  # 70%
            "print_areas": ["front"]
        },
        "mug": {
            "name": "White Ceramic Mug",
            "blueprint_id": BLUEPRINTS["mug"],
            "provider_id": 1,
            "variant_id": 1,
            "base_cost": 900,  # $9.00
            "margin": 0.60,  # 60%
            "print_areas": ["front"]
        },
        "phone_case": {
            "name": "iPhone Tough Case",
            "blueprint_id": BLUEPRINTS["phone_case"],
            "provider_id": 1,
            "variant_id": 1,
            "base_cost": 1100,  # $11.00
            "margin": 0.65,  # 65%
            "print_areas": ["front"]
        },
        "tote_bag": {
            "name": "Cotton Tote Bag",
            "blueprint_id": BLUEPRINTS["tote_bag"],
            "provider_id": 1,
            "variant_id": 1,
            "base_cost": 1300,  # $13.00
            "margin": 0.60,  # 60%
            "print_areas": ["front"]
        }
    }

    if name not in templates:
        raise ValueError(f"Unknown template: {name}")

    return templates[name]


def get_all_templates() -> Dict[str, Dict]:
    """
    Get all available product templates.

    Returns:
        Dictionary of template_name -> template_config
    """
    return {
        "tee": get_template("tee"),
        "hoodie": get_template("hoodie"),
        "crewneck": get_template("crewneck"),
        "poster": get_template("poster")
    }


def get_template_names() -> List[str]:
    """
    Get list of all template names.

    Returns:
        List of template names
    """
    return ["tee", "hoodie", "crewneck", "poster", "canvas", "mug", "phone_case", "tote_bag"]

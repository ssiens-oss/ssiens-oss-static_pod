#!/usr/bin/env python3
"""
Mockup Worker
Creates product mockups (hoodie, tee, poster) from designs
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import json

DATA_DIR = Path(__file__).parent.parent / "data"
TEMPLATES_DIR = Path(__file__).parent.parent / "config" / "templates"

# Mockup configurations
MOCKUP_CONFIGS = {
    "hoodie": {
        "template_size": (2000, 2400),
        "design_position": (500, 600),
        "design_size": (1000, 1000),
        "print_area": "chest"
    },
    "tee": {
        "template_size": (2000, 2400),
        "design_position": (500, 650),
        "design_size": (1000, 1000),
        "print_area": "chest"
    },
    "poster": {
        "template_size": (1800, 2400),
        "design_position": (50, 50),
        "design_size": (1700, 2300),
        "print_area": "full"
    },
    "mug": {
        "template_size": (1200, 1200),
        "design_position": (200, 300),
        "design_size": (800, 600),
        "print_area": "wrap"
    }
}

def create_mockup(design_path, product_type="hoodie", output_path=None):
    """
    Create product mockup from design

    Args:
        design_path: Path to design image
        product_type: Type of product (hoodie, tee, poster, mug)
        output_path: Optional output path

    Returns:
        Path: Path to generated mockup
    """

    # Get mockup config
    config = MOCKUP_CONFIGS.get(product_type, MOCKUP_CONFIGS["hoodie"])

    # Load design
    design = Image.open(design_path)

    # Create mockup template
    mockup = create_template(product_type, config)

    # Resize design to fit
    design_resized = design.resize(config["design_size"], Image.Resampling.LANCZOS)

    # Composite design onto mockup
    mockup.paste(design_resized, config["design_position"], design_resized if design_resized.mode == "RGBA" else None)

    # Save mockup
    if output_path is None:
        design_name = Path(design_path).stem
        output_path = DATA_DIR / "designs" / f"{design_name}_{product_type}_mockup.png"

    mockup.save(output_path, "PNG")

    print(f"✅ Created {product_type} mockup: {output_path}")

    return output_path

def create_template(product_type, config):
    """
    Create mockup template

    In production, this would load actual product templates
    For now, creates simple colored backgrounds
    """

    # Template colors by product type
    colors = {
        "hoodie": (30, 30, 40),      # Dark gray
        "tee": (255, 255, 255),       # White
        "poster": (240, 240, 245),    # Light gray
        "mug": (255, 250, 240)        # Cream
    }

    color = colors.get(product_type, (255, 255, 255))

    # Create template
    template = Image.new("RGB", config["template_size"], color)

    # Add simple product shape (placeholder for real templates)
    draw = ImageDraw.Draw(template)

    if product_type == "hoodie":
        # Draw simple hoodie shape
        draw.rectangle(
            [(400, 500), (1600, 2200)],
            fill=(50, 50, 60),
            outline=(100, 100, 110),
            width=5
        )
    elif product_type == "tee":
        # Draw simple t-shirt shape
        draw.rectangle(
            [(400, 600), (1600, 2000)],
            fill=(245, 245, 250),
            outline=(200, 200, 210),
            width=5
        )

    return template

def create_batch_mockups(design_path, product_types=None):
    """
    Create mockups for multiple product types

    Args:
        design_path: Path to design
        product_types: List of product types (default: all)

    Returns:
        dict: Mapping of product type → mockup path
    """

    if product_types is None:
        product_types = ["hoodie", "tee", "poster"]

    mockups = {}

    for product_type in product_types:
        try:
            mockup_path = create_mockup(design_path, product_type)
            mockups[product_type] = str(mockup_path)
        except Exception as e:
            print(f"❌ Failed to create {product_type} mockup: {e}")

    return mockups

def create_variant_mockups(design_path, product_type, colors=None):
    """
    Create mockups with different product colors

    Args:
        design_path: Path to design
        product_type: Product type
        colors: List of color names

    Returns:
        dict: Mapping of color → mockup path
    """

    if colors is None:
        colors = ["black", "white", "gray"]

    mockups = {}
    design_name = Path(design_path).stem

    for color in colors:
        output_path = DATA_DIR / "designs" / f"{design_name}_{product_type}_{color}_mockup.png"
        mockup_path = create_mockup(design_path, product_type, output_path)
        mockups[color] = str(mockup_path)

    return mockups

if __name__ == "__main__":
    # CLI usage
    import argparse

    parser = argparse.ArgumentParser(description="Create product mockups")
    parser.add_argument("design", help="Path to design image")
    parser.add_argument("--type", default="hoodie", choices=["hoodie", "tee", "poster", "mug"])
    parser.add_argument("--batch", action="store_true", help="Create all product types")
    parser.add_argument("--output", help="Output path")

    args = parser.parse_args()

    design_path = Path(args.design)

    if not design_path.exists():
        print(f"❌ Design not found: {design_path}")
        sys.exit(1)

    if args.batch:
        mockups = create_batch_mockups(design_path)
        print(f"\n✅ Created {len(mockups)} mockups:")
        for ptype, path in mockups.items():
            print(f"  {ptype}: {path}")
    else:
        mockup_path = create_mockup(design_path, args.type, args.output)
        print(f"\n✅ Mockup created: {mockup_path}")

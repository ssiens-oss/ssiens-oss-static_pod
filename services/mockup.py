#!/usr/bin/env python3
"""
Mockup Generator Service
Generates product mockups by compositing transparent designs onto apparel templates
"""

import sys
import os
from PIL import Image


def generate_mockup(
    base_template_path: str,
    design_path: str,
    output_path: str,
    scale: float = 0.7,
    y_offset: float = 0.45
):
    """
    Generate product mockup by compositing design onto template

    Args:
        base_template_path: Path to base apparel template (PNG with transparency)
        design_path: Path to design PNG (transparent background)
        output_path: Where to save the final mockup
        scale: Design scale relative to template width (0.0-1.0)
        y_offset: Vertical position as fraction of template height (0.0-1.0)
    """
    # Load base template
    base = Image.open(base_template_path).convert("RGBA")
    base_w, base_h = base.size

    # Load design
    design = Image.open(design_path).convert("RGBA")
    design_w, design_h = design.size

    # Calculate scaled design size
    target_w = int(base_w * scale)
    aspect_ratio = design_h / design_w
    target_h = int(target_w * aspect_ratio)

    # Resize design maintaining aspect ratio
    design_resized = design.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Calculate position to center design horizontally
    x = (base_w - target_w) // 2

    # Calculate vertical position using offset
    y = int(base_h * y_offset - target_h / 2)

    # Ensure design stays within bounds
    y = max(0, min(y, base_h - target_h))

    # Composite design onto base
    base.alpha_composite(design_resized, (x, y))

    # Save result
    base.save(output_path, "PNG")

    return output_path


def main():
    if len(sys.argv) < 4:
        print("Usage: python mockup.py <template> <design> <output> [scale] [y_offset]")
        print("Example: python mockup.py tshirt_base.png design.png mockup.png 0.7 0.45")
        sys.exit(1)

    template_path = sys.argv[1]
    design_path = sys.argv[2]
    output_path = sys.argv[3]
    scale = float(sys.argv[4]) if len(sys.argv) > 4 else 0.7
    y_offset = float(sys.argv[5]) if len(sys.argv) > 5 else 0.45

    # Validate inputs
    if not os.path.exists(template_path):
        print(f"Error: Template not found: {template_path}")
        sys.exit(1)

    if not os.path.exists(design_path):
        print(f"Error: Design not found: {design_path}")
        sys.exit(1)

    # Generate mockup
    try:
        result = generate_mockup(template_path, design_path, output_path, scale, y_offset)
        print(f"Mockup generated: {result}")
    except Exception as e:
        print(f"Error generating mockup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

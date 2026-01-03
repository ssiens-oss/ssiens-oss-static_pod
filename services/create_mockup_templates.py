#!/usr/bin/env python3
"""
Create placeholder mockup templates
Generates simple colored base templates for t-shirt and hoodie mockups
Users should replace these with real product photography for production use
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_template(product_type: str, output_path: str, size=(1200, 1400)):
    """
    Create a simple placeholder mockup template

    Args:
        product_type: 'tshirt' or 'hoodie'
        output_path: Where to save the template
        size: Template dimensions (width, height)
    """
    # Create base image with transparency
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Define colors
    if product_type == 'tshirt':
        color = (70, 70, 70, 255)  # Dark gray
        label = "T-SHIRT"
    else:  # hoodie
        color = (50, 50, 50, 255)  # Darker gray
        label = "HOODIE"

    # Draw simple shirt/hoodie shape
    # Body rectangle
    body_x = size[0] // 4
    body_y = size[1] // 4
    body_w = size[0] // 2
    body_h = int(size[1] * 0.6)

    draw.rectangle(
        [body_x, body_y, body_x + body_w, body_y + body_h],
        fill=color
    )

    # Neck opening
    neck_w = size[0] // 8
    neck_h = size[1] // 20
    neck_x = (size[0] - neck_w) // 2
    draw.rectangle(
        [neck_x, body_y, neck_x + neck_w, body_y + neck_h],
        fill=(0, 0, 0, 0)
    )

    # Sleeves
    sleeve_w = size[0] // 6
    sleeve_h = size[1] // 3

    # Left sleeve
    draw.polygon(
        [
            (body_x, body_y),
            (body_x - sleeve_w, body_y + sleeve_h // 2),
            (body_x, body_y + sleeve_h)
        ],
        fill=color
    )

    # Right sleeve
    draw.polygon(
        [
            (body_x + body_w, body_y),
            (body_x + body_w + sleeve_w, body_y + sleeve_h // 2),
            (body_x + body_w, body_y + sleeve_h)
        ],
        fill=color
    )

    # Add hood for hoodie
    if product_type == 'hoodie':
        hood_w = size[0] // 3
        hood_h = size[1] // 6
        hood_x = (size[0] - hood_w) // 2

        draw.ellipse(
            [hood_x, body_y - hood_h // 2, hood_x + hood_w, body_y + hood_h],
            fill=color
        )

    # Add text label (optional, for clarity)
    try:
        # Try to use a font, but fall back to default if not available
        font_size = 40
        # Use PIL's default font
        text = f"PLACEHOLDER {label} MOCKUP"
        text_bbox = draw.textbbox((0, 0), text)
        text_w = text_bbox[2] - text_bbox[0]
        text_x = (size[0] - text_w) // 2
        text_y = size[1] - 100

        draw.text((text_x, text_y), text, fill=(150, 150, 150, 255))

        note = "(Replace with real product photo)"
        note_bbox = draw.textbbox((0, 0), note)
        note_w = note_bbox[2] - note_bbox[0]
        note_x = (size[0] - note_w) // 2

        draw.text((note_x, text_y + 30), note, fill=(100, 100, 100, 255))
    except:
        pass  # Skip text if there are font issues

    # Save
    img.save(output_path, 'PNG')
    print(f"Created placeholder template: {output_path}")


def main():
    """Create both t-shirt and hoodie placeholder templates"""

    # Get template directory from environment or use default
    templates_dir = os.environ.get('MOCKUP_TEMPLATES_DIR', '/workspace/data/mockup-templates')

    # Ensure directory exists
    os.makedirs(templates_dir, exist_ok=True)

    # Create templates
    create_placeholder_template(
        'tshirt',
        os.path.join(templates_dir, 'tshirt_base.png'),
        size=(1200, 1400)
    )

    create_placeholder_template(
        'hoodie',
        os.path.join(templates_dir, 'hoodie_base.png'),
        size=(1200, 1500)
    )

    print(f"\n✓ Placeholder mockup templates created in: {templates_dir}")
    print("\nNOTE: For production use, replace these placeholders with:")
    print("  - High-quality product photography")
    print("  - Professional mockup templates")
    print("  - Templates from services like Printful, Printify, or Placeit")
    print("\nTemplate requirements:")
    print("  - PNG format with transparency")
    print("  - 1200x1400px or larger")
    print("  - Clear chest area for design placement")


if __name__ == '__main__':
    main()

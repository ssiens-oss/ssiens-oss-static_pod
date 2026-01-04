#!/usr/bin/env python3
"""
Create placeholder mockup templates for t-shirt and hoodie
These are simple templates that can be replaced with professional product photos later
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_tshirt_template(output_path: str, width: int = 1000, height: int = 1200):
    """Create a simple t-shirt template placeholder"""
    # Create blank image with transparency
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Draw a simple t-shirt shape
    # Body
    body_color = (200, 200, 200, 255)
    draw.rectangle([(250, 300), (750, 1000)], fill=body_color, outline=(100, 100, 100, 255), width=3)

    # Sleeves
    draw.polygon([(250, 300), (150, 400), (150, 500), (250, 450)], fill=body_color, outline=(100, 100, 100, 255))
    draw.polygon([(750, 300), (850, 400), (850, 500), (750, 450)], fill=body_color, outline=(100, 100, 100, 255))

    # Neckline
    draw.ellipse([(425, 280), (575, 350)], fill=(255, 255, 255, 255), outline=(100, 100, 100, 255), width=2)

    # Design area marker (where the design will be placed)
    design_area_color = (150, 150, 150, 100)
    draw.rectangle([(350, 400), (650, 700)], fill=design_area_color, outline=(80, 80, 80, 150), width=2)

    # Add text label
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font = ImageFont.load_default()

    text = "Design Area"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    draw.text((text_x, 540), text, fill=(80, 80, 80, 200), font=font)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG')
    print(f"✓ Created t-shirt template: {output_path}")

def create_hoodie_template(output_path: str, width: int = 1000, height: int = 1200):
    """Create a simple hoodie template placeholder"""
    # Create blank image with transparency
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Draw a simple hoodie shape
    # Body
    body_color = (180, 180, 180, 255)
    draw.rectangle([(250, 350), (750, 1050)], fill=body_color, outline=(100, 100, 100, 255), width=3)

    # Sleeves
    draw.polygon([(250, 350), (150, 450), (150, 600), (250, 550)], fill=body_color, outline=(100, 100, 100, 255))
    draw.polygon([(750, 350), (850, 450), (850, 600), (750, 550)], fill=body_color, outline=(100, 100, 100, 255))

    # Hood
    draw.arc([(350, 250), (650, 400)], start=0, end=180, fill=(100, 100, 100, 255), width=3)
    draw.rectangle([(350, 325), (650, 350)], fill=body_color)

    # Drawstring
    draw.line([(450, 360), (550, 360)], fill=(60, 60, 60, 255), width=2)

    # Pocket
    pocket_color = (160, 160, 160, 255)
    draw.rectangle([(350, 650), (650, 800)], fill=pocket_color, outline=(100, 100, 100, 255), width=2)

    # Design area marker (where the design will be placed)
    design_area_color = (150, 150, 150, 100)
    draw.rectangle([(350, 450), (650, 750)], fill=design_area_color, outline=(80, 80, 80, 150), width=2)

    # Add text label
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font = ImageFont.load_default()

    text = "Design Area"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    draw.text((text_x, 590), text, fill=(80, 80, 80, 200), font=font)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG')
    print(f"✓ Created hoodie template: {output_path}")

if __name__ == '__main__':
    # Create templates in workspace data directory
    template_dir = '/workspace/data/mockup-templates'

    create_tshirt_template(f'{template_dir}/tshirt_base.png')
    create_hoodie_template(f'{template_dir}/hoodie_base.png')

    print("\n✅ Mockup templates created successfully!")
    print(f"Location: {template_dir}")
    print("\nNote: These are placeholder templates. Replace with professional product photos for production use.")

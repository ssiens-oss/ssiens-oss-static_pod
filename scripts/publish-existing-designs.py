#!/usr/bin/env python3
"""
Process existing ComfyUI outputs - create gallery proof and publish to Printify
"""

import os
import sys
import requests
import time
from pathlib import Path
from typing import List
from PIL import Image, ImageDraw, ImageFont
import glob

# Configuration
PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")
COMFYUI_OUTPUT = os.getenv("COMFYUI_OUTPUT_DIR", "./ComfyUI/output")

class ExistingImageProcessor:
    def __init__(self):
        self.comfyui_output = Path(COMFYUI_OUTPUT)
        self.gallery_dir = Path("data/gallery")
        self.gallery_dir.mkdir(parents=True, exist_ok=True)

    def find_images(self, pattern: str = "*.png") -> List[Path]:
        """Find all images in ComfyUI output directory"""
        images = list(self.comfyui_output.glob(pattern))
        # Also check for jpg/jpeg
        images.extend(self.comfyui_output.glob("*.jpg"))
        images.extend(self.comfyui_output.glob("*.jpeg"))

        # Sort by modification time (newest first)
        images.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        return images

    def create_gallery_proof(self, image_paths: List[Path], output_path: str):
        """Create a gallery proof sheet from images"""

        print(f"📸 Creating gallery proof from {len(image_paths)} images...")

        if not image_paths:
            print("⚠️  No images found")
            return

        # Load and resize images
        images = []
        for path in image_paths:
            try:
                img = Image.open(path)
                img.thumbnail((512, 512))
                images.append((img, path.stem))  # Use filename as title
            except Exception as e:
                print(f"⚠️  Skipping {path.name}: {e}")

        if not images:
            print("⚠️  No valid images to process")
            return

        # Calculate grid
        cols = min(3, len(images))
        rows = (len(images) + cols - 1) // cols

        cell_width = 512
        cell_height = 600
        gallery_width = cols * cell_width + (cols + 1) * 20
        gallery_height = rows * cell_height + (rows + 1) * 20

        gallery = Image.new('RGB', (gallery_width, gallery_height), color='white')
        draw = ImageDraw.Draw(gallery)

        # Load fonts
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = ImageFont.load_default()
            small_font = font

        # Place images
        for idx, (img, title) in enumerate(images):
            row = idx // cols
            col = idx % cols

            x = col * cell_width + (col + 1) * 20
            y = row * cell_height + (row + 1) * 20

            # Paste image
            gallery.paste(img, (x, y))

            # Draw title
            text_y = y + 512 + 10
            # Truncate long filenames
            display_title = title[:40] + "..." if len(title) > 40 else title
            draw.text((x + 10, text_y), display_title, fill='black', font=font)
            draw.text((x + 10, text_y + 30), f"#{idx + 1}", fill='gray', font=small_font)

        # Add header
        header_height = 80
        new_gallery = Image.new('RGB', (gallery_width, gallery_height + header_height), color='#2c3e50')
        new_gallery.paste(gallery, (0, header_height))

        draw = ImageDraw.Draw(new_gallery)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        except:
            title_font = font

        draw.text((20, 20), f"ComfyUI Gallery - {timestamp}", fill='white', font=title_font)

        # Save
        new_gallery.save(output_path, quality=95)
        print(f"✅ Gallery saved: {output_path}")

    def upload_to_printify(self, image_path: Path, title: str, price: float = 39.99):
        """Upload to Printify"""

        if not PRINTIFY_API_KEY or not PRINTIFY_SHOP_ID:
            print(f"⚠️  Skipping upload for {title} (no Printify credentials)")
            return None

        headers = {"Authorization": f"Bearer {PRINTIFY_API_KEY}"}

        print(f"📤 Uploading {title}...")

        # Upload image
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/png')}
            response = requests.post(
                "https://api.printify.com/v1/uploads/images.json",
                headers=headers,
                files=files
            )

            if response.status_code != 200:
                print(f"❌ Upload failed: {response.text}")
                return None

            image_id = response.json()["id"]

        # Create hoodie product
        product_data = {
            "title": title,
            "description": f"Unique AI-generated design: {title}",
            "blueprint_id": 77,  # Heavy Blend Hoodie
            "print_provider_id": 99,
            "variants": [
                {"id": vid, "price": int(price * 100), "is_enabled": True}
                for vid in [45740, 45741, 45742, 45743, 45744]
            ],
            "print_areas": [{
                "variant_ids": [45740, 45741, 45742, 45743, 45744],
                "placeholders": [{
                    "position": "front",
                    "images": [{
                        "id": image_id,
                        "x": 0.5,
                        "y": 0.5,
                        "scale": 1.0,
                        "angle": 0
                    }]
                }]
            }]
        }

        response = requests.post(
            f"https://api.printify.com/v1/shops/{PRINTIFY_SHOP_ID}/products.json",
            headers={**headers, "Content-Type": "application/json"},
            json=product_data
        )

        if response.status_code == 200:
            product = response.json()
            print(f"✅ Published: {title} (Product ID: {product['id']})")
            return product
        else:
            print(f"❌ Publish failed: {response.text}")
            return None

    def process(self, count: int = None, publish: bool = True, pattern: str = "*.png"):
        """Process existing images"""

        print("🎨 Processing existing ComfyUI outputs\n")
        print(f"Looking in: {self.comfyui_output}")

        # Find images
        all_images = self.find_images(pattern)

        if not all_images:
            print(f"❌ No images found in {self.comfyui_output}")
            print(f"\nMake sure ComfyUI has generated images.")
            print(f"Images should be in: {self.comfyui_output}/")
            return

        # Limit count if specified
        images = all_images[:count] if count else all_images

        print(f"Found {len(all_images)} total images")
        print(f"Processing {len(images)} images\n")

        # Create gallery proof
        gallery_path = self.gallery_dir / f"gallery_{int(time.time())}.png"
        self.create_gallery_proof(images, str(gallery_path))

        # Publish to Printify
        if publish and (PRINTIFY_API_KEY and PRINTIFY_SHOP_ID):
            print(f"\n📤 Publishing {len(images)} designs to Printify...\n")

            published = []
            for idx, img_path in enumerate(images):
                # Create product title from filename
                title = img_path.stem.replace("_", " ").title()
                if len(title) > 50:
                    title = title[:50]

                product = self.upload_to_printify(img_path, title)
                if product:
                    published.append(product)

                # Rate limiting
                if idx < len(images) - 1:
                    time.sleep(1)

            print(f"\n✅ Published {len(published)}/{len(images)} products")
        else:
            print("\n⚠️  Skipping Printify publishing")

        # Summary
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        print(f"Images processed: {len(images)}")
        print(f"Gallery proof: {gallery_path}")
        print(f"Source directory: {self.comfyui_output}")
        print("\nProcessed images:")
        for idx, img in enumerate(images[:20]):  # Show first 20
            print(f"  {idx + 1}. {img.name}")
        if len(images) > 20:
            print(f"  ... and {len(images) - 20} more")
        print("="*70)

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Process existing ComfyUI outputs and publish to Printify'
    )
    parser.add_argument(
        '--count',
        type=int,
        help='Number of images to process (default: all)'
    )
    parser.add_argument(
        '--no-publish',
        action='store_true',
        help='Skip Printify publishing (only create gallery)'
    )
    parser.add_argument(
        '--pattern',
        type=str,
        default='*.png',
        help='File pattern to match (default: *.png)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='ComfyUI output directory (default: ./ComfyUI/output)'
    )

    args = parser.parse_args()

    # Override output directory if specified
    if args.output_dir:
        global COMFYUI_OUTPUT
        COMFYUI_OUTPUT = args.output_dir

    processor = ExistingImageProcessor()
    processor.process(
        count=args.count,
        publish=not args.no_publish,
        pattern=args.pattern
    )

if __name__ == "__main__":
    main()

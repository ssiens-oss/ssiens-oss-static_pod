#!/usr/bin/env python3
"""
Automated ComfyUI Design Generator with Gallery Proof & Publishing

This script:
1. Auto-generates creative prompts with Claude
2. Generates designs with ComfyUI
3. Creates a gallery proof sheet
4. Publishes to Printify
"""

import os
import sys
import requests
import json
import time
from pathlib import Path
from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont
import io

# Configuration
COMFYUI_URL = os.getenv("COMFYUI_API_URL", "http://localhost:8188")
PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

class AutoDesignGenerator:
    def __init__(self):
        self.output_dir = Path("data/designs")
        self.gallery_dir = Path("data/gallery")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.gallery_dir.mkdir(parents=True, exist_ok=True)

    def generate_batch_prompts(self, count: int = 5, theme: str = None) -> List[Dict[str, str]]:
        """Generate multiple creative prompts with Claude"""

        if not ANTHROPIC_API_KEY:
            print("⚠️  ANTHROPIC_API_KEY not set, using default prompts")
            return [
                {"title": f"Design {i+1}", "prompt": f"abstract art design number {i+1}, vibrant colors, modern style"}
                for i in range(count)
            ]

        from anthropic import Anthropic
        client = Anthropic(api_key=ANTHROPIC_API_KEY)

        theme_text = f" with the theme '{theme}'" if theme else ""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Generate {count} unique, creative SDXL prompts for hoodie/t-shirt designs{theme_text}.

Each design should be:
- Bold and eye-catching
- Suitable for print-on-demand
- Unique and commercially viable
- High contrast and visually striking

Return as JSON array with format:
[
  {{"title": "Design Name", "prompt": "detailed SDXL prompt"}},
  ...
]

Return ONLY the JSON array, no other text."""
            }]
        )

        try:
            text = message.content[0].text.strip()
            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]

            prompts = json.loads(text)
            return prompts
        except Exception as e:
            print(f"Error parsing prompts: {e}")
            return [
                {"title": f"Design {i+1}", "prompt": f"creative design {i+1}, artistic style, bold colors"}
                for i in range(count)
            ]

    def queue_comfyui_generation(self, prompt: str, seed: int = None) -> str:
        """Queue a generation in ComfyUI"""

        if seed is None:
            seed = int(time.time() * 1000) % 2147483647

        workflow = {
            "3": {
                "inputs": {
                    "seed": seed,
                    "steps": 30,
                    "cfg": 7.5,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "text, watermark, low quality, blurry, distorted, ugly",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": f"design_{seed}",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }

        response = requests.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow})

        if response.status_code == 200:
            return response.json()["prompt_id"]
        else:
            raise Exception(f"Failed to queue: {response.text}")

    def wait_and_download(self, prompt_id: str, save_path: str, timeout: int = 300) -> bool:
        """Wait for generation and download image"""

        start_time = time.time()

        while time.time() - start_time < timeout:
            response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")

            if response.status_code == 200:
                history = response.json()

                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})

                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            images = node_output["images"]
                            if images:
                                img = images[0]
                                img_url = f"{COMFYUI_URL}/view?filename={img['filename']}&subfolder={img.get('subfolder', '')}&type={img['type']}"

                                # Download
                                img_response = requests.get(img_url)
                                if img_response.status_code == 200:
                                    with open(save_path, 'wb') as f:
                                        f.write(img_response.content)
                                    return True

            time.sleep(2)

        return False

    def create_gallery_proof(self, image_paths: List[str], titles: List[str], output_path: str):
        """Create a gallery proof sheet"""

        print("📸 Creating gallery proof...")

        # Load images
        images = []
        for path in image_paths:
            if os.path.exists(path):
                img = Image.open(path)
                img.thumbnail((512, 512))  # Resize for gallery
                images.append(img)

        if not images:
            print("⚠️  No images to create gallery")
            return

        # Calculate grid dimensions
        cols = min(3, len(images))
        rows = (len(images) + cols - 1) // cols

        # Create gallery
        cell_width = 512
        cell_height = 600  # Extra space for title
        gallery_width = cols * cell_width + (cols + 1) * 20
        gallery_height = rows * cell_height + (rows + 1) * 20

        gallery = Image.new('RGB', (gallery_width, gallery_height), color='white')
        draw = ImageDraw.Draw(gallery)

        # Try to use a better font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()
            small_font = font

        # Place images
        for idx, (img, title) in enumerate(zip(images, titles)):
            row = idx // cols
            col = idx % cols

            x = col * cell_width + (col + 1) * 20
            y = row * cell_height + (row + 1) * 20

            # Paste image
            gallery.paste(img, (x, y))

            # Draw title
            text_y = y + 512 + 10
            draw.text((x + 10, text_y), title, fill='black', font=font)

            # Draw index
            draw.text((x + 10, text_y + 35), f"Design #{idx + 1}", fill='gray', font=small_font)

        # Add header
        header_height = 80
        new_gallery = Image.new('RGB', (gallery_width, gallery_height + header_height), color='#2c3e50')
        new_gallery.paste(gallery, (0, header_height))

        draw = ImageDraw.Draw(new_gallery)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except:
            title_font = font

        draw.text((20, 20), f"Design Gallery Proof - {timestamp}", fill='white', font=title_font)

        # Save
        new_gallery.save(output_path, quality=95)
        print(f"✅ Gallery saved: {output_path}")

    def publish_to_printify(self, image_path: str, title: str, price: float = 39.99) -> Dict:
        """Publish design to Printify"""

        if not PRINTIFY_API_KEY or not PRINTIFY_SHOP_ID:
            print(f"⚠️  Skipping Printify upload for: {title}")
            return None

        headers = {"Authorization": f"Bearer {PRINTIFY_API_KEY}"}

        # Upload image
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            response = requests.post(
                "https://api.printify.com/v1/uploads/images.json",
                headers=headers,
                files=files
            )

            if response.status_code != 200:
                print(f"❌ Failed to upload {title}: {response.text}")
                return None

            image_id = response.json()["id"]

        # Create product
        product_data = {
            "title": title,
            "description": f"Unique {title} design created with AI. Premium quality heavyweight hoodie.",
            "blueprint_id": 77,  # Heavy Blend Hoodie
            "print_provider_id": 99,
            "variants": [
                {"id": vid, "price": int(price * 100), "is_enabled": True}
                for vid in [45740, 45741, 45742, 45743, 45744]  # S, M, L, XL, 2XL
            ],
            "print_areas": [{
                "variant_ids": [45740, 45741, 45742, 45743, 45744],
                "placeholders": [{
                    "position": "front",
                    "images": [{"id": image_id, "x": 0.5, "y": 0.5, "scale": 1.0, "angle": 0}]
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
            print(f"✅ Published: {title} (ID: {product['id']})")
            return product
        else:
            print(f"❌ Failed to publish {title}: {response.text}")
            return None

    def run(self, count: int = 5, theme: str = None, publish: bool = True):
        """Run the complete workflow"""

        print("🚀 Auto Design Generator Starting...\n")
        print(f"Generating {count} designs{f' with theme: {theme}' if theme else ''}\n")

        # Generate prompts
        print("🤖 Generating creative prompts with Claude...")
        prompts = self.generate_batch_prompts(count, theme)
        print(f"✅ Generated {len(prompts)} prompts\n")

        # Generate images
        print("🎨 Generating designs with ComfyUI...")
        generated_images = []

        for idx, design in enumerate(prompts):
            title = design['title']
            prompt = design['prompt']

            print(f"\n[{idx + 1}/{len(prompts)}] {title}")
            print(f"Prompt: {prompt[:80]}...")

            # Queue generation
            prompt_id = self.queue_comfyui_generation(prompt, seed=int(time.time() * 1000) + idx)

            # Save path
            timestamp = int(time.time())
            filename = f"design_{timestamp}_{idx}.png"
            save_path = self.output_dir / filename

            # Wait and download
            print("   Generating...")
            success = self.wait_and_download(prompt_id, str(save_path))

            if success:
                print(f"   ✅ Saved: {save_path}")
                generated_images.append({
                    'path': str(save_path),
                    'title': title,
                    'prompt': prompt
                })
            else:
                print(f"   ❌ Failed to generate")

        if not generated_images:
            print("\n❌ No images generated")
            return

        print(f"\n✅ Generated {len(generated_images)} designs\n")

        # Create gallery proof
        gallery_path = self.gallery_dir / f"gallery_{int(time.time())}.png"
        self.create_gallery_proof(
            [img['path'] for img in generated_images],
            [img['title'] for img in generated_images],
            str(gallery_path)
        )

        print(f"\n📸 Gallery proof: {gallery_path}\n")

        # Publish to Printify
        if publish and (PRINTIFY_API_KEY and PRINTIFY_SHOP_ID):
            print("📤 Publishing to Printify...")

            published = []
            for design in generated_images:
                product = self.publish_to_printify(design['path'], design['title'])
                if product:
                    published.append(product)
                time.sleep(1)  # Rate limiting

            print(f"\n✅ Published {len(published)}/{len(generated_images)} products")
        else:
            print("\n⚠️  Skipping Printify publishing (configure PRINTIFY_API_KEY and PRINTIFY_SHOP_ID)")

        # Summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        print(f"Generated designs: {len(generated_images)}")
        print(f"Gallery proof: {gallery_path}")
        print(f"Designs location: {self.output_dir}/")
        print("\nGenerated designs:")
        for idx, design in enumerate(generated_images):
            print(f"  {idx + 1}. {design['title']}")
        print("="*60)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Auto-generate designs with ComfyUI')
    parser.add_argument('--count', type=int, default=5, help='Number of designs to generate')
    parser.add_argument('--theme', type=str, help='Design theme (optional)')
    parser.add_argument('--no-publish', action='store_true', help='Skip Printify publishing')

    args = parser.parse_args()

    generator = AutoDesignGenerator()
    generator.run(count=args.count, theme=args.theme, publish=not args.no_publish)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate designs with ComfyUI and upload to Printify
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
COMFYUI_URL = os.getenv("COMFYUI_API_URL", "http://localhost:8188")
PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def generate_prompt_with_claude(theme: str) -> str:
    """Generate a creative prompt using Claude"""
    if not ANTHROPIC_API_KEY:
        print("⚠️  ANTHROPIC_API_KEY not set, using default prompt")
        return f"A vibrant, artistic design featuring {theme}, bold colors, graphic art style, suitable for a hoodie print"

    from anthropic import Anthropic
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"Generate a detailed SDXL prompt for a hoodie design with the theme: {theme}. The design should be bold, eye-catching, and suitable for print-on-demand. Return only the prompt, no other text."
        }]
    )

    return message.content[0].text

def queue_comfyui_prompt(prompt: str) -> str:
    """Queue a prompt in ComfyUI and return the prompt_id"""

    # Simple workflow for SDXL
    workflow = {
        "3": {
            "inputs": {
                "seed": int(time.time()),
                "steps": 30,
                "cfg": 7.0,
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
                "text": "text, watermark, low quality, blurry, distorted",
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
                "filename_prefix": "ComfyUI",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }

    response = requests.post(
        f"{COMFYUI_URL}/prompt",
        json={"prompt": workflow}
    )

    if response.status_code == 200:
        return response.json()["prompt_id"]
    else:
        raise Exception(f"Failed to queue prompt: {response.text}")

def wait_for_comfyui_completion(prompt_id: str, timeout: int = 300) -> str:
    """Wait for ComfyUI to complete and return the image path"""
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
                            # Return the first image
                            img = images[0]
                            return f"{COMFYUI_URL}/view?filename={img['filename']}&subfolder={img.get('subfolder', '')}&type={img['type']}"

        time.sleep(2)

    raise Exception(f"Timeout waiting for ComfyUI completion")

def download_image(url: str, save_path: str):
    """Download image from URL"""
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return save_path
    else:
        raise Exception(f"Failed to download image: {response.status_code}")

def upload_to_printify(image_path: str, title: str, description: str, price: float = 39.99):
    """Upload design to Printify and create hoodie product"""

    if not PRINTIFY_API_KEY or not PRINTIFY_SHOP_ID:
        print("⚠️  Printify credentials not configured. Skipping upload.")
        print(f"   Generated image saved at: {image_path}")
        return None

    headers = {
        "Authorization": f"Bearer {PRINTIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    # Upload image
    print("📤 Uploading image to Printify...")

    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/png')}

        response = requests.post(
            "https://api.printify.com/v1/uploads/images.json",
            headers={"Authorization": f"Bearer {PRINTIFY_API_KEY}"},
            files=files
        )

        if response.status_code != 200:
            raise Exception(f"Failed to upload image: {response.text}")

        image_id = response.json()["id"]
        print(f"✅ Image uploaded: {image_id}")

    # Create hoodie product (Gildan 18500 - Heavy Blend Hoodie)
    print("👕 Creating hoodie product...")

    product_data = {
        "title": title,
        "description": description,
        "blueprint_id": 77,  # Heavy Blend Hoodie
        "print_provider_id": 99,  # MonsterDigital
        "variants": [
            {
                "id": 45740,  # S
                "price": int(price * 100),
                "is_enabled": True
            },
            {
                "id": 45741,  # M
                "price": int(price * 100),
                "is_enabled": True
            },
            {
                "id": 45742,  # L
                "price": int(price * 100),
                "is_enabled": True
            },
            {
                "id": 45743,  # XL
                "price": int(price * 100),
                "is_enabled": True
            },
            {
                "id": 45744,  # 2XL
                "price": int(price * 100),
                "is_enabled": True
            }
        ],
        "print_areas": [
            {
                "variant_ids": [45740, 45741, 45742, 45743, 45744],
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": image_id,
                                "x": 0.5,
                                "y": 0.5,
                                "scale": 1.0,
                                "angle": 0
                            }
                        ]
                    }
                ]
            }
        ]
    }

    response = requests.post(
        f"https://api.printify.com/v1/shops/{PRINTIFY_SHOP_ID}/products.json",
        headers=headers,
        json=product_data
    )

    if response.status_code == 200:
        product = response.json()
        print(f"✅ Hoodie created! Product ID: {product['id']}")
        return product
    else:
        raise Exception(f"Failed to create product: {response.text}")

def main():
    """Main workflow"""

    print("🎨 ComfyUI to Printify Hoodie Generator\n")

    # Get theme from args or use default
    theme = sys.argv[1] if len(sys.argv) > 1 else "abstract geometric patterns"

    print(f"Theme: {theme}\n")

    # Generate prompt
    print("🤖 Generating creative prompt with Claude...")
    prompt = generate_prompt_with_claude(theme)
    print(f"Prompt: {prompt}\n")

    # Generate image with ComfyUI
    print("🎨 Generating image with ComfyUI...")
    prompt_id = queue_comfyui_prompt(prompt)
    print(f"Queued: {prompt_id}")

    image_url = wait_for_comfyui_completion(prompt_id)
    print(f"✅ Image generated: {image_url}\n")

    # Download image
    output_dir = Path("data/designs")
    output_dir.mkdir(parents=True, exist_ok=True)

    image_path = output_dir / f"hoodie_{int(time.time())}.png"
    download_image(image_url, str(image_path))
    print(f"💾 Saved: {image_path}\n")

    # Upload to Printify
    title = f"{theme.title()} Hoodie"
    description = f"Unique {theme} design created with AI. Premium quality heavyweight hoodie."

    product = upload_to_printify(str(image_path), title, description)

    if product:
        print(f"\n✅ Complete! Hoodie created on Printify")
        print(f"   Product ID: {product['id']}")
        print(f"   Title: {product['title']}")
    else:
        print(f"\n✅ Image generated and saved: {image_path}")
        print("   Configure Printify credentials in .env to auto-upload")

if __name__ == "__main__":
    main()

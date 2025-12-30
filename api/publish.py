"""
Unified Publish Orchestrator
Manages the full pipeline: Generate → Mockup → Upload → Publish
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import requests

from api.pricing import price_product
from api.validators import validate_product

DATA_DIR = Path(__file__).parent.parent / "data"

def publish_product(product_data):
    """
    Orchestrate full product publication pipeline

    Steps:
    1. Generate design (via ComfyUI worker)
    2. Create mockups (hoodie/tee templates)
    3. Upload to Printify
    4. Publish to Shopify
    5. Sync to TikTok Shop

    Returns:
        dict: Publication result with SKUs and URLs
    """

    # Generate unique SKU
    sku = generate_sku(product_data)
    product_data["sku"] = sku

    # Step 1: Generate design
    design_path = generate_design(product_data)
    product_data["design_path"] = str(design_path)

    # Step 2: Create mockups
    mockups = create_mockups(product_data, design_path)
    product_data["mockups"] = mockups

    # Step 3: Upload to Printify
    printify_id = upload_to_printify(product_data)
    product_data["printify_id"] = printify_id

    # Step 4: Publish to Shopify
    shopify_id = publish_to_shopify(product_data)
    product_data["shopify_id"] = shopify_id

    # Step 5: Sync to TikTok Shop
    tiktok_id = sync_to_tiktok(product_data)
    product_data["tiktok_id"] = tiktok_id

    # Log successful publication
    log_publication(product_data)

    return {
        "sku": sku,
        "printify_id": printify_id,
        "shopify_id": shopify_id,
        "tiktok_id": tiktok_id,
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_sku(product_data):
    """Generate unique SKU"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    product_type = product_data.get("type", "product")[:3].upper()
    return f"SW-{product_type}-{timestamp}"

def generate_design(product_data):
    """
    Trigger ComfyUI worker to generate design
    In production, this calls the ComfyUI API
    """
    design_dir = DATA_DIR / "designs"
    design_dir.mkdir(parents=True, exist_ok=True)

    # For now, create placeholder
    # In production, this would call ComfyUI worker
    design_path = design_dir / f"{product_data['sku']}.png"

    # Mock: In production this would be actual ComfyUI generation
    # comfy_result = requests.post("http://localhost:8188/prompt", json={
    #     "prompt": product_data.get("prompt", ""),
    #     "workflow": "standard"
    # })

    # Placeholder for now
    design_path.touch()

    return design_path

def create_mockups(product_data, design_path):
    """
    Create product mockups (hoodie, tee, poster)
    Calls mockup worker
    """
    mockup_types = ["hoodie", "tee", "poster"]
    mockups = []

    for mockup_type in mockup_types:
        mockup_path = DATA_DIR / "designs" / f"{product_data['sku']}_{mockup_type}.png"

        # In production, this calls mockup worker
        # mockup_result = requests.post("http://localhost:5001/create_mockup", json={
        #     "design_path": str(design_path),
        #     "template": mockup_type
        # })

        mockup_path.touch()
        mockups.append({
            "type": mockup_type,
            "path": str(mockup_path)
        })

    return mockups

def upload_to_printify(product_data):
    """
    Upload product to Printify
    """
    api_key = os.environ.get("PRINTIFY_API_KEY")
    shop_id = os.environ.get("PRINTIFY_SHOP_ID")

    if not api_key or not shop_id:
        # Mock mode for development
        return f"printify_mock_{product_data['sku']}"

    # Production Printify API call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": product_data["title"],
        "description": product_data.get("description", ""),
        "blueprint_id": 384,  # Hoodie
        "print_provider_id": 99,
        "variants": [
            {
                "id": 17390,
                "price": int(product_data["price"] * 100)
            }
        ],
        "print_areas": [
            {
                "variant_ids": [17390],
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": "upload_image_id",
                                "x": 0.5,
                                "y": 0.5,
                                "scale": 1,
                                "angle": 0
                            }
                        ]
                    }
                ]
            }
        ]
    }

    # response = requests.post(
    #     f"https://api.printify.com/v1/shops/{shop_id}/products.json",
    #     headers=headers,
    #     json=payload
    # )

    return f"printify_mock_{product_data['sku']}"

def publish_to_shopify(product_data):
    """
    Publish product to Shopify store
    """
    api_key = os.environ.get("SHOPIFY_API_KEY")
    store = os.environ.get("SHOPIFY_STORE")

    if not api_key or not store:
        return f"shopify_mock_{product_data['sku']}"

    # Production Shopify API call
    # headers = {
    #     "X-Shopify-Access-Token": api_key,
    #     "Content-Type": "application/json"
    # }

    # payload = {
    #     "product": {
    #         "title": product_data["title"],
    #         "body_html": product_data.get("description", ""),
    #         "vendor": "StaticWaves",
    #         "product_type": product_data.get("type", "Apparel"),
    #         "status": "active"
    #     }
    # }

    return f"shopify_mock_{product_data['sku']}"

def sync_to_tiktok(product_data):
    """
    Sync product to TikTok Shop
    """
    shop_id = os.environ.get("TIKTOK_SHOP_ID")

    if not shop_id:
        return f"tiktok_mock_{product_data['sku']}"

    # Production TikTok Shop API call
    return f"tiktok_mock_{product_data['sku']}"

def log_publication(product_data):
    """Log successful publication"""
    log_dir = DATA_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"publications_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"

    with open(log_file, "a") as f:
        json.dump({
            "timestamp": datetime.utcnow().isoformat(),
            "sku": product_data["sku"],
            "title": product_data["title"],
            "price": product_data["price"]
        }, f)
        f.write("\n")

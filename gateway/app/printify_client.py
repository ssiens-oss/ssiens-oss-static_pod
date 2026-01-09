"""
Printify API Client
Handles product creation and publishing
"""
import requests
from typing import Dict, Optional

PRINTIFY_API = "https://api.printify.com/v1"

class PrintifyClient:
    def __init__(self, api_key: str, shop_id: str):
        if not api_key or not shop_id:
            raise RuntimeError("Printify API key or Shop ID missing")

        self.api_key = api_key
        self.shop_id = shop_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def upload_image(self, image_path: str, filename: str) -> Optional[str]:
        """Upload image to Printify and return image ID"""
        try:
            # First, upload the image file
            with open(image_path, "rb") as f:
                files = {"file": (filename, f, "image/png")}
                r = requests.post(
                    f"{PRINTIFY_API}/uploads/images.json",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files=files
                )

            if not r.ok:
                print(f"Upload error: {r.status_code} - {r.text}")
                return None

            return r.json().get("id")
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None

    def create_product(
        self,
        title: str,
        image_id: str,
        blueprint_id: int,
        provider_id: int,
        price: int = 1999  # $19.99 in cents
    ) -> Optional[Dict]:
        """Create a product with uploaded image"""
        try:
            payload = {
                "title": title,
                "description": title,
                "blueprint_id": blueprint_id,
                "print_provider_id": provider_id,
                "variants": [
                    {"id": 17390, "price": price, "is_enabled": True},  # S
                    {"id": 17426, "price": price, "is_enabled": True},  # M
                    {"id": 17428, "price": price, "is_enabled": True},  # L
                    {"id": 17430, "price": price, "is_enabled": True},  # XL
                    {"id": 17432, "price": price, "is_enabled": True},  # 2XL
                ],
                "print_areas": [{
                    "variant_ids": [17390, 17426, 17428, 17430, 17432],
                    "placeholders": [{
                        "position": "front",
                        "images": [{
                            "id": image_id,
                            "x": 0.5,
                            "y": 0.5,
                            "scale": 1,
                            "angle": 0
                        }]
                    }]
                }]
            }

            r = requests.post(
                f"{PRINTIFY_API}/shops/{self.shop_id}/products.json",
                headers=self.headers,
                json=payload
            )

            if not r.ok:
                print(f"Create product error: {r.status_code} - {r.text}")
                return None

            return r.json()
        except Exception as e:
            print(f"Error creating product: {e}")
            return None

    def publish_product(self, product_id: str) -> bool:
        """Publish product to connected sales channels"""
        try:
            r = requests.post(
                f"{PRINTIFY_API}/shops/{self.shop_id}/products/{product_id}/publish.json",
                headers=self.headers,
                json={
                    "title": True,
                    "description": True,
                    "images": True,
                    "variants": True,
                    "tags": True
                }
            )
            return r.ok
        except Exception as e:
            print(f"Error publishing product: {e}")
            return False

    def create_and_publish(
        self,
        image_path: str,
        title: str,
        blueprint_id: int,
        provider_id: int
    ) -> Optional[str]:
        """Full workflow: upload image, create product, publish"""
        # Upload image
        image_id = self.upload_image(image_path, title)
        if not image_id:
            return None

        # Create product
        product = self.create_product(title, image_id, blueprint_id, provider_id)
        if not product:
            return None

        product_id = product.get("id")
        if not product_id:
            return None

        # Publish
        if not self.publish_product(product_id):
            print(f"Warning: Product {product_id} created but not published")

        return product_id

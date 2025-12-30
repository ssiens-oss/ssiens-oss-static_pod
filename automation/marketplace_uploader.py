"""
Marketplace Uploader - CLI tool for uploading to Gumroad and Itch.io
Automates product creation and file uploads
"""

import requests
import logging
from typing import Dict, List, Optional
from pathlib import Path
from config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GumroadUploader:
    """Uploads products to Gumroad"""

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or config.marketplace.gumroad_access_token
        self.base_url = "https://api.gumroad.com/v2"

    def create_product(
        self,
        name: str,
        description: str,
        price: int,  # Price in cents
        file_path: Path,
        tags: Optional[List[str]] = None,
        custom_permalink: Optional[str] = None
    ) -> Optional[Dict]:
        """Create a new product on Gumroad"""
        logger.info(f"Creating Gumroad product: {name}")

        url = f"{self.base_url}/products"

        # Product data
        data = {
            "access_token": self.access_token,
            "name": name,
            "description": description,
            "price": price,
            "custom_permalink": custom_permalink or name.lower().replace(" ", "-")
        }

        # Add tags if provided
        if tags:
            data["tags"] = ",".join(tags)

        try:
            # Step 1: Create product
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            product = response.json()

            if not product.get("success"):
                logger.error(f"Failed to create product: {product}")
                return None

            product_id = product["product"]["id"]
            logger.info(f"Product created: {product_id}")

            # Step 2: Upload file
            if file_path.exists():
                upload_success = self._upload_file(product_id, file_path)
                if not upload_success:
                    logger.warning("Product created but file upload failed")

            # Step 3: Publish product
            self._publish_product(product_id)

            logger.info(f"✓ Gumroad product published: {product['product']['short_url']}")
            return product["product"]

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create Gumroad product: {e}")
            return None

    def _upload_file(self, product_id: str, file_path: Path) -> bool:
        """Upload file to existing product"""
        logger.info(f"Uploading file: {file_path.name}")

        url = f"{self.base_url}/products/{product_id}/files"

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f)}
                data = {'access_token': self.access_token}

                response = requests.post(url, data=data, files=files, timeout=120)
                response.raise_for_status()

                result = response.json()
                if result.get("success"):
                    logger.info("File uploaded successfully")
                    return True
                else:
                    logger.error(f"File upload failed: {result}")
                    return False

        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return False

    def _publish_product(self, product_id: str) -> bool:
        """Publish (enable) a product"""
        url = f"{self.base_url}/products/{product_id}/enable"

        try:
            data = {'access_token': self.access_token}
            response = requests.put(url, data=data, timeout=30)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                logger.info("Product published")
                return True
            else:
                logger.error(f"Failed to publish: {result}")
                return False

        except Exception as e:
            logger.error(f"Failed to publish product: {e}")
            return False

    def list_products(self) -> List[Dict]:
        """List all products"""
        url = f"{self.base_url}/products"

        try:
            params = {'access_token': self.access_token}
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                return result.get("products", [])
            return []

        except Exception as e:
            logger.error(f"Failed to list products: {e}")
            return []


class ItchioUploader:
    """Uploads games/assets to Itch.io"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.marketplace.itchio_api_key
        self.base_url = "https://itch.io/api/1"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def create_game(
        self,
        title: str,
        short_text: str,
        description: str,
        classification: str = "assets",  # "game" or "assets"
        kind: str = "default",  # "default", "flash", "unity", "java", "html"
        price: int = 0,  # Price in cents (0 for free)
        tags: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Create a new game/asset project on Itch.io"""
        logger.info(f"Creating Itch.io project: {title}")

        url = f"{self.base_url}/{self.get_username()}/games"

        data = {
            "title": title,
            "short_text": short_text,
            "body": description,
            "classification": classification,
            "kind": kind,
            "type": "default"
        }

        # Set pricing
        if price > 0:
            data["sale_status"] = "paid"
            data["min_price"] = price
        else:
            data["sale_status"] = "free"

        # Add tags
        if tags:
            data["tags"] = tags

        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            game = response.json()

            logger.info(f"✓ Itch.io project created: {game.get('id')}")
            return game

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create Itch.io project: {e}")
            return None

    def upload_file(
        self,
        game_id: int,
        file_path: Path,
        channel: str = "default"
    ) -> bool:
        """Upload file to existing game/asset using butler CLI"""
        logger.info(f"Uploading to Itch.io via butler: {file_path.name}")

        try:
            # Note: This requires butler CLI to be installed
            # Installation: https://itch.io/docs/butler/
            import subprocess

            username = self.get_username()
            game_url = f"{username}/{game_id}"

            # Use butler to push file
            cmd = [
                "butler",
                "push",
                str(file_path),
                game_url + ":" + channel,
                "--userversion-file", str(file_path) + ".version"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                logger.info("✓ File uploaded via butler")
                return True
            else:
                logger.error(f"Butler upload failed: {result.stderr}")
                return False

        except FileNotFoundError:
            logger.error("Butler CLI not found. Install from: https://itch.io/docs/butler/")
            return False
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return False

    def get_username(self) -> str:
        """Get authenticated username"""
        url = f"{self.base_url}/profile"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            profile = response.json()
            return profile.get("user", {}).get("username", "unknown")

        except Exception as e:
            logger.error(f"Failed to get username: {e}")
            return "unknown"

    def list_games(self) -> List[Dict]:
        """List all games/assets"""
        url = f"{self.base_url}/{self.get_username()}/games"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get("games", [])

        except Exception as e:
            logger.error(f"Failed to list games: {e}")
            return []


class MarketplaceUploader:
    """Unified uploader for multiple marketplaces"""

    def __init__(self):
        self.gumroad = GumroadUploader()
        self.itchio = ItchioUploader()

    def upload_to_all(
        self,
        title: str,
        short_description: str,
        long_description: str,
        file_path: Path,
        price_usd: float = 0,
        tags: Optional[List[str]] = None,
        marketplaces: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """Upload to multiple marketplaces"""
        logger.info("=" * 60)
        logger.info(f"Uploading: {title}")
        logger.info("=" * 60)

        marketplaces = marketplaces or ["gumroad", "itchio"]
        price_cents = int(price_usd * 100)

        results = {}

        # Upload to Gumroad
        if "gumroad" in marketplaces:
            logger.info("\n[Gumroad]")
            gumroad_product = self.gumroad.create_product(
                name=title,
                description=long_description,
                price=price_cents,
                file_path=file_path,
                tags=tags
            )
            results["gumroad"] = gumroad_product is not None

        # Upload to Itch.io
        if "itchio" in marketplaces:
            logger.info("\n[Itch.io]")
            itchio_game = self.itchio.create_game(
                title=title,
                short_text=short_description,
                description=long_description,
                price=price_cents,
                tags=tags
            )

            if itchio_game:
                # Upload file using butler
                game_id = itchio_game.get("id")
                upload_success = self.itchio.upload_file(game_id, file_path)
                results["itchio"] = upload_success
            else:
                results["itchio"] = False

        logger.info("\n" + "=" * 60)
        logger.info("Upload Summary")
        logger.info("=" * 60)
        for marketplace, success in results.items():
            status = "✓" if success else "✗"
            logger.info(f"{status} {marketplace.capitalize()}: {'Success' if success else 'Failed'}")
        logger.info("=" * 60)

        return results


def main():
    """Example usage"""
    uploader = MarketplaceUploader()

    # Example listing data (would come from listing_generator.py)
    title = "Fantasy Potion Icons – Hand-Painted RPG UI Pack"
    short_desc = "32 vibrant potion icons perfect for RPG games and fantasy UIs"
    long_desc = """Transform your game's UI with these stunning hand-painted potion icons!

This pack includes 32 unique magical potion designs featuring:
- Vibrant, eye-catching colors
- Transparent backgrounds (PNG)
- High resolution (512x512px)
- Perfect for RPG, fantasy, and adventure games

Each icon is carefully crafted to stand out in your game's inventory, shop, or HUD."""

    file_path = Path("./archives/fantasy_potion_pack.zip")
    tags = ["gamedev", "icons", "rpg", "ui", "fantasy", "2d"]

    # Upload to all marketplaces
    if file_path.exists():
        results = uploader.upload_to_all(
            title=title,
            short_description=short_desc,
            long_description=long_desc,
            file_path=file_path,
            price_usd=4.99,
            tags=tags,
            marketplaces=["gumroad"]  # Add "itchio" when butler is installed
        )

        if any(results.values()):
            print("\n✓ Successfully uploaded to at least one marketplace!")
        else:
            print("\n✗ All uploads failed")
    else:
        print(f"✗ File not found: {file_path}")


if __name__ == "__main__":
    main()

"""
Marketplace Store
Browse and purchase presets, voices, and other assets
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Asset:
    """Marketplace asset"""
    id: str
    name: str
    type: str  # preset, voice, midi, persona, battle_theme
    creator_id: str
    creator_name: str
    price_tokens: int  # Price in compute tokens or access tokens
    description: str
    tags: List[str]
    downloads: int = 0
    rating: float = 0.0


class MarketplaceStore:
    """Main marketplace interface"""

    def __init__(self, data_dir: str = "marketplace_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self.assets_file = os.path.join(data_dir, "assets.json")
        self.assets = self._load_assets()

    def list_assets(
        self,
        asset_type: Optional[str] = None,
        creator_id: Optional[str] = None
    ) -> List[Asset]:
        """
        List marketplace assets

        Args:
            asset_type: Filter by type
            creator_id: Filter by creator

        Returns:
            List of assets
        """
        results = self.assets

        if asset_type:
            results = [a for a in results if a.type == asset_type]

        if creator_id:
            results = [a for a in results if a.creator_id == creator_id]

        return results

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """Get specific asset"""
        for asset in self.assets:
            if asset.id == asset_id:
                return asset
        return None

    def upload_asset(self, asset: Asset) -> str:
        """
        Upload new asset to marketplace

        Args:
            asset: Asset to upload

        Returns:
            Asset ID
        """
        # Add to store
        self.assets.append(asset)
        self._save_assets()

        print(f"✓ Asset uploaded: {asset.name} by {asset.creator_name}")

        return asset.id

    def purchase_asset(
        self,
        user_id: str,
        asset_id: str,
        balance: int
    ) -> Dict:
        """
        Purchase an asset

        Args:
            user_id: Buyer user ID
            asset_id: Asset to purchase
            balance: User's token balance

        Returns:
            Purchase result
        """
        asset = self.get_asset(asset_id)

        if not asset:
            return {"success": False, "error": "Asset not found"}

        if balance < asset.price_tokens:
            return {"success": False, "error": "Insufficient tokens"}

        # Record purchase
        purchase_record = {
            "user_id": user_id,
            "asset_id": asset_id,
            "price_paid": asset.price_tokens,
            "timestamp": self._timestamp()
        }

        self._record_purchase(purchase_record)

        # Update asset stats
        asset.downloads += 1
        self._save_assets()

        print(f"✓ Purchase complete: {asset.name}")

        return {
            "success": True,
            "asset": asdict(asset),
            "tokens_spent": asset.price_tokens,
            "remaining_balance": balance - asset.price_tokens
        }

    def _load_assets(self) -> List[Asset]:
        """Load assets from disk"""
        if not os.path.exists(self.assets_file):
            return []

        with open(self.assets_file, 'r') as f:
            data = json.load(f)

        return [Asset(**item) for item in data]

    def _save_assets(self):
        """Save assets to disk"""
        data = [asdict(a) for a in self.assets]

        with open(self.assets_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _record_purchase(self, record: Dict):
        """Record purchase transaction"""
        purchases_file = os.path.join(self.data_dir, "purchases.json")

        purchases = []
        if os.path.exists(purchases_file):
            with open(purchases_file, 'r') as f:
                purchases = json.load(f)

        purchases.append(record)

        with open(purchases_file, 'w') as f:
            json.dump(purchases, f, indent=2)

    def _timestamp(self) -> float:
        """Get current timestamp"""
        import time
        return time.time()

"""
Asset Manager
Handles asset files (presets, voices, MIDI, etc.)
"""

import os
import json
import hashlib
from typing import Dict, Optional


class AssetManager:
    """Manages marketplace asset files"""

    def __init__(self, assets_dir: str = "marketplace_assets"):
        self.assets_dir = assets_dir
        os.makedirs(assets_dir, exist_ok=True)

    def store_asset_file(
        self,
        file_path: str,
        asset_id: str,
        asset_type: str
    ) -> str:
        """
        Store asset file securely

        Args:
            file_path: Source file path
            asset_id: Asset ID
            asset_type: Asset type

        Returns:
            Stored file path
        """
        # Create type directory
        type_dir = os.path.join(self.assets_dir, asset_type)
        os.makedirs(type_dir, exist_ok=True)

        # Copy file
        import shutil
        ext = os.path.splitext(file_path)[1]
        dest_path = os.path.join(type_dir, f"{asset_id}{ext}")

        shutil.copy(file_path, dest_path)

        # Generate checksum
        checksum = self._calculate_checksum(dest_path)

        # Store metadata
        metadata = {
            "asset_id": asset_id,
            "file_path": dest_path,
            "checksum": checksum,
            "type": asset_type
        }

        metadata_path = os.path.join(type_dir, f"{asset_id}.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Asset file stored: {dest_path}")

        return dest_path

    def get_asset_file(self, asset_id: str) -> Optional[str]:
        """Get asset file path"""
        # Search in all type directories
        for type_dir in os.listdir(self.assets_dir):
            type_path = os.path.join(self.assets_dir, type_dir)

            if not os.path.isdir(type_path):
                continue

            metadata_path = os.path.join(type_path, f"{asset_id}.json")

            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)

                return metadata.get("file_path")

        return None

    def verify_asset(self, asset_id: str) -> bool:
        """Verify asset file integrity"""
        file_path = self.get_asset_file(asset_id)

        if not file_path or not os.path.exists(file_path):
            return False

        # Get stored checksum
        type_dir = os.path.dirname(file_path)
        metadata_path = os.path.join(type_dir, f"{asset_id}.json")

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        stored_checksum = metadata.get("checksum")

        # Calculate current checksum
        current_checksum = self._calculate_checksum(file_path)

        return stored_checksum == current_checksum

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum"""
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)

        return sha256.hexdigest()

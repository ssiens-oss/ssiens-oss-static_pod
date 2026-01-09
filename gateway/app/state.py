"""
State Management
Tracks image approval and publish status with atomic writes
"""
import json
import os
from typing import Dict, List
from pathlib import Path
import threading

class StateManager:
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.lock = threading.Lock()
        self.state = self._load()

    def _load(self) -> Dict:
        """Load state from disk"""
        if not os.path.exists(self.state_file):
            return {"images": {}}

        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading state: {e}")
            return {"images": {}}

    def _save(self) -> None:
        """Atomically save state to disk"""
        temp_file = f"{self.state_file}.tmp"
        try:
            with open(temp_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            os.replace(temp_file, self.state_file)
        except Exception as e:
            print(f"Error saving state: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def get_image_status(self, image_id: str) -> str:
        """Get status: pending, approved, rejected, publishing, published, failed"""
        with self.lock:
            return self.state["images"].get(image_id, {}).get("status", "pending")

    def set_image_status(self, image_id: str, status: str, metadata: Dict = None) -> None:
        """Set image status with optional metadata"""
        with self.lock:
            if image_id not in self.state["images"]:
                self.state["images"][image_id] = {}

            self.state["images"][image_id]["status"] = status

            if metadata:
                self.state["images"][image_id].update(metadata)

            self._save()

    def get_images_by_status(self, status: str) -> List[str]:
        """Get all image IDs with given status"""
        with self.lock:
            return [
                img_id for img_id, data in self.state["images"].items()
                if data.get("status") == status
            ]

    def get_all_images(self) -> Dict:
        """Get full state dict"""
        with self.lock:
            return self.state["images"].copy()

    def add_image(self, image_id: str, filename: str, path: str) -> None:
        """Register a new image"""
        with self.lock:
            self.state["images"][image_id] = {
                "filename": filename,
                "path": path,
                "status": "pending"
            }
            self._save()

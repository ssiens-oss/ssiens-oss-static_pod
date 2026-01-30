"""
Image Service

Handles image storage, retrieval, and status management.
"""
import base64
import logging
import requests
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.state import StateManager, ImageStatus, StateManagerError

logger = logging.getLogger(__name__)


class ImageService:
    """Service for managing images"""

    def __init__(
        self,
        image_dir: str,
        state_manager: StateManager,
        comfyui_url: Optional[str] = None
    ):
        """
        Initialize image service.

        Args:
            image_dir: Directory for storing images
            state_manager: State manager for tracking status
            comfyui_url: Optional ComfyUI URL for downloading images
        """
        self.image_dir = Path(image_dir)
        self.state_manager = state_manager
        self.comfyui_url = comfyui_url

        # Ensure directory exists
        self.image_dir.mkdir(parents=True, exist_ok=True)

    def list_images(self) -> List[Dict[str, Any]]:
        """
        List all images with their status.

        Returns:
            List of image dictionaries
        """
        images = []
        state = self.state_manager.get_all_images()

        for img_file in self.image_dir.glob("*.png"):
            img_id = img_file.stem
            img_state = state.get(img_id, {})
            status = img_state.get("status", ImageStatus.PENDING.value)

            # Register if new
            if img_id not in state:
                try:
                    self.state_manager.add_image(img_id, img_file.name, str(img_file))
                except StateManagerError as e:
                    logger.error(f"Failed to add image {img_id}: {e}")
                    continue

            images.append({
                "id": img_id,
                "filename": img_file.name,
                "status": status,
                "path": f"/api/image/{img_id}",
                "created_at": img_state.get("created_at"),
                "updated_at": img_state.get("updated_at"),
                "error_message": img_state.get("error_message"),
                "product_id": img_state.get("product_id"),
                "title": img_state.get("title")
            })

        # Sort by filename (newest first)
        images.sort(key=lambda x: x["filename"], reverse=True)
        return images

    def get_image_path(self, image_id: str) -> Optional[Path]:
        """
        Get the path to an image file.

        Args:
            image_id: Image identifier

        Returns:
            Path to image or None if not found
        """
        path = self.image_dir / f"{image_id}.png"
        return path if path.exists() else None

    def save_from_data(
        self,
        image_data: str,
        filename: Optional[str] = None
    ) -> Optional[Tuple[str, str]]:
        """
        Save an image from base64 data or URL.

        Args:
            image_data: Base64 string or URL
            filename: Optional custom filename

        Returns:
            Tuple of (image_id, file_path) or None on failure
        """
        image_id = f"generated_{uuid.uuid4().hex[:8]}_0"
        if not filename:
            filename = f"{image_id}.png"

        file_path = self.image_dir / filename

        try:
            if image_data.startswith(("http://", "https://")):
                logger.info(f"Downloading image from URL: {image_data[:80]}")
                response = requests.get(image_data, timeout=60)
                response.raise_for_status()
                file_path.write_bytes(response.content)
            else:
                logger.info("Decoding base64 image data")
                data = image_data.split(",", 1)[1] if "," in image_data else image_data
                file_path.write_bytes(base64.b64decode(data))

            self.state_manager.add_image(image_id, filename, str(file_path))
            logger.info(f"Saved image: {image_id} -> {file_path}")
            return image_id, str(file_path)

        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return None

    def save_from_comfyui(
        self,
        filename: str,
        subfolder: str = "",
        image_type: str = "output"
    ) -> Optional[Tuple[str, str]]:
        """
        Download and save an image from ComfyUI.

        Args:
            filename: ComfyUI image filename
            subfolder: Optional subfolder
            image_type: Image type (output, temp, input)

        Returns:
            Tuple of (image_id, file_path) or None on failure
        """
        if not self.comfyui_url:
            logger.warning("ComfyUI URL not configured for image download")
            return None

        # Build safe filename
        safe_name = Path(filename).name
        if subfolder:
            safe_subfolder = subfolder.replace("/", "_").replace("\\", "_")
            safe_name = f"{safe_subfolder}_{safe_name}"

        if not safe_name.lower().endswith(".png"):
            logger.warning(f"Skipping non-PNG: {safe_name}")
            return None

        output_path = self.image_dir / safe_name
        if output_path.exists():
            image_id = output_path.stem
            return image_id, str(output_path)

        try:
            response = requests.get(
                f"{self.comfyui_url}/view",
                params={
                    "filename": filename,
                    "subfolder": subfolder,
                    "type": image_type
                },
                timeout=60
            )
            response.raise_for_status()
            output_path.write_bytes(response.content)

            image_id = output_path.stem
            self.state_manager.add_image(image_id, safe_name, str(output_path))
            return image_id, str(output_path)

        except Exception as e:
            logger.error(f"Failed to download ComfyUI image {filename}: {e}")
            return None

    def set_status(
        self,
        image_id: str,
        status: ImageStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Set the status of an image.

        Args:
            image_id: Image identifier
            status: New status
            metadata: Optional additional metadata

        Returns:
            True if successful
        """
        try:
            self.state_manager.set_image_status(image_id, status.value, metadata)
            return True
        except StateManagerError as e:
            logger.error(f"Failed to set status for {image_id}: {e}")
            return False

    def get_status(self, image_id: str) -> str:
        """Get the status of an image."""
        return self.state_manager.get_image_status(image_id)

    def get_statistics(self) -> Dict[str, int]:
        """Get image statistics."""
        return self.state_manager.get_statistics()

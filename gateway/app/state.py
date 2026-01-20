"""
State Management
Thread-safe image approval and publish status tracking with atomic writes
"""
import json
import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ImageStatus(Enum):
    """Valid image status values"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"

    @classmethod
    def is_valid(cls, status: str) -> bool:
        """Check if status string is valid"""
        return status in [s.value for s in cls]

    @classmethod
    def list_values(cls) -> List[str]:
        """Get list of all valid status values"""
        return [s.value for s in cls]


@dataclass
class ImageMetadata:
    """Image metadata structure"""
    filename: str
    path: str
    status: str
    created_at: str
    updated_at: str
    product_id: Optional[str] = None
    title: Optional[str] = None
    price_cents: Optional[int] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    style: Optional[str] = None
    genre: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageMetadata":
        """Create from dictionary with defaults"""
        now = datetime.now().isoformat()
        return cls(
            filename=data.get("filename", ""),
            path=data.get("path", ""),
            status=data.get("status", ImageStatus.PENDING.value),
            created_at=data.get("created_at", now),
            updated_at=data.get("updated_at", now),
            product_id=data.get("product_id"),
            title=data.get("title"),
            price_cents=data.get("price_cents"),
            description=data.get("description"),
            prompt=data.get("prompt"),
            style=data.get("style"),
            genre=data.get("genre"),
            width=data.get("width"),
            height=data.get("height"),
            error_message=data.get("error_message")
        )


class StateManagerError(Exception):
    """Base exception for state manager errors"""
    pass


class StateManager:
    """
    Thread-safe state manager for tracking image status

    Features:
    - Atomic file writes with temp files
    - Thread-safe operations with locks
    - Structured metadata with validation
    - Automatic timestamp tracking
    - Comprehensive error handling
    """

    def __init__(self, state_file: str):
        """
        Initialize state manager

        Args:
            state_file: Path to JSON state file
        """
        self.state_file = state_file
        self.lock = threading.Lock()
        self.state: Dict[str, Dict[str, Any]] = {"images": {}}
        self._load()

        logger.info(f"State manager initialized with file: {state_file}")

    def _load(self) -> None:
        """Load state from disk with error recovery"""
        if not os.path.exists(self.state_file):
            logger.info("State file not found, starting with empty state")
            self.state = {"images": {}}
            return

        try:
            with open(self.state_file, 'r') as f:
                loaded_state = json.load(f)

            # Validate loaded state structure
            if not isinstance(loaded_state, dict):
                raise ValueError("State file must contain a JSON object")

            if "images" not in loaded_state:
                logger.warning("State file missing 'images' key, adding it")
                loaded_state["images"] = {}

            self.state = loaded_state
            logger.info(f"Loaded state with {len(self.state['images'])} images")

        except json.JSONDecodeError as e:
            logger.error(f"Corrupted state file (JSON decode error): {e}")
            # Backup corrupted file
            backup_path = f"{self.state_file}.corrupted.{int(datetime.now().timestamp())}"
            try:
                os.rename(self.state_file, backup_path)
                logger.info(f"Backed up corrupted state to: {backup_path}")
            except Exception as backup_error:
                logger.error(f"Failed to backup corrupted state: {backup_error}")

            self.state = {"images": {}}

        except Exception as e:
            logger.error(f"Error loading state: {e}")
            self.state = {"images": {}}

    def _save(self) -> None:
        """Atomically save state to disk"""
        temp_file = f"{self.state_file}.tmp"

        try:
            # Write to temp file first
            with open(temp_file, 'w') as f:
                json.dump(self.state, f, indent=2)

            # Atomic rename (on POSIX systems)
            os.replace(temp_file, self.state_file)
            logger.debug("State saved successfully")

        except Exception as e:
            logger.error(f"Error saving state: {e}")
            # Clean up temp file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup temp file: {cleanup_error}")

            raise StateManagerError(f"Failed to save state: {e}")

    def _update_timestamp(self, image_data: Dict[str, Any]) -> None:
        """Update the updated_at timestamp"""
        image_data["updated_at"] = datetime.now().isoformat()

    def get_image_status(self, image_id: str) -> str:
        """
        Get status of an image

        Args:
            image_id: Image identifier

        Returns:
            Status string (pending, approved, rejected, publishing, published, failed)
        """
        with self.lock:
            image_data = self.state["images"].get(image_id, {})
            status = image_data.get("status", ImageStatus.PENDING.value)
            logger.debug(f"Get status for {image_id}: {status}")
            return status

    def set_image_status(
        self,
        image_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Set image status with optional metadata

        Args:
            image_id: Image identifier
            status: New status (must be valid ImageStatus)
            metadata: Optional additional metadata to store

        Raises:
            ValueError: If status is invalid
            StateManagerError: If save fails
        """
        # Validate status
        if not ImageStatus.is_valid(status):
            valid_statuses = ImageStatus.list_values()
            raise ValueError(
                f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
            )

        with self.lock:
            # Initialize image data if not exists
            if image_id not in self.state["images"]:
                now = datetime.now().isoformat()
                self.state["images"][image_id] = {
                    "status": status,
                    "created_at": now,
                    "updated_at": now
                }
            else:
                self.state["images"][image_id]["status"] = status
                self._update_timestamp(self.state["images"][image_id])

            # Add optional metadata
            if metadata:
                self.state["images"][image_id].update(metadata)
                self._update_timestamp(self.state["images"][image_id])

            logger.info(f"Set status for {image_id}: {status}")

            # Save state
            try:
                self._save()
            except StateManagerError as e:
                logger.error(f"Failed to save state after status update: {e}")
                # State is updated in memory but not persisted
                raise

    def get_images_by_status(self, status: str) -> List[str]:
        """
        Get all image IDs with given status

        Args:
            status: Status to filter by

        Returns:
            List of image IDs
        """
        with self.lock:
            images = [
                img_id for img_id, data in self.state["images"].items()
                if data.get("status") == status
            ]
            logger.debug(f"Found {len(images)} images with status '{status}'")
            return images

    def get_all_images(self) -> Dict[str, Dict[str, Any]]:
        """
        Get full state dict (thread-safe copy)

        Returns:
            Copy of all image data
        """
        with self.lock:
            return self.state["images"].copy()

    def get_image_metadata(self, image_id: str) -> Optional[ImageMetadata]:
        """
        Get full metadata for an image

        Args:
            image_id: Image identifier

        Returns:
            ImageMetadata object or None if not found
        """
        with self.lock:
            data = self.state["images"].get(image_id)
            if data:
                return ImageMetadata.from_dict(data)
            return None

    def add_image(
        self,
        image_id: str,
        filename: str,
        path: str,
        status: str = ImageStatus.PENDING.value
    ) -> None:
        """
        Register a new image

        Args:
            image_id: Image identifier
            filename: Original filename
            path: Path to image file
            status: Initial status (default: pending)

        Raises:
            ValueError: If status is invalid
            StateManagerError: If save fails
        """
        # Validate status
        if not ImageStatus.is_valid(status):
            raise ValueError(f"Invalid status: {status}")

        with self.lock:
            now = datetime.now().isoformat()
            self.state["images"][image_id] = {
                "filename": filename,
                "path": path,
                "status": status,
                "created_at": now,
                "updated_at": now
            }

            logger.info(f"Added new image: {image_id} ({filename})")

            try:
                self._save()
            except StateManagerError as e:
                logger.error(f"Failed to save state after adding image: {e}")
                raise

    def delete_image(self, image_id: str) -> bool:
        """
        Remove an image from state

        Args:
            image_id: Image identifier

        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if image_id in self.state["images"]:
                del self.state["images"][image_id]
                logger.info(f"Deleted image: {image_id}")

                try:
                    self._save()
                    return True
                except StateManagerError as e:
                    logger.error(f"Failed to save state after deleting image: {e}")
                    raise
            else:
                logger.warning(f"Attempted to delete non-existent image: {image_id}")
                return False

    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about images

        Returns:
            Dict with counts per status
        """
        with self.lock:
            stats = {
                "total": len(self.state["images"])
            }

            # Count by status
            for status in ImageStatus:
                count = len([
                    img for img in self.state["images"].values()
                    if img.get("status") == status.value
                ])
                stats[status.value] = count

            return stats

    def clear_old_images(self, days: int = 30) -> int:
        """
        Remove images older than specified days

        Args:
            days: Age threshold in days

        Returns:
            Number of images removed
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        removed_count = 0

        with self.lock:
            images_to_remove = []

            for img_id, data in self.state["images"].items():
                try:
                    created_at = datetime.fromisoformat(data.get("created_at", ""))
                    if created_at < cutoff:
                        images_to_remove.append(img_id)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid timestamp for {img_id}: {e}")

            for img_id in images_to_remove:
                del self.state["images"][img_id]
                removed_count += 1

            if removed_count > 0:
                logger.info(f"Cleared {removed_count} images older than {days} days")
                try:
                    self._save()
                except StateManagerError as e:
                    logger.error(f"Failed to save state after clearing old images: {e}")
                    raise

        return removed_count

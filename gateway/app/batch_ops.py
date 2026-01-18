"""
Batch operations for approve/reject/publish
"""
import logging
from typing import List, Dict, Any, Tuple
from app.state import StateManager, ImageStatus

logger = logging.getLogger(__name__)


class BatchOperationResult:
    """Result of a batch operation"""

    def __init__(self):
        self.successful: List[str] = []
        self.failed: List[Tuple[str, str]] = []  # (image_id, error_message)
        self.skipped: List[Tuple[str, str]] = []  # (image_id, reason)

    def add_success(self, image_id: str):
        """Mark operation as successful for image"""
        self.successful.append(image_id)

    def add_failure(self, image_id: str, error: str):
        """Mark operation as failed for image"""
        self.failed.append((image_id, error))

    def add_skipped(self, image_id: str, reason: str):
        """Mark operation as skipped for image"""
        self.skipped.append((image_id, reason))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            'successful': self.successful,
            'failed': [{'image_id': img_id, 'error': err} for img_id, err in self.failed],
            'skipped': [{'image_id': img_id, 'reason': reason} for img_id, reason in self.skipped],
            'counts': {
                'successful': len(self.successful),
                'failed': len(self.failed),
                'skipped': len(self.skipped),
                'total': len(self.successful) + len(self.failed) + len(self.skipped)
            }
        }


class BatchOperations:
    """
    Batch operations for images.

    Supports:
    - Batch approve
    - Batch reject
    - Batch publish
    - Batch delete
    """

    def __init__(self, state_manager: StateManager):
        """
        Initialize batch operations.

        Args:
            state_manager: State manager instance
        """
        self.state_manager = state_manager

    def batch_approve(self, image_ids: List[str]) -> BatchOperationResult:
        """
        Approve multiple images.

        Args:
            image_ids: List of image IDs to approve

        Returns:
            Batch operation result
        """
        result = BatchOperationResult()

        for image_id in image_ids:
            try:
                # Check if image exists
                if image_id not in self.state_manager.state:
                    result.add_failure(image_id, "Image not found")
                    continue

                # Check current status
                current_status = self.state_manager.state[image_id].get('status')

                if current_status == ImageStatus.APPROVED.value:
                    result.add_skipped(image_id, "Already approved")
                    continue

                if current_status not in [ImageStatus.PENDING.value, ImageStatus.REJECTED.value]:
                    result.add_skipped(image_id, f"Cannot approve image in status: {current_status}")
                    continue

                # Approve
                self.state_manager.set_image_status(image_id, ImageStatus.APPROVED.value)
                result.add_success(image_id)

                logger.info(f"Batch approved: {image_id}")

            except Exception as e:
                logger.error(f"Failed to approve {image_id}: {e}")
                result.add_failure(image_id, str(e))

        return result

    def batch_reject(self, image_ids: List[str], reason: str = None) -> BatchOperationResult:
        """
        Reject multiple images.

        Args:
            image_ids: List of image IDs to reject
            reason: Optional rejection reason

        Returns:
            Batch operation result
        """
        result = BatchOperationResult()

        for image_id in image_ids:
            try:
                # Check if image exists
                if image_id not in self.state_manager.state:
                    result.add_failure(image_id, "Image not found")
                    continue

                # Check current status
                current_status = self.state_manager.state[image_id].get('status')

                if current_status == ImageStatus.REJECTED.value:
                    result.add_skipped(image_id, "Already rejected")
                    continue

                if current_status == ImageStatus.PUBLISHED.value:
                    result.add_skipped(image_id, "Cannot reject published image")
                    continue

                # Reject
                metadata = {'rejection_reason': reason} if reason else {}
                self.state_manager.set_image_status(
                    image_id,
                    ImageStatus.REJECTED.value,
                    metadata
                )
                result.add_success(image_id)

                logger.info(f"Batch rejected: {image_id}")

            except Exception as e:
                logger.error(f"Failed to reject {image_id}: {e}")
                result.add_failure(image_id, str(e))

        return result

    def batch_publish(
        self,
        image_ids: List[str],
        platform: str,
        product_type: str,
        price_cents: int = None
    ) -> BatchOperationResult:
        """
        Publish multiple images.

        Note: Actual publishing logic should be called separately.
        This method only validates and marks images ready for publishing.

        Args:
            image_ids: List of image IDs to publish
            platform: Platform to publish to
            product_type: Product type
            price_cents: Optional price in cents

        Returns:
            Batch operation result
        """
        result = BatchOperationResult()

        for image_id in image_ids:
            try:
                # Check if image exists
                if image_id not in self.state_manager.state:
                    result.add_failure(image_id, "Image not found")
                    continue

                # Check current status
                current_status = self.state_manager.state[image_id].get('status')

                if current_status != ImageStatus.APPROVED.value:
                    result.add_skipped(
                        image_id,
                        f"Image must be approved before publishing (current: {current_status})"
                    )
                    continue

                # Mark ready for publishing
                metadata = {
                    'platform': platform,
                    'product_type': product_type
                }
                if price_cents:
                    metadata['price_cents'] = price_cents

                self.state_manager.update_metadata(image_id, metadata)
                result.add_success(image_id)

                logger.info(f"Batch publish queued: {image_id}")

            except Exception as e:
                logger.error(f"Failed to queue publish for {image_id}: {e}")
                result.add_failure(image_id, str(e))

        return result

    def batch_delete(self, image_ids: List[str], force: bool = False) -> BatchOperationResult:
        """
        Delete multiple images.

        Args:
            image_ids: List of image IDs to delete
            force: If True, delete even if published

        Returns:
            Batch operation result
        """
        result = BatchOperationResult()

        for image_id in image_ids:
            try:
                # Check if image exists
                if image_id not in self.state_manager.state:
                    result.add_failure(image_id, "Image not found")
                    continue

                # Check current status
                current_status = self.state_manager.state[image_id].get('status')

                if current_status == ImageStatus.PUBLISHED.value and not force:
                    result.add_skipped(image_id, "Cannot delete published image (use force=true)")
                    continue

                # Delete from state
                del self.state_manager.state[image_id]
                self.state_manager.save()

                result.add_success(image_id)
                logger.info(f"Batch deleted: {image_id}")

            except Exception as e:
                logger.error(f"Failed to delete {image_id}: {e}")
                result.add_failure(image_id, str(e))

        return result

    def batch_update_metadata(
        self,
        image_ids: List[str],
        metadata: Dict[str, Any]
    ) -> BatchOperationResult:
        """
        Update metadata for multiple images.

        Args:
            image_ids: List of image IDs
            metadata: Metadata to update

        Returns:
            Batch operation result
        """
        result = BatchOperationResult()

        for image_id in image_ids:
            try:
                # Check if image exists
                if image_id not in self.state_manager.state:
                    result.add_failure(image_id, "Image not found")
                    continue

                # Update metadata
                self.state_manager.update_metadata(image_id, metadata)
                result.add_success(image_id)

                logger.info(f"Batch metadata updated: {image_id}")

            except Exception as e:
                logger.error(f"Failed to update metadata for {image_id}: {e}")
                result.add_failure(image_id, str(e))

        return result

    def get_batch_by_filter(
        self,
        status: str = None,
        batch_id: str = None,
        platform: str = None,
        limit: int = None
    ) -> List[str]:
        """
        Get image IDs matching filter criteria.

        Args:
            status: Filter by status
            batch_id: Filter by batch ID
            platform: Filter by platform
            limit: Maximum results to return

        Returns:
            List of matching image IDs
        """
        matching_ids = []

        for image_id, img_state in self.state_manager.state.items():
            # Filter by status
            if status and img_state.get('status') != status:
                continue

            # Filter by batch_id
            if batch_id:
                metadata = img_state.get('metadata', {})
                if metadata.get('batch_id') != batch_id:
                    continue

            # Filter by platform
            if platform:
                metadata = img_state.get('metadata', {})
                if metadata.get('platform') != platform:
                    continue

            matching_ids.append(image_id)

            # Check limit
            if limit and len(matching_ids) >= limit:
                break

        return matching_ids

"""
Webhook support for async event notifications
"""
import requests
import logging
import time
import hmac
import hashlib
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from app.retry import retry_with_backoff, RetryConfig

logger = logging.getLogger(__name__)


@dataclass
class WebhookEvent:
    """Webhook event data"""
    event_type: str  # 'generation.completed', 'image.approved', 'product.published', etc.
    data: Dict[str, Any]
    timestamp: float
    event_id: str


class WebhookDelivery:
    """
    Handles webhook delivery with retries and signatures.
    """

    def __init__(self, url: str, secret: str = None, timeout: int = 10):
        """
        Initialize webhook delivery.

        Args:
            url: Webhook endpoint URL
            secret: Optional secret for HMAC signatures
            timeout: Request timeout in seconds
        """
        self.url = url
        self.secret = secret
        self.timeout = timeout

    def _generate_signature(self, payload: str) -> str:
        """
        Generate HMAC signature for payload.

        Args:
            payload: JSON payload string

        Returns:
            HMAC signature
        """
        if not self.secret:
            return ""

        signature = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"sha256={signature}"

    def deliver(self, event: WebhookEvent) -> bool:
        """
        Deliver webhook event.

        Args:
            event: Webhook event to deliver

        Returns:
            True if delivery successful, False otherwise
        """
        # Build payload
        payload = {
            'event_type': event.event_type,
            'event_id': event.event_id,
            'timestamp': event.timestamp,
            'data': event.data
        }

        payload_str = json.dumps(payload)

        # Build headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'POD-Gateway-Webhook/1.0',
            'X-Webhook-Event': event.event_type,
            'X-Webhook-ID': event.event_id
        }

        # Add signature if secret is configured
        if self.secret:
            headers['X-Webhook-Signature'] = self._generate_signature(payload_str)

        # Deliver with retries
        retry_config = RetryConfig(
            max_attempts=3,
            initial_delay=2.0,
            max_delay=30.0
        )

        @retry_with_backoff(
            config=retry_config,
            exceptions=(requests.RequestException,)
        )
        def send_webhook():
            response = requests.post(
                self.url,
                data=payload_str,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response

        try:
            response = send_webhook()
            logger.info(f"Webhook delivered successfully to {self.url}: {event.event_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to deliver webhook to {self.url}: {e}")
            return False


class WebhookManager:
    """
    Manages webhook registrations and deliveries.
    """

    def __init__(self):
        self.webhooks: Dict[str, List[WebhookDelivery]] = {}
        self.delivery_stats = {
            'total_sent': 0,
            'successful': 0,
            'failed': 0
        }

    def register(self, event_type: str, url: str, secret: str = None):
        """
        Register webhook endpoint for event type.

        Args:
            event_type: Event type to subscribe to (e.g., 'image.approved')
            url: Webhook endpoint URL
            secret: Optional secret for HMAC signatures
        """
        if event_type not in self.webhooks:
            self.webhooks[event_type] = []

        delivery = WebhookDelivery(url, secret)
        self.webhooks[event_type].append(delivery)

        logger.info(f"Registered webhook for {event_type}: {url}")

    def unregister(self, event_type: str, url: str):
        """
        Unregister webhook endpoint.

        Args:
            event_type: Event type
            url: Webhook endpoint URL
        """
        if event_type in self.webhooks:
            self.webhooks[event_type] = [
                w for w in self.webhooks[event_type]
                if w.url != url
            ]

    def emit(self, event_type: str, data: Dict[str, Any], event_id: str = None):
        """
        Emit webhook event to registered endpoints.

        Args:
            event_type: Event type
            data: Event data
            event_id: Optional event ID (generated if not provided)
        """
        if event_type not in self.webhooks or not self.webhooks[event_type]:
            return

        # Create event
        event = WebhookEvent(
            event_type=event_type,
            data=data,
            timestamp=time.time(),
            event_id=event_id or f"evt_{int(time.time() * 1000)}"
        )

        # Deliver to all registered webhooks
        for webhook in self.webhooks[event_type]:
            self.delivery_stats['total_sent'] += 1

            success = webhook.deliver(event)

            if success:
                self.delivery_stats['successful'] += 1
            else:
                self.delivery_stats['failed'] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get webhook delivery statistics"""
        return {
            'registered_webhooks': {
                event_type: len(webhooks)
                for event_type, webhooks in self.webhooks.items()
            },
            'delivery_stats': self.delivery_stats
        }


# Global webhook manager
webhook_manager = WebhookManager()


# Event type constants
class WebhookEvents:
    """Standard webhook event types"""
    GENERATION_STARTED = 'generation.started'
    GENERATION_COMPLETED = 'generation.completed'
    GENERATION_FAILED = 'generation.failed'

    IMAGE_APPROVED = 'image.approved'
    IMAGE_REJECTED = 'image.rejected'

    PRODUCT_PUBLISHED = 'product.published'
    PRODUCT_FAILED = 'product.failed'

    BATCH_COMPLETED = 'batch.completed'


# Convenience functions
def emit_generation_completed(image_id: str, metadata: Dict[str, Any]):
    """Emit generation completed event"""
    webhook_manager.emit(
        WebhookEvents.GENERATION_COMPLETED,
        {'image_id': image_id, 'metadata': metadata}
    )


def emit_image_approved(image_id: str):
    """Emit image approved event"""
    webhook_manager.emit(
        WebhookEvents.IMAGE_APPROVED,
        {'image_id': image_id}
    )


def emit_product_published(image_id: str, product_id: str, platform: str):
    """Emit product published event"""
    webhook_manager.emit(
        WebhookEvents.PRODUCT_PUBLISHED,
        {
            'image_id': image_id,
            'product_id': product_id,
            'platform': platform
        }
    )


def emit_batch_completed(batch_id: str, success_count: int, failed_count: int):
    """Emit batch completed event"""
    webhook_manager.emit(
        WebhookEvents.BATCH_COMPLETED,
        {
            'batch_id': batch_id,
            'success_count': success_count,
            'failed_count': failed_count
        }
    )

"""Integration modules for external services."""

from antigravity.integrations.slack import notify_slack
from antigravity.integrations.email import notify_email
from antigravity.integrations.webhook import emit_webhook
from antigravity.integrations.zazzle import ZazzleClient, create_zazzle_product

__all__ = [
    "notify_slack",
    "notify_email",
    "emit_webhook",
    "ZazzleClient",
    "create_zazzle_product",
]

"""Integration modules for external services."""

from antigravity.integrations.slack import notify_slack
from antigravity.integrations.email import notify_email
from antigravity.integrations.webhook import emit_webhook

__all__ = [
    "notify_slack",
    "notify_email",
    "emit_webhook",
]

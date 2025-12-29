"""
Notification System for Printify Autopublisher

Supports:
- Telegram
- Discord
- Slack (optional)
"""

import os
import requests
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

log = get_logger("NOTIFIER")


class Notifier:
    """
    Multi-platform notification sender.
    """

    def __init__(self):
        """Initialize notifier with environment credentials."""
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat = os.getenv("TELEGRAM_CHAT_ID")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")

    def send(self, message: str, level: str = "info") -> bool:
        """
        Send notification across all configured platforms.

        Args:
            message: Message to send
            level: Notification level (info, success, error, warning)

        Returns:
            True if any notification succeeded
        """
        emoji = self._get_emoji(level)
        full_msg = f"{emoji} {message}"

        results = []

        # Try all configured platforms
        if self.telegram_token and self.telegram_chat:
            results.append(self._send_telegram(full_msg))

        if self.discord_webhook:
            results.append(self._send_discord(full_msg, level))

        if self.slack_webhook:
            results.append(self._send_slack(full_msg))

        return any(results)

    def _get_emoji(self, level: str) -> str:
        """Get emoji for notification level."""
        emojis = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }
        return emojis.get(level, "ℹ️")

    def _send_telegram(self, message: str) -> bool:
        """Send Telegram notification."""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            response = requests.post(
                url,
                data={
                    "chat_id": self.telegram_chat,
                    "text": message,
                    "parse_mode": "Markdown"
                },
                timeout=5
            )
            response.raise_for_status()
            log.debug("Telegram notification sent")
            return True

        except Exception as e:
            log.error(f"Telegram notification failed: {e}")
            return False

    def _send_discord(self, message: str, level: str) -> bool:
        """Send Discord notification."""
        try:
            # Color based on level
            colors = {
                "info": 3447003,  # Blue
                "success": 3066993,  # Green
                "error": 15158332,  # Red
                "warning": 15105570  # Orange
            }

            payload = {
                "embeds": [{
                    "description": message,
                    "color": colors.get(level, 3447003)
                }]
            }

            response = requests.post(
                self.discord_webhook,
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            log.debug("Discord notification sent")
            return True

        except Exception as e:
            log.error(f"Discord notification failed: {e}")
            return False

    def _send_slack(self, message: str) -> bool:
        """Send Slack notification."""
        try:
            payload = {
                "text": message
            }

            response = requests.post(
                self.slack_webhook,
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            log.debug("Slack notification sent")
            return True

        except Exception as e:
            log.error(f"Slack notification failed: {e}")
            return False


# Global notifier instance
_notifier: Optional[Notifier] = None


def get_notifier() -> Notifier:
    """Get global notifier instance."""
    global _notifier
    if _notifier is None:
        _notifier = Notifier()
    return _notifier


def notify(message: str, level: str = "info") -> bool:
    """
    Convenience function to send notification.

    Args:
        message: Message to send
        level: Notification level (info, success, error, warning)

    Returns:
        True if any notification succeeded
    """
    return get_notifier().send(message, level)

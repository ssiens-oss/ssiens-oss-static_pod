"""Slack notification integration."""

import os
import requests
from typing import Optional


def notify_slack(
    message: str,
    webhook_url: Optional[str] = None,
    channel: Optional[str] = None,
    username: str = "Antigravity POD Bot"
) -> bool:
    """
    Send notification to Slack.

    Args:
        message: Message to send
        webhook_url: Slack webhook URL (uses SLACK_WEBHOOK_URL env var if not provided)
        channel: Optional channel override
        username: Bot username

    Returns:
        True if successful, False otherwise
    """
    url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL")

    if not url:
        print("Warning: SLACK_WEBHOOK_URL not configured, skipping Slack notification")
        return False

    try:
        payload = {
            "text": message,
            "username": username,
        }

        if channel:
            payload["channel"] = channel

        response = requests.post(
            url,
            json=payload,
            timeout=5,
        )

        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        print(f"Slack notification failed: {e}")
        return False


def notify_slack_rich(
    title: str,
    text: str,
    color: str = "#36a64f",
    fields: Optional[list] = None,
    webhook_url: Optional[str] = None
) -> bool:
    """
    Send rich formatted message to Slack.

    Args:
        title: Message title
        text: Main text
        color: Sidebar color (hex)
        fields: List of field dicts with 'title' and 'value'
        webhook_url: Slack webhook URL

    Returns:
        True if successful, False otherwise
    """
    url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL")

    if not url:
        print("Warning: SLACK_WEBHOOK_URL not configured")
        return False

    try:
        attachment = {
            "color": color,
            "title": title,
            "text": text,
            "footer": "Antigravity POD System",
            "ts": int(__import__("time").time()),
        }

        if fields:
            attachment["fields"] = fields

        payload = {
            "attachments": [attachment]
        }

        response = requests.post(
            url,
            json=payload,
            timeout=5,
        )

        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        print(f"Slack rich notification failed: {e}")
        return False

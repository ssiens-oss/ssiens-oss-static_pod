"""
Alert System
Discord and Telegram notifications for key events
"""

import os
import requests
from datetime import datetime

def send_alert(alert_data):
    """
    Send alert to configured channels

    Args:
        alert_data: dict with 'type', 'message', and optional metadata
    """

    # Send to Discord if configured
    discord_webhook = os.environ.get("DISCORD_WEBHOOK")
    if discord_webhook:
        send_discord(discord_webhook, alert_data)

    # Send to Telegram if configured
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if telegram_bot_token and telegram_chat_id:
        send_telegram(telegram_bot_token, telegram_chat_id, alert_data)

def send_discord(webhook_url, alert_data):
    """Send Discord webhook notification"""
    try:
        # Color based on alert type
        colors = {
            "success": 0x00ff00,  # Green
            "error": 0xff0000,    # Red
            "warning": 0xffaa00,  # Orange
            "info": 0x0099ff      # Blue
        }

        color = colors.get(alert_data.get("type", "info"), 0x0099ff)

        embed = {
            "title": f"StaticWaves POD Alert",
            "description": alert_data.get("message", ""),
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": []
        }

        # Add SKU if present
        if "sku" in alert_data:
            embed["fields"].append({
                "name": "SKU",
                "value": alert_data["sku"],
                "inline": True
            })

        # Add any extra metadata
        for key, value in alert_data.items():
            if key not in ["type", "message", "sku"]:
                embed["fields"].append({
                    "name": key.replace("_", " ").title(),
                    "value": str(value),
                    "inline": True
                })

        payload = {
            "embeds": [embed]
        }

        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()

    except Exception as e:
        print(f"Discord alert failed: {e}")

def send_telegram(bot_token, chat_id, alert_data):
    """Send Telegram notification"""
    try:
        # Format message
        message_lines = [
            "🚀 *StaticWaves POD Alert*",
            "",
            f"*Type:* {alert_data.get('type', 'info').upper()}",
            f"*Message:* {alert_data.get('message', '')}",
        ]

        # Add SKU if present
        if "sku" in alert_data:
            message_lines.append(f"*SKU:* `{alert_data['sku']}`")

        # Add timestamp
        message_lines.append(f"*Time:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

        message = "\n".join(message_lines)

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()

    except Exception as e:
        print(f"Telegram alert failed: {e}")

def test_alerts():
    """Test alert system"""
    send_alert({
        "type": "info",
        "message": "Alert system test - all systems operational",
        "test": True
    })

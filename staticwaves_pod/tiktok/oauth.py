"""
TikTok OAuth Auto-Refresh Module

Automatically refreshes TikTok OAuth tokens before expiry to ensure
zero downtime for uploads and API operations.
"""

import os
import requests
import time
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

log = get_logger("TIKTOK-OAUTH")
STATE = Path("staticwaves_pod/data/oauth.json")

CLIENT_ID = os.environ.get("TIKTOK_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "")


def refresh():
    """
    Refresh TikTok OAuth access token using the refresh token.

    Updates the state file with new access token and expiry time.
    Raises exception if refresh fails.
    """
    if not STATE.exists():
        raise RuntimeError(f"OAuth state file not found at {STATE}")

    state = json.loads(STATE.read_text())

    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("TIKTOK_CLIENT_ID and TIKTOK_CLIENT_SECRET must be set")

    log.info("🔄 Refreshing TikTok OAuth token...")

    r = requests.post(
        "https://open-api.tiktokglobalshop.com/oauth/token/refresh",
        json={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": state["refresh_token"]
        }
    )
    r.raise_for_status()
    data = r.json()

    state.update({
        "access_token": data["access_token"],
        "expires_at": time.time() + data["expires_in"]
    })
    STATE.write_text(json.dumps(state, indent=2))
    log.info("🔁 TikTok token refreshed successfully")


def get_token():
    """
    Get valid TikTok OAuth access token.

    Automatically refreshes token if it expires within 5 minutes.

    Returns:
        Valid access token string
    """
    if not STATE.exists():
        raise RuntimeError(
            f"OAuth state missing at {STATE}. "
            "Run initial OAuth flow to generate state file."
        )

    state = json.loads(STATE.read_text())

    # Refresh if token expires within 5 minutes (300 seconds)
    if time.time() > state["expires_at"] - 300:
        refresh()
        state = json.loads(STATE.read_text())

    return state["access_token"]


def initialize_oauth_state(access_token: str, refresh_token: str, expires_in: int):
    """
    Initialize OAuth state file with tokens from initial OAuth flow.

    Args:
        access_token: Initial access token
        refresh_token: Refresh token for renewals
        expires_in: Token expiry time in seconds
    """
    STATE.parent.mkdir(parents=True, exist_ok=True)

    state = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": time.time() + expires_in
    }

    STATE.write_text(json.dumps(state, indent=2))
    log.info("✅ OAuth state initialized")


if __name__ == "__main__":
    # Test token refresh
    try:
        token = get_token()
        log.info(f"✅ Token valid: {token[:20]}...")
    except Exception as e:
        log.error(f"❌ Error: {e}")

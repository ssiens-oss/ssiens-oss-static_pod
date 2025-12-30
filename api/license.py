"""
License Enforcement & Telemetry
Commercial SaaS controls with usage tracking
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
import hashlib
import hmac

LICENSE_FILE = Path("/opt/staticwaves/license.json")
TELEMETRY_ENDPOINT = "https://api.staticwaves.io/ping"

class LicenseError(Exception):
    """License validation failed"""
    pass

def check_license():
    """
    Verify license is valid

    Raises:
        LicenseError: If license is invalid or expired

    Returns:
        dict: License information
    """

    # Allow bypass in development
    if os.environ.get("STATICWAVES_DEV_MODE") == "true":
        return {
            "client_id": "dev",
            "tier": "unlimited",
            "expires": "2099-12-31"
        }

    # Check if license file exists
    if not LICENSE_FILE.exists():
        raise LicenseError("No license file found. Please contact StaticWaves support.")

    # Load license
    try:
        with open(LICENSE_FILE) as f:
            license_data = json.load(f)
    except Exception as e:
        raise LicenseError(f"Invalid license file: {e}")

    # Verify required fields
    required_fields = ["client_id", "tier", "expires", "signature"]
    for field in required_fields:
        if field not in license_data:
            raise LicenseError(f"License missing required field: {field}")

    # Check expiration
    expires = license_data["expires"]
    if datetime.utcnow().isoformat() > expires:
        raise LicenseError(f"License expired on {expires}")

    # Verify signature (simplified - production should use GPG)
    # In production, verify with GPG signature
    if not verify_license_signature(license_data):
        raise LicenseError("Invalid license signature")

    return license_data

def verify_license_signature(license_data):
    """
    Verify license signature
    In production, this would use GPG verification
    """

    # Get expected signature
    expected_sig = license_data.get("signature", "")

    # For now, just check it exists
    # In production, use GPG:
    # gpg --verify license.json.sig license.json

    return len(expected_sig) > 0

def check_usage_limits(license_data, current_usage):
    """
    Check if usage is within license limits

    Args:
        license_data: License info
        current_usage: Current usage stats (e.g., skus_today)

    Raises:
        LicenseError: If limits exceeded
    """

    tier_limits = {
        "solo": {"max_skus_per_day": 10},
        "agency": {"max_skus_per_day": 50},
        "enterprise": {"max_skus_per_day": 500},
        "unlimited": {"max_skus_per_day": float('inf')}
    }

    tier = license_data.get("tier", "solo")
    limits = tier_limits.get(tier, tier_limits["solo"])

    # Check daily SKU limit
    max_skus = limits.get("max_skus_per_day", 10)
    current_skus = current_usage.get("skus_today", 0)

    if current_skus >= max_skus:
        raise LicenseError(
            f"Daily SKU limit reached ({current_skus}/{max_skus}). "
            f"Upgrade your tier or wait until tomorrow."
        )

def send_telemetry(event_data):
    """
    Send telemetry ping to StaticWaves API

    Privacy-safe: No PII, opt-out supported
    """

    # Check if telemetry is disabled
    if os.environ.get("STATICWAVES_TELEMETRY") == "false":
        return

    try:
        # Load license for client ID
        license_data = check_license()

        payload = {
            "client_id": license_data.get("client_id"),
            "tier": license_data.get("tier"),
            "event": event_data.get("event", "ping"),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

        # Add event-specific data (no PII)
        if "skus_today" in event_data:
            payload["skus_today"] = event_data["skus_today"]

        # Send ping (non-blocking, short timeout)
        requests.post(
            TELEMETRY_ENDPOINT,
            json=payload,
            timeout=2
        )

    except Exception:
        # Telemetry failures should never break the app
        pass

def generate_license(client_id, tier, expires, secret_key):
    """
    Generate a license file (admin tool)

    Usage:
        python -c "from api.license import generate_license; \
                   generate_license('acme', 'agency', '2025-12-31', 'SECRET')"
    """

    license_data = {
        "client_id": client_id,
        "tier": tier,
        "expires": expires,
        "issued": datetime.utcnow().isoformat()
    }

    # Create signature
    message = json.dumps(license_data, sort_keys=True)
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    license_data["signature"] = signature

    # Write license file
    output_file = f"license_{client_id}.json"
    with open(output_file, "w") as f:
        json.dump(license_data, f, indent=2)

    print(f"✅ License generated: {output_file}")
    print(f"Client: {client_id}")
    print(f"Tier: {tier}")
    print(f"Expires: {expires}")

    return license_data

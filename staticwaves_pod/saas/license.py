"""
SaaS License Validation

Implements license key validation for white-label SaaS distribution.
Uses SHA-256 hashing with salt for security.
"""

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

log = get_logger("LICENSE")

LICENSE_SALT = os.environ.get("LICENSE_SALT", "default_salt_change_in_production")


def validate(key: str) -> bool:
    """
    Validate a license key.

    Valid keys produce SHA-256 hashes starting with '0000' when
    combined with the LICENSE_SALT.

    Args:
        key: License key to validate

    Returns:
        True if valid, False otherwise
    """
    if not key:
        log.error("❌ Empty license key")
        return False

    digest = hashlib.sha256(
        (key + LICENSE_SALT).encode()
    ).hexdigest()

    is_valid = digest.startswith("0000")

    if is_valid:
        log.info(f"✅ License key validated: {key[:8]}...")
    else:
        log.warning(f"❌ Invalid license key: {key[:8]}...")

    return is_valid


def generate_key(prefix: str = "SWPOD") -> str:
    """
    Generate a valid license key.

    Brute-force generates a key that produces a hash starting with '0000'.

    Args:
        prefix: Key prefix for branding

    Returns:
        Valid license key
    """
    import random
    import string

    log.info("🔑 Generating license key...")

    attempts = 0
    while True:
        attempts += 1

        # Generate random suffix
        suffix = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=12)
        )
        key = f"{prefix}-{suffix}"

        if validate(key):
            log.info(f"✅ Generated valid key after {attempts} attempts")
            return key

        if attempts % 1000 == 0:
            log.debug(f"🔄 {attempts} attempts...")


def check_license() -> bool:
    """
    Check if a valid license is configured.

    Reads LICENSE_KEY from environment.

    Returns:
        True if valid license exists
    """
    key = os.environ.get("LICENSE_KEY")

    if not key:
        log.error("❌ LICENSE_KEY not set in environment")
        return False

    return validate(key)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "generate":
            # Generate a new license key
            key = generate_key()
            print(f"\n✅ New License Key: {key}\n")
            print(f"Set in environment: export LICENSE_KEY={key}\n")

        elif sys.argv[1] == "validate":
            # Validate a key
            if len(sys.argv) > 2:
                is_valid = validate(sys.argv[2])
                print(f"\nValid: {is_valid}\n")
            else:
                print("Usage: python license.py validate <KEY>")

    else:
        print("Usage:")
        print("  python license.py generate        # Generate new key")
        print("  python license.py validate <KEY>  # Validate a key")

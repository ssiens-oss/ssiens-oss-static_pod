#!/usr/bin/env python3
"""
StaticWaves POD CLI

Command-line interface for managing TikTok Shop operations.
"""

import sys
import argparse
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from staticwaves_pod.core.logger import get_logger
from staticwaves_pod.saas.bootstrap import init, health_check
from staticwaves_pod.saas.license import generate_key, validate
from staticwaves_pod.tiktok.oauth import get_token, refresh
from staticwaves_pod.tiktok.analytics import compute_cvr, get_all_metrics, reset_metrics
from staticwaves_pod.tiktok.price_optimizer import prune_prices, get_price_report
from staticwaves_pod.tiktok.appeal_safe_copy import validate_copy, sanitize_copy

log = get_logger("CLI")


def cmd_init(args):
    """Initialize SaaS environment."""
    print("🚀 Initializing StaticWaves POD...\n")
    try:
        init()
        print("✅ Initialization complete!\n")

        health = health_check()
        print("📊 Health Status:")
        for key, value in health.items():
            status = "✅" if value in [True, "healthy"] else "❌"
            print(f"  {status} {key}: {value}")
        print()

    except Exception as e:
        print(f"❌ Initialization failed: {e}\n")
        sys.exit(1)


def cmd_license(args):
    """License key operations."""
    if args.action == "generate":
        print("🔑 Generating license key...\n")
        key = generate_key()
        print(f"✅ New License Key: {key}\n")
        print(f"Set in environment:")
        print(f"  export LICENSE_KEY={key}\n")

    elif args.action == "validate":
        if not args.key:
            print("❌ Please provide a key to validate\n")
            sys.exit(1)

        is_valid = validate(args.key)
        if is_valid:
            print(f"✅ License key is VALID\n")
        else:
            print(f"❌ License key is INVALID\n")
            sys.exit(1)


def cmd_oauth(args):
    """OAuth operations."""
    if args.action == "refresh":
        print("🔄 Refreshing OAuth token...\n")
        try:
            refresh()
            print("✅ Token refreshed successfully\n")
        except Exception as e:
            print(f"❌ Refresh failed: {e}\n")
            sys.exit(1)

    elif args.action == "status":
        try:
            token = get_token()
            print(f"✅ Token is valid: {token[:20]}...\n")
        except Exception as e:
            print(f"❌ Token error: {e}\n")
            sys.exit(1)


def cmd_analytics(args):
    """Analytics operations."""
    if args.action == "compute":
        print("📊 Computing conversion rates...\n")
        compute_cvr()
        print("✅ CVR computed\n")

    elif args.action == "report":
        import json
        metrics = get_all_metrics()
        print("📈 Analytics Report:\n")
        print(json.dumps(metrics, indent=2))
        print()

    elif args.action == "reset":
        if args.sku:
            print(f"🔄 Resetting metrics for {args.sku}...\n")
            reset_metrics(args.sku)
        else:
            print("🔄 Resetting ALL metrics...\n")
            reset_metrics()
        print("✅ Metrics reset\n")


def cmd_prices(args):
    """Price optimization operations."""
    if args.action == "prune":
        print("🧹 Pruning underperforming prices...\n")
        removed = prune_prices()

        total = sum(len(prices) for prices in removed.values())
        print(f"✅ Removed {total} price buckets\n")

        if total > 0:
            import json
            print("Removed prices:")
            print(json.dumps(removed, indent=2))
            print()

    elif args.action == "report":
        import json
        report = get_price_report()
        print("💰 Price Report:\n")
        print(json.dumps(report, indent=2))
        print()


def cmd_copy(args):
    """Copy validation operations."""
    if args.action == "validate":
        if not args.text:
            print("❌ Please provide text to validate\n")
            sys.exit(1)

        is_safe, violations = validate_copy(args.text)

        if is_safe:
            print("✅ Copy is appeal-safe\n")
        else:
            print(f"❌ Found {len(violations)} violations:\n")
            for v in violations:
                print(f"  - {v}")
            print()

    elif args.action == "sanitize":
        if not args.text:
            print("❌ Please provide text to sanitize\n")
            sys.exit(1)

        sanitized = sanitize_copy(args.text)
        print("🧹 Sanitized copy:\n")
        print(sanitized)
        print()


def main():
    parser = argparse.ArgumentParser(
        description="StaticWaves POD - TikTok Shop Automation CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # init command
    parser_init = subparsers.add_parser("init", help="Initialize SaaS environment")
    parser_init.set_defaults(func=cmd_init)

    # license command
    parser_license = subparsers.add_parser("license", help="License operations")
    parser_license.add_argument(
        "action",
        choices=["generate", "validate"],
        help="License action"
    )
    parser_license.add_argument("--key", help="License key to validate")
    parser_license.set_defaults(func=cmd_license)

    # oauth command
    parser_oauth = subparsers.add_parser("oauth", help="OAuth operations")
    parser_oauth.add_argument(
        "action",
        choices=["refresh", "status"],
        help="OAuth action"
    )
    parser_oauth.set_defaults(func=cmd_oauth)

    # analytics command
    parser_analytics = subparsers.add_parser("analytics", help="Analytics operations")
    parser_analytics.add_argument(
        "action",
        choices=["compute", "report", "reset"],
        help="Analytics action"
    )
    parser_analytics.add_argument("--sku", help="SKU to reset (optional)")
    parser_analytics.set_defaults(func=cmd_analytics)

    # prices command
    parser_prices = subparsers.add_parser("prices", help="Price optimization")
    parser_prices.add_argument(
        "action",
        choices=["prune", "report"],
        help="Price action"
    )
    parser_prices.set_defaults(func=cmd_prices)

    # copy command
    parser_copy = subparsers.add_parser("copy", help="Copy validation")
    parser_copy.add_argument(
        "action",
        choices=["validate", "sanitize"],
        help="Copy action"
    )
    parser_copy.add_argument("--text", help="Text to validate/sanitize")
    parser_copy.set_defaults(func=cmd_copy)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()

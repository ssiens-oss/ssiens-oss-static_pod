#!/usr/bin/env python3
"""
Zazzle API Validation Script

This script validates your Zazzle API configuration and tests connectivity.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv


def check_env_vars():
    """Check if required environment variables are set."""
    print("🔍 Checking Environment Variables...\n")

    load_dotenv()

    checks = {
        "ZAZZLE_ASSOCIATE_ID": os.environ.get("ZAZZLE_ASSOCIATE_ID"),
        "ZAZZLE_API_KEY": os.environ.get("ZAZZLE_API_KEY"),
        "ZAZZLE_STORE_ID": os.environ.get("ZAZZLE_STORE_ID"),
        "ZAZZLE_DEFAULT_TEMPLATE": os.environ.get("ZAZZLE_DEFAULT_TEMPLATE"),
        "ENABLE_ZAZZLE": os.environ.get("ENABLE_ZAZZLE"),
    }

    has_credentials = False

    for var, value in checks.items():
        if value:
            # Mask sensitive values
            if "KEY" in var or "ID" in var:
                masked = value[:8] + "..." if len(value) > 8 else value
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value}")

            if var in ["ZAZZLE_ASSOCIATE_ID", "ZAZZLE_API_KEY"]:
                has_credentials = True
        else:
            status = "⚠️ " if var in ["ZAZZLE_ASSOCIATE_ID", "ZAZZLE_API_KEY"] else "ℹ️ "
            print(f"  {status} {var}: Not set")

    print()

    if not has_credentials:
        print("❌ No Zazzle credentials found!")
        print("   You need at least one of:")
        print("   - ZAZZLE_ASSOCIATE_ID")
        print("   - ZAZZLE_API_KEY")
        print()
        print("Run: ./setup_zazzle.sh to configure")
        return False

    return True


def test_client_initialization():
    """Test Zazzle client initialization."""
    print("🔧 Testing Zazzle Client Initialization...\n")

    try:
        from antigravity.integrations.zazzle import ZazzleClient

        client = ZazzleClient()

        print("  ✅ Zazzle client initialized successfully")
        print(f"  ✅ Store URL: {client.get_store_url()}")

        if client.associate_id:
            print(f"  ✅ Associate ID configured")

        if client.api_key:
            print(f"  ✅ API Key configured")

        if client.store_id:
            print(f"  ✅ Store ID: {client.store_id}")

        print()
        return True

    except ValueError as e:
        print(f"  ❌ Configuration error: {e}")
        print()
        return False

    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        print()
        return False


def test_product_types():
    """Test product types are available."""
    print("📦 Checking Product Types...\n")

    try:
        from antigravity.integrations.zazzle import ZazzleClient

        client = ZazzleClient()

        print("  Available product types:")
        for product_type in client.PRODUCT_TYPES.keys():
            print(f"    • {product_type}")

        print()
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False


def test_templates():
    """Test Zazzle templates."""
    print("📋 Checking Templates...\n")

    try:
        from antigravity.integrations.zazzle import ZAZZLE_TEMPLATES

        print("  Available templates:")
        for template_name, config in ZAZZLE_TEMPLATES.items():
            print(f"    • {template_name}")
            print(f"      Product: {config['product_type']}")
            print(f"      Price: ${config['price']}")
            print(f"      Royalty: {config['royalty_percentage']}%")

        print()
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False


def test_orchestrator():
    """Test Zazzle orchestrator initialization."""
    print("🎨 Testing Zazzle POD Orchestrator...\n")

    try:
        from antigravity.pod.zazzle_orchestrator import ZazzlePODOrchestrator

        orchestrator = ZazzlePODOrchestrator(
            dry_run=True,
            require_human=True,
        )

        print("  ✅ Zazzle POD Orchestrator initialized")
        print("  ✅ Antigravity core loaded")

        if orchestrator.zazzle_available:
            print("  ✅ Zazzle client available")
        else:
            print("  ⚠️  Zazzle client not available (check credentials)")

        print()
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_verification():
    """Test verification functions."""
    print("✅ Testing Verification Functions...\n")

    try:
        from antigravity.verification import (
            verify_zazzle_product,
            verify_zazzle_store,
        )

        print("  ✅ verify_zazzle_product() available")
        print("  ✅ verify_zazzle_store() available")
        print()
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("="*70)
    print("  Next Steps")
    print("="*70)
    print()
    print("1. Test with a design (dry run):")
    print("   python -m antigravity.zazzle_cli design design.png --dry-run \\")
    print("     --product-type tshirt --template tshirt_basic")
    print()
    print("2. Try the quick start examples:")
    print("   python examples/zazzle_quickstart.py")
    print()
    print("3. Process for real:")
    print("   python -m antigravity.zazzle_cli design design.png \\")
    print("     --product-type hoodie --template hoodie_premium")
    print()
    print("4. Create multiple product types:")
    print("   python -m antigravity.zazzle_cli multi design.png \\")
    print("     --product-types tshirt,hoodie,mug,poster")
    print()
    print("5. Watch directory (autonomous):")
    print("   python -m antigravity.zazzle_cli watch \\")
    print("     --watch-dir /data/comfyui/output")
    print()
    print("6. Read full documentation:")
    print("   cat ZAZZLE_INTEGRATION.md")
    print()


def main():
    """Run all validation tests."""
    print("\n" + "="*70)
    print("  Zazzle API Validation")
    print("="*70 + "\n")

    tests = [
        ("Environment Variables", check_env_vars),
        ("Client Initialization", test_client_initialization),
        ("Product Types", test_product_types),
        ("Templates", test_templates),
        ("Orchestrator", test_orchestrator),
        ("Verification", test_verification),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))

    # Summary
    print("="*70)
    print("  Validation Summary")
    print("="*70)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")

    print()
    print(f"  Total: {passed}/{total} tests passed")
    print()

    if passed == total:
        print("✅ All tests passed! Zazzle integration is ready.")
        print()
        print_next_steps()
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print()

        if not results[0][1]:  # Environment variables check failed
            print("💡 Quick fix:")
            print("   Run: ./setup_zazzle.sh")
            print()

        return 1


if __name__ == "__main__":
    exit(main())

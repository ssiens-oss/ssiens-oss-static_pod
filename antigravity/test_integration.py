#!/usr/bin/env python3
"""
Quick test script to verify Zazzle integration setup
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all core modules can be imported"""
    print("🧪 Testing module imports...")

    try:
        from antigravity.models import PODOffer, ModelResponse, ExecutionPlan
        print("  ✅ Models imported successfully")
    except Exception as e:
        print(f"  ❌ Failed to import models: {e}")
        return False

    try:
        from antigravity.integrations.zazzle import ZazzleClient, ZAZZLE_TEMPLATES
        print("  ✅ Zazzle integration imported successfully")
    except Exception as e:
        print(f"  ❌ Failed to import Zazzle integration: {e}")
        return False

    try:
        from antigravity.pod.zazzle_orchestrator import ZazzlePODOrchestrator
        print("  ✅ Zazzle orchestrator imported successfully")
    except Exception as e:
        print(f"  ❌ Failed to import Zazzle orchestrator: {e}")
        return False

    return True

def test_configuration():
    """Test that configuration is loaded"""
    print("\n⚙️  Testing configuration...")

    # Load .env
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("  ❌ .env file not found")
        return False

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

    # Check Zazzle config
    associate_id = os.getenv("ZAZZLE_ASSOCIATE_ID", "")
    store_id = os.getenv("ZAZZLE_STORE_ID", "")

    if not associate_id or associate_id == "your-associate-id":
        print("  ❌ Zazzle Associate ID not configured")
        return False
    print(f"  ✅ Associate ID: {associate_id}")

    if not store_id or store_id == "your-store-id":
        print("  ❌ Zazzle Store ID not configured")
        return False
    print(f"  ✅ Store ID: {store_id}")

    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    if openai_key and not openai_key.startswith("sk-..."):
        print(f"  ✅ OpenAI API Key configured")
    else:
        print(f"  ⚠️  OpenAI API Key not configured (required for AI orchestration)")

    if anthropic_key and not anthropic_key.startswith("sk-ant-..."):
        print(f"  ✅ Anthropic API Key configured")
    else:
        print(f"  ⚠️  Anthropic API Key not configured (required for AI orchestration)")

    return True

def test_zazzle_client():
    """Test Zazzle client initialization"""
    print("\n🏪 Testing Zazzle client...")

    try:
        from antigravity.integrations.zazzle import ZazzleClient

        client = ZazzleClient()
        print(f"  ✅ Client initialized")
        print(f"  ✅ Store URL: {client.get_store_url()}")

        # Test templates
        from antigravity.integrations.zazzle import ZAZZLE_TEMPLATES
        print(f"  ✅ {len(ZAZZLE_TEMPLATES)} product templates available")

        return True
    except Exception as e:
        print(f"  ❌ Failed to initialize Zazzle client: {e}")
        return False

def test_dry_run():
    """Test dry run mode"""
    print("\n🧪 Testing dry run mode...")

    try:
        from antigravity.pod.zazzle_orchestrator import ZazzlePODOrchestrator

        orchestrator = ZazzlePODOrchestrator(dry_run=True)
        print(f"  ✅ Orchestrator initialized in dry-run mode")

        return True
    except Exception as e:
        print(f"  ❌ Failed to initialize orchestrator: {e}")
        return False

def main():
    print("=" * 60)
    print("  ZAZZLE INTEGRATION TEST")
    print("=" * 60)
    print()

    tests = [
        ("Module imports", test_imports),
        ("Configuration", test_configuration),
        ("Zazzle client", test_zazzle_client),
        ("Dry run mode", test_dry_run),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("  TEST RESULTS")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")

    print()
    print(f"  {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your Zazzle integration is ready to use.")
        print("\nNext steps:")
        print("  1. Create a test design image")
        print("  2. Run: python3 -m antigravity.zazzle_cli design your_design.png --dry-run")
        print()
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
        print("  See ZAZZLE_QUICKSTART.md for setup instructions.")
        print()

    print("=" * 60)

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())

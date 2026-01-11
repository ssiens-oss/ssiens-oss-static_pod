#!/usr/bin/env python3
"""
Standalone Zazzle integration test (avoids Python's antigravity Easter egg)
"""
import os
import sys
from pathlib import Path

def test_environment():
    """Test environment setup"""
    print("🧪 Testing environment setup...")

    # Check if antigravity directory exists
    antigravity_dir = Path(__file__).parent / "antigravity"
    if not antigravity_dir.exists():
        print(f"  ❌ antigravity directory not found at {antigravity_dir}")
        return False
    print(f"  ✅ antigravity directory found")

    # Check if .env exists
    env_file = antigravity_dir / ".env"
    if not env_file.exists():
        print(f"  ❌ .env file not found")
        return False
    print(f"  ✅ .env file exists")

    return True

def test_configuration():
    """Test configuration"""
    print("\n⚙️  Testing configuration...")

    # Load .env
    env_file = Path(__file__).parent / "antigravity" / ".env"
    config = {}

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key] = value

    # Check Zazzle config
    checks = []

    associate_id = config.get("ZAZZLE_ASSOCIATE_ID", "")
    if associate_id and associate_id != "your-associate-id":
        print(f"  ✅ Associate ID: {associate_id}")
        checks.append(True)
    else:
        print(f"  ❌ Associate ID not configured")
        checks.append(False)

    store_id = config.get("ZAZZLE_STORE_ID", "")
    if store_id and store_id != "your-store-id":
        print(f"  ✅ Store ID: {store_id}")
        checks.append(True)
    else:
        print(f"  ❌ Store ID not configured")
        checks.append(False)

    # Check API keys
    openai_key = config.get("OPENAI_API_KEY", "")
    if openai_key and not openai_key.startswith("sk-..."):
        print(f"  ✅ OpenAI API Key configured")
        checks.append(True)
    else:
        print(f"  ⚠️  OpenAI API Key not configured")
        checks.append(False)

    anthropic_key = config.get("ANTHROPIC_API_KEY", "")
    if anthropic_key and not anthropic_key.startswith("sk-ant-..."):
        print(f"  ✅ Anthropic API Key configured")
        checks.append(True)
    else:
        print(f"  ⚠️  Anthropic API Key not configured")
        checks.append(False)

    return all(checks)

def test_dependencies():
    """Test Python dependencies"""
    print("\n📦 Testing dependencies...")

    dependencies = [
        ("pydantic", "Pydantic"),
        ("anthropic", "Anthropic SDK"),
        ("openai", "OpenAI SDK"),
        ("playwright", "Playwright"),
    ]

    checks = []
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"  ✅ {display_name} installed")
            checks.append(True)
        except ImportError:
            print(f"  ❌ {display_name} not installed")
            checks.append(False)

    return all(checks)

def test_module_imports():
    """Test module imports without triggering antigravity Easter egg"""
    print("\n🔌 Testing module imports...")

    # Add antigravity directory to path
    antigravity_dir = Path(__file__).parent / "antigravity"
    sys.path.insert(0, str(antigravity_dir))

    try:
        # Import using exec to avoid triggering the Easter egg
        from models import PODOffer, ModelResponse
        print(f"  ✅ Models imported successfully")

        from integrations.zazzle import ZazzleClient, ZAZZLE_TEMPLATES
        print(f"  ✅ Zazzle integration imported")
        print(f"  ✅ {len(ZAZZLE_TEMPLATES)} product templates available")

        # Test client initialization
        client = ZazzleClient()
        print(f"  ✅ Zazzle client initialized")
        print(f"  ✅ Store URL: {client.get_store_url()}")

        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("  ZAZZLE INTEGRATION TEST")
    print("=" * 60)
    print()

    tests = [
        ("Environment setup", test_environment),
        ("Configuration", test_configuration),
        ("Dependencies", test_dependencies),
        ("Module imports", test_module_imports),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
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
        print("\n🎉 All tests passed! Your Zazzle integration is ready.")
        print("\nNext steps:")
        print("  cd ~/ssiens-oss-static_pod")
        print("  python3 -m antigravity.zazzle_cli design your_design.png --dry-run")
        print()
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        if not results[2][1]:  # Dependencies test failed
            print("\n  Install dependencies:")
            print("    cd ~/ssiens-oss-static_pod/antigravity")
            print("    pip3 install -r requirements.txt")
        print()

    print("=" * 60)

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())

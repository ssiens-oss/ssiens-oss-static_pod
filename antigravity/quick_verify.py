#!/usr/bin/env python3
"""
Quick verification of Zazzle configuration without heavy dependencies
"""
import os
from pathlib import Path

# Load environment variables
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

print("=" * 50)
print("  ZAZZLE CONFIGURATION VERIFICATION")
print("=" * 50)
print()

# Check Zazzle credentials
associate_id = os.getenv("ZAZZLE_ASSOCIATE_ID", "")
store_id = os.getenv("ZAZZLE_STORE_ID", "")
api_key = os.getenv("ZAZZLE_API_KEY", "")
default_template = os.getenv("ZAZZLE_DEFAULT_TEMPLATE", "tshirt_basic")
enable_zazzle = os.getenv("ENABLE_ZAZZLE", "true")

print("📋 Credentials Status:")
print()

if associate_id and associate_id not in ["your-associate-id", ""]:
    print(f"  ✅ Ambassador ID: {associate_id}")
else:
    print(f"  ❌ Ambassador ID: Not configured")

if store_id and store_id not in ["your-store-id", ""]:
    print(f"  ✅ Store ID: {store_id}")
else:
    print(f"  ❌ Store ID: Not configured")

if api_key and api_key not in ["your-api-key", ""]:
    masked_key = api_key[:12] + "..." if len(api_key) > 12 else "***"
    print(f"  ⚠️  API Key: {masked_key} (optional)")
else:
    print(f"  ⚠️  API Key: Not configured (optional for most operations)")

print()
print("⚙️  Configuration:")
print(f"  • Default Template: {default_template}")
print(f"  • Zazzle Enabled: {enable_zazzle}")
print()

# Generate store URL
if store_id and store_id not in ["your-store-id", ""]:
    store_url = f"https://www.zazzle.com/store/{store_id}"
    print("🔗 Your Zazzle Store:")
    print(f"  {store_url}")
    print()

# Check API keys for AI models
print("🤖 AI Model APIs (required for orchestration):")
print()

openai_key = os.getenv("OPENAI_API_KEY", "")
anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
grok_key = os.getenv("GROK_API_KEY", "")

if openai_key and not openai_key.startswith("sk-..."):
    print(f"  ✅ OpenAI API Key: Configured")
else:
    print(f"  ❌ OpenAI API Key: Not configured")

if anthropic_key and not anthropic_key.startswith("sk-ant-..."):
    print(f"  ✅ Anthropic API Key: Configured")
else:
    print(f"  ❌ Anthropic API Key: Not configured")

if grok_key:
    print(f"  ⚠️  Grok API Key: Configured (currently using mock)")
else:
    print(f"  ⚠️  Grok API Key: Not configured (optional, using mock)")

print()
print("=" * 50)

# Provide next steps
if associate_id and store_id:
    print("✅ READY TO USE!")
    print()
    print("Next steps:")
    print("  1. Wait for pip install to complete")
    print("  2. Install Playwright browsers:")
    print("     cd /home/user/ssiens-oss-static_pod/antigravity")
    print("     python3 -m playwright install")
    print()
    print("  3. Test with dry run:")
    print("     python3 -m antigravity.zazzle_cli design your_design.png --dry-run")
    print()
else:
    print("⚠️  Please configure your Zazzle credentials in .env")
    print("   See ZAZZLE_QUICKSTART.md for instructions")

print("=" * 50)

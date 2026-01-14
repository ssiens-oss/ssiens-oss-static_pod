#!/usr/bin/env python3
"""
Verify RunPod Serverless Configuration
Checks if credentials are properly set in .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

print("🔍 Checking RunPod Serverless Configuration...\n")

# Check API Key
api_key = os.environ.get("RUNPOD_API_KEY")
if api_key:
    if len(api_key) > 10:
        print(f"✅ RUNPOD_API_KEY: Set ({api_key[:10]}...{api_key[-4:]})")
    else:
        print(f"❌ RUNPOD_API_KEY: Too short or empty")
        print(f"   Current value: '{api_key}'")
else:
    print("❌ RUNPOD_API_KEY: Not found in .env")
    print("   Add: RUNPOD_API_KEY=sk_live_your_key")

print()

# Check Endpoint ID
endpoint_id = os.environ.get("RUNPOD_ENDPOINT_ID")
if endpoint_id:
    if len(endpoint_id) > 5:
        print(f"✅ RUNPOD_ENDPOINT_ID: Set ({endpoint_id})")
    else:
        print(f"❌ RUNPOD_ENDPOINT_ID: Too short or empty")
        print(f"   Current value: '{endpoint_id}'")
else:
    print("❌ RUNPOD_ENDPOINT_ID: Not found in .env")
    print("   Add: RUNPOD_ENDPOINT_ID=your_endpoint_id")

print()

# Summary
if api_key and endpoint_id and len(api_key) > 10 and len(endpoint_id) > 5:
    print("✅ Configuration looks good!")
    print("\nYou can now run:")
    print("   python comfyui_serverless.py")
else:
    print("❌ Configuration incomplete")
    print("\n📋 To fix:")
    print("   1. Deploy endpoint: https://runpod.io/console/serverless")
    print("   2. Get your API key: Profile → Settings → API Keys")
    print("   3. Edit .env: cd ~/ssiens-oss-static_pod && nano .env")
    print("   4. Add your credentials and save")

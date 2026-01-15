#!/usr/bin/env python3
"""
Comprehensive Printify API test
Tests API key validity and finds correct shop ID
"""
from dotenv import load_dotenv
import os
import requests

load_dotenv('../.env')

api_key = os.getenv('PRINTIFY_API_KEY')
shop_id = os.getenv('PRINTIFY_SHOP_ID')

print("🔍 Printify API Diagnostic")
print("=" * 60)
print(f"\nAPI Key: {api_key[:20] if api_key else 'NOT SET'}...")
print(f"Shop ID: {shop_id}")

if not api_key:
    print("\n❌ PRINTIFY_API_KEY not set in .env")
    print("   Get your API key from: https://printify.com/app/account/api")
    exit(1)

headers = {'Authorization': f'Bearer {api_key}'}

# Test 1: Check API key validity by listing shops
print("\n📋 Test 1: List all shops accessible with this API key")
print("-" * 60)

try:
    response = requests.get(
        'https://api.printify.com/v1/shops.json',
        headers=headers,
        timeout=10
    )

    print(f"Status: {response.status_code}")

    if response.ok:
        shops = response.json()
        print(f"✅ API key is valid!")
        print(f"\n📊 Found {len(shops)} shop(s):\n")

        for shop in shops:
            shop_id_found = shop.get('id')
            shop_title = shop.get('title', 'Unknown')
            print(f"   Shop ID: {shop_id_found}")
            print(f"   Title: {shop_title}")
            print(f"   Sales Channel: {shop.get('sales_channel', 'N/A')}")

            if str(shop_id_found) == str(shop_id):
                print(f"   ✅ MATCHES your configured shop ID!\n")
            else:
                print(f"   ⚠️  Different from your configured ID ({shop_id})\n")

        if shops:
            correct_shop_id = shops[0]['id']
            print(f"\n💡 Update your .env with:")
            print(f"   PRINTIFY_SHOP_ID={correct_shop_id}")
    else:
        print(f"❌ API key invalid or expired")
        print(f"   Error: {response.text}")
        print(f"\n💡 Get a new API key from:")
        print(f"   https://printify.com/app/account/api")

except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: If shop ID exists, try to access it
if shop_id:
    print(f"\n📋 Test 2: Access shop {shop_id} directly")
    print("-" * 60)

    try:
        response = requests.get(
            f'https://api.printify.com/v1/shops/{shop_id}.json',
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.ok:
            shop = response.json()
            print(f"✅ Shop accessible!")
            print(f"   Title: {shop.get('title')}")
            print(f"   Sales Channel: {shop.get('sales_channel')}")
        else:
            print(f"❌ Cannot access shop {shop_id}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Test 3: Check blueprint 77 (Gildan 18500 Hoodie)
print(f"\n📋 Test 3: Verify Blueprint 77 (Gildan 18500)")
print("-" * 60)

try:
    response = requests.get(
        'https://api.printify.com/v1/catalog/blueprints/77.json',
        headers=headers,
        timeout=10
    )

    if response.ok:
        blueprint = response.json()
        print(f"✅ Blueprint 77: {blueprint.get('title')}")
        print(f"   Brand: {blueprint.get('brand')}")
        print(f"   Model: {blueprint.get('model')}")
    else:
        print(f"⚠️  Cannot access blueprint 77")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("\n✅ Diagnostic complete!")
print("\n📋 Next steps:")
print("   1. Update PRINTIFY_SHOP_ID in .env if needed")
print("   2. Restart gateway: ./start.sh")
print("   3. Try publishing again")

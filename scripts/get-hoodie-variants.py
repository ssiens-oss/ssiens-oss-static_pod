#!/usr/bin/env python3
"""Get hoodie variant IDs from Printify API"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")

headers = {
    "Authorization": f"Bearer {PRINTIFY_API_KEY}"
}

# Get blueprint details for hoodie
blueprint_id = 12
print_provider_id = 99

url = f"https://api.printify.com/v1/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json"

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Found {len(data['variants'])} variants")
    print("\nVariant IDs (copy these to bulk-publish-hoodies.py):")
    print("[")
    for i, variant in enumerate(data['variants']):
        print(f'    {{"id": {variant["id"]}, "price": 3499, "is_enabled": True}},  # {variant["title"]}')
    print("]")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

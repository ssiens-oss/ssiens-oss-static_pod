from pathlib import Path
import pandas as pd
import uuid

# ---- CONFIG ----
OUT_DIR = Path("exports")
OUT_DIR.mkdir(exist_ok=True)

PRODUCTS_DIR = Path("queues/published")
BASE_PRICE = 49.99
INVENTORY = 999
CATEGORY = "Apparel & Accessories > Clothing > Hoodies"
BRAND = "StaticWaves"

rows = []

for img in PRODUCTS_DIR.glob("*.png"):
    sku = f"SW-{uuid.uuid4().hex[:8].upper()}"

    rows.append({
        "product_name": f"StaticWaves Hoodie – {img.stem}",
        "description": "Premium StaticWaves hoodie. Limited glitch drop.",
        "price": int(BASE_PRICE),              # TikTok prefers ints
        "quantity": INVENTORY,                  # Prevent auto-disable
        "sku": sku,
        "image_url": f"https://yourcdn.com/{img.name}",
        "category": CATEGORY,
        "shipping_weight": "0.5",
        "brand": BRAND,
        "condition": "New"
    })

df = pd.DataFrame(rows)

out = OUT_DIR / "tiktok_shop_feed.xlsx"
df.to_excel(out, index=False)

print(f"✅ TikTok Shop feed generated → {out}")

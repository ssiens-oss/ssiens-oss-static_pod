import os, requests, base64
from pathlib import Path
from core.logger import get_logger

log = get_logger("SHOPIFY")

STORE = os.environ["SHOPIFY_STORE"]
TOKEN = os.environ["SHOPIFY_TOKEN"]

HEAD = {
    "X-Shopify-Access-Token": TOKEN,
    "Content-Type": "application/json"
}

for img in Path("queues/published").glob("*.png"):
    with open(img,"rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    r = requests.post(
        f"https://{STORE}.myshopify.com/admin/api/2024-01/products.json",
        headers=HEAD,
        json={
            "product": {
                "title": f"StaticWaves Drop {img.stem}",
                "images": [{"attachment": b64}],
                "variants": [{"price": "49.99", "inventory_management": "shopify"}]
            }
        }
    )
    r.raise_for_status()
    log.info(f"Published → {img.name}")
    img.unlink()

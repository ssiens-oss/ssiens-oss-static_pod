import os, requests
from pathlib import Path
from core.retry import safe_retry
from core.logger import get_logger

log = get_logger("PRINTIFY")

HEAD = {
    "Authorization": f"Bearer {os.environ['PRINTIFY_API_KEY']}"
}

SHOP = os.environ["PRINTIFY_SHOP_ID"]
IN = Path("queues/published")

@safe_retry()
def upload(img):
    with open(img,"rb") as f:
        r = requests.post(
            "https://api.printify.com/v1/uploads/images.json",
            headers=HEAD,
            files={"file": f}
        )
    r.raise_for_status()
    return r.json()["id"]

for img in IN.glob("*.png"):
    try:
        img_id = upload(img)
        log.info(f"Uploaded → {img_id}")
        img.unlink()
    except Exception as e:
        log.error(e)

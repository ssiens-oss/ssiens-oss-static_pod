from rembg import remove
from PIL import Image
from pathlib import Path
from core.logger import get_logger

log = get_logger("RMBG")

IN = Path("queues/incoming")
OUT = Path("queues/processed")

OUT.mkdir(parents=True, exist_ok=True)

while True:
    for img in IN.glob("*.png"):
        try:
            log.info(f"RMBG → {img.name}")
            out = OUT / img.name
            i = Image.open(img)
            r = remove(i)
            r.save(out)
            img.unlink()
        except Exception as e:
            log.error(e)

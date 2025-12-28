from PIL import Image
from pathlib import Path
from core.logger import get_logger

log = get_logger("MOCKUP")

BASE = Image.open("assets/hoodie_base.png")
IN = Path("queues/processed")
OUT = Path("queues/published")

OUT.mkdir(parents=True, exist_ok=True)

for design in IN.glob("*.png"):
    img = BASE.copy()
    d = Image.open(design).resize((800,800))
    img.paste(d, (600,500), d)
    out = OUT / design.name
    img.save(out)
    design.unlink()
    log.info(f"Mockup ready → {out.name}")

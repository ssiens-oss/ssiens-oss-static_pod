import cv2
import numpy as np
import os
import shutil
from collections import defaultdict

IN_DIR = "/workspace/ComfyUI/output"
OUT_DIR = "/workspace/staticwaves-pod/winners"
KEEP_PER_PROMPT = 3

os.makedirs(OUT_DIR, exist_ok=True)

def score_image(path):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return 0

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Edge density (boldness)
    edges = cv2.Canny(gray, 100, 200)
    edge_score = np.mean(edges > 0)

    # Contrast
    contrast = gray.std() / 255.0

    # Blur penalty
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    blur_score = min(blur / 1000.0, 1.0)

    # Foreground coverage (assumes transparent bg)
    if img.shape[2] == 4:
        alpha = img[:, :, 3]
        fg_ratio = np.mean(alpha > 10)
    else:
        fg_ratio = 0.5

    score = (
        edge_score * 2.5 +
        contrast * 2.0 +
        blur_score * 2.0 +
        fg_ratio * 1.5
    )

    return score

# Group images by prompt batch (every 20)
files = sorted([f for f in os.listdir(IN_DIR) if f.endswith(".png")])
groups = defaultdict(list)

for idx, f in enumerate(files):
    prompt_id = idx // 20
    groups[prompt_id].append(f)

kept = 0
deleted = 0

for prompt_id, imgs in groups.items():
    scored = []
    for f in imgs:
        path = os.path.join(IN_DIR, f)
        s = score_image(path)
        scored.append((s, f))

    scored.sort(reverse=True, key=lambda x: x[0])
    winners = scored[:KEEP_PER_PROMPT]
    losers = scored[KEEP_PER_PROMPT:]

    for _, f in winners:
        shutil.copy2(
            os.path.join(IN_DIR, f),
            os.path.join(OUT_DIR, f)
        )
        kept += 1

    for _, f in losers:
        os.remove(os.path.join(IN_DIR, f))
        deleted += 1

print(f"🏆 Winners kept: {kept}")
print(f"🗑️ Variants removed: {deleted}")
print("✅ Auto-ranking complete")

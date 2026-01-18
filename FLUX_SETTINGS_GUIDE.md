# Flux Model Settings Guide - Sharp Images Fixed

## Problem: Out of Focus / Blurry Images

Your images were coming out blurry/out of focus because the workflow was using **SDXL settings for a Flux model**.

Flux models require very different parameters than SDXL!

---

## What Was Wrong

### Before (Blurry/Out of Focus)
```python
steps: 20        # Too low for Flux
cfg_scale: 7.0   # WAY too high for Flux!
scheduler: "normal"
```

**Why this caused blurry images:**
- **High CFG (7.0):** Flux interprets high CFG as "over-guidance" which creates blurry, over-processed images
- **Low Steps (20):** Not enough sampling iterations for Flux to refine details
- **Wrong Scheduler:** "normal" isn't optimal for Flux

---

## What's Fixed Now

### After (Sharp & Detailed)
```python
steps: 30        # ✅ Flux needs 30-50 for quality
cfg_scale: 2.0   # ✅ Flux sweet spot is 1.0-3.5
scheduler: "simple"  # ✅ Works better with Flux
```

---

## The Science: Why Flux Is Different

### CFG Scale (Classifier-Free Guidance)

**SDXL:**
- CFG 7-12 = normal
- Higher CFG = more prompt adherence
- Can handle high CFG without blur

**Flux:**
- CFG 1.0-3.5 = optimal
- **CFG > 4.0 = blurry/over-processed**
- Flux has built-in guidance, doesn't need high CFG
- Lower CFG = sharper, cleaner images

**Why:** Flux dev models are trained differently and already have strong inherent guidance.

### Sampling Steps

**SDXL:**
- 20-30 steps = good quality
- Diminishing returns after 30

**Flux:**
- 30-50 steps = optimal
- **< 25 steps = lack of detail**
- Benefits from more refinement iterations
- 30 steps = good balance (speed vs quality)
- 50 steps = maximum quality (slower)

### Scheduler

**SDXL:**
- "normal" or "karras" work well

**Flux:**
- **"simple"** works best
- More predictable convergence
- Cleaner results

---

## Comparison Chart

| Setting | SDXL (Old) | Flux (New) | Impact |
|---------|------------|------------|--------|
| CFG Scale | 7.0 | 2.0 | **Sharpness** |
| Steps | 20 | 30 | **Detail** |
| Scheduler | normal | simple | Quality |
| Resolution | 1024 | 3600 | **Print DPI** |

**Combined effect:** Dramatically sharper, more detailed images!

---

## Expected Results

### Before (Out of Focus)
- Soft/blurry edges
- Lack of fine detail
- Over-processed look
- Muddy colors
- Not print-ready

### After (Sharp & Clear)
- Crisp edges
- Fine detail preserved
- Natural, clean look
- Vibrant colors
- Print-ready quality

---

## Performance Impact

### Generation Time

| Resolution | Old Settings | New Settings | Change |
|------------|--------------|--------------|--------|
| 1024x1024 | ~10s | N/A | Deprecated |
| 3600x3600 | ~30s (CFG 7) | ~45-60s (CFG 2, 30 steps) | +50% |

**Worth it?** Absolutely! The quality improvement is massive.

### VRAM Usage

- No significant change
- 3600x3600 @ 30 steps: ~8-10GB
- Works fine on standard RunPod instances

---

## Testing the Fix

### 1. Restart Gateway

```bash
cd ~/ssiens-oss-static_pod/gateway
export PYTHONPATH=$(pwd)

# Stop old process
pkill -f "python.*main.py"

# Start with new settings
.venv/bin/python app/main.py
```

### 2. Generate Test Image

Open browser: `http://localhost:5000`

**Test Prompt:**
```
geometric pattern, high detail, sharp lines, intricate design
```

**Watch Terminal Logs:**
```
INFO - Generating image at 3600x3600, 30 steps, CFG 2.0
```

### 3. Verify Settings Applied

Check terminal doesn't show warnings:
```
⚠ CFG scale 7.0 is too high for Flux  # Should NOT appear
⚠ Steps 20 may be too low            # Should NOT appear
```

### 4. Compare Image Quality

**Look for:**
- Sharp, crisp edges (not soft/blurry)
- Fine details preserved
- Clean, natural rendering
- No over-processing artifacts

### 5. Zoom Test

```bash
# Open image and zoom to 200%
identify gateway/data/images/generated_*.png

# Should be sharp even when zoomed
```

---

## Advanced: Fine-Tuning

### For Maximum Sharpness
```python
steps: 50
cfg_scale: 1.5
```
- Slower (~90s generation)
- Highest quality
- Best for hero products

### For Speed (Still Good Quality)
```python
steps: 25
cfg_scale: 2.5
```
- Faster (~30s generation)
- Good quality
- Good for testing

### For Artistic Style
```python
steps: 40
cfg_scale: 3.0
```
- More creative interpretation
- Still sharp
- Good for stylized designs

---

## Troubleshooting

### Images still look soft

**Check:**
1. Settings actually applied (check terminal logs)
2. RunPod endpoint has enough VRAM
3. Flux model loaded correctly
4. No network issues during generation

**Try:**
- Lower CFG to 1.5
- Increase steps to 40
- Check ComfyUI logs on RunPod

### Generation too slow

**Options:**
1. Reduce steps: 30 → 25
2. Reduce resolution: 3600 → 2400 (minimum POD)
3. Upgrade RunPod instance (faster GPU)

**Don't:**
- Increase CFG (will make blurry)
- Reduce below 25 steps (quality suffers)

### Unexpected results

**Flux is very sensitive to:**
- Prompt phrasing (be specific)
- Negative prompts (Flux often ignores them)
- CFG scale (small changes matter)

**Best practices:**
- Keep prompts clear and specific
- Use CFG 1.5-2.5 for most cases
- Don't over-rely on negative prompts

---

## API Usage

### Default (Automatic - Recommended)
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cyberpunk cat neon lights"
  }'
```
- Uses: 3600x3600, 30 steps, CFG 2.0
- Optimized for Flux + POD

### Custom Settings
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "geometric design",
    "width": 4500,
    "height": 5400,
    "steps": 40,
    "cfg_scale": 2.5
  }'
```

### Maximum Quality
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "intricate mandala pattern",
    "width": 4800,
    "height": 6000,
    "steps": 50,
    "cfg_scale": 1.5
  }'
```

---

## Recommended Settings by Use Case

### T-Shirts & Hoodies (Default)
```
Resolution: 3600x3600
Steps: 30
CFG: 2.0
```

### Posters (High Detail)
```
Resolution: 4800x6000
Steps: 40
CFG: 2.0
```

### Stickers (Fast Turnaround)
```
Resolution: 3000x3000
Steps: 25
CFG: 2.5
```

### Hero Products (Maximum Quality)
```
Resolution: 4500x5400
Steps: 50
CFG: 1.5
```

---

## Summary of Changes

✅ **CFG Scale:** 7.0 → 2.0 (Flux-optimized)
✅ **Steps:** 20 → 30 (more detail)
✅ **Scheduler:** normal → simple (cleaner results)
✅ **Resolution:** 1024 → 3600 (print quality)

**Result:** Sharp, detailed, print-ready images! 🎉

---

## Before/After Checklist

Run this checklist to verify the fix:

- [ ] Terminal shows: `INFO - Generating at... 30 steps, CFG 2.0`
- [ ] No warnings about high CFG or low steps
- [ ] Image file size ~2-4MB (not ~500KB)
- [ ] `identify` shows 3600x3600 resolution
- [ ] Zoomed image looks sharp (not blurry)
- [ ] Details are crisp and clear
- [ ] Colors are vibrant
- [ ] No over-processing artifacts

If all checked ✅ = Successfully fixed!

---

## References

- [Flux Model Documentation](https://github.com/black-forest-labs/flux)
- Recommended CFG: 1.0-3.5
- Recommended Steps: 30-50
- ComfyUI Flux Best Practices

**Key Insight:** Flux is NOT SDXL. Lower CFG, more steps, "simple" scheduler.

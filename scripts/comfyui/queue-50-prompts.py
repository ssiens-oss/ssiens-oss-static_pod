#!/usr/bin/env python3
"""
StaticWaves 50-Prompt Auto-Queue for ComfyUI
Queues 25 Cryptid + 25 Brain Rot prompts optimized for POD streetwear
"""

import requests
import uuid
import random
import time
import os
import sys

# Configuration
COMFY_API = os.getenv("COMFYUI_API_URL", "http://127.0.0.1:8188/prompt")
MODEL_NAME = os.getenv("COMFYUI_MODEL", "sdxl_base_1.0.safetensors")  # or v1-5-pruned-emaonly.safetensors
USE_SDXL = "sdxl" in MODEL_NAME.lower()

# Resolution settings
if USE_SDXL:
    WIDTH = 1024
    HEIGHT = 1024
    STEPS = 34
    CFG = 7
    SAMPLER = "dpmpp_2m"
    SCHEDULER = "karras"
    BATCH_SIZE = 2
else:
    WIDTH = 512
    HEIGHT = 512
    STEPS = 28
    CFG = 7
    SAMPLER = "euler"
    SCHEDULER = "normal"
    BATCH_SIZE = 4

# Brand anchor (prepended to all prompts)
BRAND_ANCHOR = "StaticWaves aesthetic, neon glitch streetwear, cyberpunk signal distortion, purple teal palette, bold graphic silhouette, futuristic underground fashion"

NEGATIVE = "photorealistic, realistic fabric, folds, shadows, mockups, models, people, faces, background, scenery, gradients, blurry, low contrast, jpeg artifacts, watermark, text blocks"

# 25 Cryptid Prompts
CRYPTID_PROMPTS = [
    "Neon cryptid wolf mascot, cyberpunk glitch distortion, bold vector outlines, centered logo, transparent background",
    "Mechanical cryptid bear, circuit-board textures, aggressive streetwear emblem, high contrast",
    "Cyber serpent mascot, fractal scales, digital noise, futuristic streetwear logo",
    "Glitch demon ram mascot, CRT scanlines, datamosh tearing, bold silhouette",
    "Neon crow cryptid, holographic glitch wings, underground cyber aesthetic",
    "AI cryptid tiger head, sharp geometry, signal distortion, logo-ready",
    "Cyberpunk goat demon mascot, broken neon horns, glitch corruption",
    "Futuristic cryptid owl, glowing eyes, pixel interference, minimal vector style",
    "Neon wolf skull cryptid, digital decay, brutalist streetwear emblem",
    "Synthetic dragon mascot, circuit anatomy, glitch overlays, flat graphic lighting",
    "Cryptid ape mascot, distorted signal waves, aggressive fashion logo",
    "Cyber fox cryptid, hologram glitch effects, thick outlines, brand mark",
    "Neon bull demon mascot, fractured geometry, datamosh artifacts",
    "AI-generated cryptid moth, glowing sigils, cyberpunk noise",
    "Mechanical cryptid dog, exposed circuitry, glitchwave distortion",
    "Cyberpunk spider cryptid, angular limbs, digital interference",
    "Neon cryptid raven skull, CRT glow, underground streetwear logo",
    "Futuristic cryptid panther, energy outlines, glitch tears",
    "Demon fish cryptid mascot, cyberpunk bioluminescence, bold silhouette",
    "Cryptid wolf sigil, sacred geometry fused with circuitry",
    "Cybernetic cryptid bat, radar-wave glitches, flat vector style",
    "Neon horned cryptid skull, signal corruption, logo composition",
    "AI chimera mascot, mixed animal geometry, cyber glitch effects",
    "Digital cryptid guardian, totemic pose, neon noise accents",
    "Synthetic cryptid beast emblem, minimal palette, screen-print friendly"
]

# 25 Brain Rot Prompts
BRAINROT_PROMPTS = [
    "Surreal brain rot creature, chaotic glitch artifacts, hyper-saturated neon, transparent background",
    "Meme-core distorted face, uncanny proportions, CRT noise, viral energy",
    "Glitch emoji demon, corrupted pixels, absurdist streetwear graphic",
    "Internet horror mascot, low-poly distortion, neon datamosh",
    "Chaotic cyber gremlin, overstimulated colors, meme aesthetics",
    "AI hallucination entity, fragmented geometry, brainrot visual overload",
    "Surreal glitch clown, corrupted signal effects, unsettling meme art",
    "Digital brain rot monster, melted face, pixel tearing",
    "Neon goblin meme creature, exaggerated features, glitch chaos",
    "Absurd cyber creature, cursed internet energy, bold silhouette",
    "Meme demon head, hyper-chaotic glitch layers, TikTok-core style",
    "Uncanny synthetic face, distorted eyes, CRT burn-in artifacts",
    "Glitchcore horror emoji, broken pixels, viral absurdism",
    "Surreal internet cryptid, meme distortion, oversaturated neon",
    "Corrupted AI mascot, uncanny valley, datamosh overload",
    "Brain rot angel, broken halo, meme chaos, digital noise",
    "Digital nightmare creature, cursed proportions, glitch corruption",
    "Meme-core cyber imp, exaggerated grin, pixel chaos",
    "Distorted cartoon demon, overstimulation aesthetic, glitch spam",
    "AI brain melt entity, warped geometry, neon interference",
    "Chaotic signal ghost, cursed internet meme style",
    "Digital hallucination face, fragmented features, glitch saturation",
    "Glitch creature collage, absurd internet artifacts, bold graphic style",
    "Unhinged cyber meme mascot, datamosh tearing, viral intensity",
    "Brain rot totem creature, surreal chaos, underground meme culture"
]

ALL_PROMPTS = CRYPTID_PROMPTS + BRAINROT_PROMPTS

def build_workflow(prompt_text: str, index: int):
    """Build ComfyUI workflow JSON"""
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": MODEL_NAME}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["1", 1],
                "text": f"{BRAND_ANCHOR}, {prompt_text}"
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["1", 1],
                "text": NEGATIVE
            }
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": WIDTH,
                "height": HEIGHT,
                "batch_size": BATCH_SIZE
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
                "seed": random.randint(0, 2**32),
                "steps": STEPS,
                "cfg": CFG,
                "sampler_name": SAMPLER,
                "scheduler": SCHEDULER,
                "denoise": 1.0
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["5", 0],
                "vae": ["1", 2]
            }
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["6", 0],
                "filename_prefix": f"staticwaves_{index:02d}"
            }
        }
    }

    return {
        "prompt": workflow,
        "client_id": str(uuid.uuid4())
    }

def queue_prompt(prompt_text: str, index: int):
    """Queue a single prompt to ComfyUI"""
    payload = build_workflow(prompt_text, index)

    try:
        response = requests.post(COMFY_API, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to queue prompt {index}: {e}")
        return False

def main():
    print("╔════════════════════════════════════════════════════╗")
    print("║  StaticWaves 50-Prompt Auto-Queue               ║")
    print("╚════════════════════════════════════════════════════╝")
    print("")
    print(f"🎨 Model: {MODEL_NAME}")
    print(f"📐 Resolution: {WIDTH}×{HEIGHT}")
    print(f"⚙️  Settings: {STEPS} steps, CFG {CFG}, {SAMPLER}")
    print(f"📦 Batch size: {BATCH_SIZE}")
    print(f"🔢 Total prompts: {len(ALL_PROMPTS)}")
    print("")

    # Test connection
    try:
        test_url = COMFY_API.replace("/prompt", "/system_stats")
        requests.get(test_url, timeout=5)
        print("✅ ComfyUI connection OK")
    except:
        print(f"❌ Cannot connect to ComfyUI at {COMFY_API}")
        print("Make sure ComfyUI is running")
        sys.exit(1)

    print("")
    print("🚀 Starting queue...")
    print("")

    success_count = 0
    for i, prompt in enumerate(ALL_PROMPTS, 1):
        category = "CRYPTID" if i <= 25 else "BRAINROT"
        print(f"[{i:02d}/50] {category}: {prompt[:60]}...")

        if queue_prompt(prompt, i):
            success_count += 1
            print(f"✅ Queued {i}/50")
        else:
            print(f"⚠️  Skipped {i}/50")

        time.sleep(0.2)  # Throttle requests

    print("")
    print("╔════════════════════════════════════════════════════╗")
    print(f"║  ✅ Queued {success_count}/50 prompts")
    print("╚════════════════════════════════════════════════════╝")
    print("")
    print("Next steps:")
    print("  1. Monitor ComfyUI queue")
    print("  2. Images will save to: ComfyUI/output/")
    print("  3. Auto-resize will process for Printify")
    print("  4. Auto-publish will create products")

if __name__ == "__main__":
    main()

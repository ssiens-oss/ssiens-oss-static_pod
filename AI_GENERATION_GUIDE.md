# AI Image Generation - User Guide

## Overview

The AI Image Generation feature allows you to create stunning, print-ready designs using AI powered by ComfyUI. Generate professional artwork directly from the dashboard with just a text prompt.

## Features

### 🎨 Intuitive Interface
- **Quick Start Templates**: 6+ pre-made templates for instant inspiration
- **Random Prompt Generator**: Get creative ideas with one click
- **Real-time Queue Monitoring**: Track generation progress in real-time
- **Batch Generation**: Create up to 8 images at once

### 🎯 Customization Options

#### Basic Settings
- **Prompt**: Describe what you want to see
- **Negative Prompt**: Specify what to avoid
- **Art Style**: 14 different styles including:
  - Photorealistic
  - Digital Art
  - Oil Painting
  - Watercolor
  - Anime
  - Cartoon
  - Abstract
  - 3D Render
  - Pixel Art
  - Sketch
  - Pop Art
  - Minimalist
  - Retro
  - Cyberpunk

#### Advanced Settings
- **Dimensions**: Choose from POD-standard 4500x5400 or custom sizes
- **Inference Steps**: 10-100 steps (higher = better quality, slower generation)
- **Guidance Scale**: 1-20 (how closely to follow the prompt)
- **Batch Size**: Generate 1-8 images simultaneously

## How to Use

### Step 1: Access the Generator
Click on the **"AI Generate"** tab in the main dashboard navigation.

### Step 2: Choose Your Approach

**Option A: Use a Template**
1. Browse the Quick Start Templates
2. Click on a template that matches your vision
3. The prompt and style will auto-populate
4. Customize as needed

**Option B: Write Your Own Prompt**
1. In the "Prompt" field, describe your desired image
2. Be specific and detailed for best results
3. Use the negative prompt to avoid unwanted elements
4. Select an art style from the dropdown

**Option C: Get Random Inspiration**
1. Click the "Random" button in the template section
2. A random template will be selected
3. Modify the prompt to match your needs

### Step 3: Configure Settings (Optional)

Click "Advanced Settings" to reveal additional options:
- Adjust image dimensions (4500x5400 recommended for POD)
- Set inference steps (30 recommended for quality/speed balance)
- Adjust guidance scale (7-9 recommended)
- Choose batch size if you want multiple variations

### Step 4: Generate

Click the big **"Generate Image"** button. Your generation will:
1. Queue immediately
2. Start processing (you'll see progress updates)
3. Complete in ~30-60 seconds (varies by settings)
4. Appear in the Generation Queue panel

### Step 5: Save to Library

Once generation completes:
1. View the preview in the queue panel
2. Click **"Save to Library"** to add it to your designs
3. The image is now ready for product creation!

## Generation Queue

The right panel shows all your generation jobs:

**Status Indicators:**
- 🟡 **Queued**: Waiting to start
- 🔵 **Processing**: Currently generating (with progress bar)
- 🟢 **Completed**: Ready to save
- 🔴 **Failed**: Error occurred (see error message)

## Tips for Best Results

### Writing Effective Prompts

**Good Prompts:**
- ✅ "A majestic lion with a golden mane, sunset background, photorealistic, highly detailed"
- ✅ "Abstract geometric shapes in purple and gold, modern minimalist design"
- ✅ "Cute cartoon panda eating bamboo, kawaii style, pastel colors"

**Avoid:**
- ❌ "lion" (too vague)
- ❌ "make it cool" (not descriptive)
- ❌ "something nice" (no specific details)

### Prompt Structure
```
[Subject] + [Details] + [Style/Mood] + [Quality Modifiers]

Example:
"A mountain landscape + with snow-capped peaks and a lake + at golden hour with dramatic clouds + highly detailed, 8k, professional photography"
```

### Using Negative Prompts

Add unwanted elements to avoid them:
- Common: "blurry, low quality, distorted, watermark, text"
- For people: "disfigured, deformed, bad anatomy"
- For art: "amateur, sketch, unfinished"

### Style Selection

Choose the style that matches your product type:

**T-Shirts & Hoodies:**
- Digital Art
- Pop Art
- Abstract
- Minimalist
- Cartoon

**Art Prints:**
- Photorealistic
- Oil Painting
- Watercolor
- 3D Render

**Fun/Novelty:**
- Pixel Art
- Anime
- Retro
- Cyberpunk

### Dimension Guidelines

**Standard POD (Recommended):**
- Width: 4500px
- Height: 5400px
- Perfect for t-shirts, hoodies, posters

**Preview/Testing:**
- Width: 1024px or 512px
- Height: 1024px or 512px
- Faster generation for testing prompts

## Technical Details

### Generation Process

1. **Queue**: Job created and added to queue (~instant)
2. **ComfyUI Startup**: Workflow loaded and started (~5-10 seconds)
3. **Inference**: AI generates the image (~20-50 seconds)
4. **Post-processing**: Image saved and optimized (~5 seconds)
5. **Completion**: Image ready for preview and download

### Performance

**Average Times:**
- 30 steps: ~30-40 seconds
- 50 steps: ~50-70 seconds
- 100 steps: ~90-120 seconds

**Batch Generation:**
- Each additional image adds ~20-30 seconds
- 4 images: ~2-3 minutes total

### Cost per Generation

With default settings:
- AI compute: ~$0.03 per image
- Storage: negligible
- **Total cost: ~$0.03 per design**

Compared to stock images ($10-50 each) or hiring designers ($50-200 per design), AI generation is extremely cost-effective.

## Integration with POD Workflow

### Complete Workflow

1. **Generate** → Use AI Generator to create designs
2. **Review** → Check generated images in queue
3. **Save** → Add to design library
4. **Create Products** → Navigate to Designs tab
5. **Publish** → Create products on Printify, Shopify, TikTok, etc.
6. **Sell** → Monitor analytics and profit

### Automation Possibilities

**Campaigns:**
- Create a campaign with multiple prompts
- Generate 10-50 designs automatically
- Auto-create products for all designs
- Batch publish to platforms

**A/B Testing:**
- Generate multiple variations of the same concept
- Publish all to test market response
- Keep best performers

## Troubleshooting

### Generation Failed

**Possible Causes:**
1. ComfyUI not running → Check backend logs
2. Invalid parameters → Reduce steps or dimensions
3. Model not loaded → Restart ComfyUI
4. Out of memory → Reduce batch size

**Solutions:**
- Check ComfyUI is running: `http://127.0.0.1:8188`
- Review error message in queue panel
- Try simpler prompt or lower settings
- Restart the backend service

### Slow Generation

**If generation takes >2 minutes:**
1. Reduce inference steps to 20-30
2. Decrease batch size to 1-2
3. Use smaller dimensions for testing
4. Check system resources (GPU/RAM)

### Image Quality Issues

**If images are blurry or low quality:**
1. Increase inference steps to 40-50
2. Add quality keywords to prompt: "highly detailed, 8k, professional"
3. Avoid negative prompts that are too restrictive
4. Try different art styles
5. Use higher guidance scale (8-10)

### Prompt Not Followed

**If result doesn't match prompt:**
1. Be more specific and descriptive
2. Increase guidance scale to 9-12
3. Add more detail words to prompt
4. Remove conflicting elements
5. Try a different art style

## ComfyUI Configuration

### Environment Variables

Add to your `.env` file:

```bash
# ComfyUI Settings
COMFYUI_URL=http://127.0.0.1:8188
COMFYUI_OUTPUT_DIR=/workspace/ComfyUI/output

# Generation Defaults
DEFAULT_STEPS=30
DEFAULT_GUIDANCE_SCALE=7.5
DEFAULT_WIDTH=4500
DEFAULT_HEIGHT=5400
```

### Custom Workflows

Advanced users can modify `backend/comfyui_service.py` to:
- Use custom ComfyUI workflows
- Add different models or checkpoints
- Implement LoRA support
- Add ControlNet integration
- Use custom schedulers/samplers

## API Reference

### Generate Image

```bash
POST /api/generation/generate
Authorization: Bearer <token>

{
  "prompt": "A beautiful sunset over mountains",
  "negative_prompt": "blurry, low quality",
  "style": "Photorealistic",
  "width": 4500,
  "height": 5400,
  "steps": 30,
  "guidance_scale": 7.5,
  "batch_size": 1
}
```

### List Jobs

```bash
GET /api/generation/jobs
Authorization: Bearer <token>
```

### Get Job Status

```bash
GET /api/generation/jobs/{job_id}
Authorization: Bearer <token>
```

### Save to Library

```bash
POST /api/generation/jobs/{job_id}/save
Authorization: Bearer <token>
```

## Best Practices

1. **Start Simple**: Use templates first to understand the system
2. **Test Prompts**: Generate at low resolution first, then upscale
3. **Save Good Prompts**: Keep a list of successful prompts
4. **Batch Wisely**: Generate multiple variations to pick the best
5. **Monitor Queue**: Don't queue too many jobs simultaneously
6. **Review Before Saving**: Not every generation is perfect
7. **Tag Appropriately**: Use meaningful tags when saving to library

## Future Enhancements

Planned features:
- [ ] Image-to-image generation (upload reference)
- [ ] Inpainting/editing existing designs
- [ ] LoRA and model selection in UI
- [ ] Prompt history and favorites
- [ ] One-click regeneration with variations
- [ ] Upscaling for final production
- [ ] Style transfer from uploaded images
- [ ] Scheduled batch generation

---

**Happy Creating! 🎨**

For support or questions, check the main documentation or API docs at http://localhost:8000/docs

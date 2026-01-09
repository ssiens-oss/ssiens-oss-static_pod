# 🎨 AI Auto-Prompter

**AI-powered creative prompt generator for Print-on-Demand designs**

Generate professional, creative POD design prompts using Claude AI with a beautiful web interface.

---

## 🎯 What It Does

- **Generates** creative AI art prompts optimized for POD
- **Claude AI** powered prompt generation
- **6 Quick Presets** for common design styles
- **Real-time** generation with streaming
- **Export** prompts to JSON
- **Beautiful UI** with dark gradient theme

---

## 🚀 Quick Start (RunPod)

### 1. Install
```bash
cd prompter
./install_runpod.sh
```

### 2. Configure
```bash
cp .env.example .env
# Add your ANTHROPIC_API_KEY
```

### 3. Run
```bash
./start.sh
```

### 4. Access
- Expose port **5001** in RunPod UI
- Open browser to proxy URL

---

## 🎨 Features

### **Prompt Generation**
- Theme-based generation (nature, abstract, vintage, etc.)
- Style customization (minimalist, retro, modern, etc.)
- Niche targeting (specific audiences)
- Product type selection (T-shirt, hoodie, poster, mug)
- Batch generation (1-20 prompts at once)

### **Quick Presets**
1. **Minimalist Modern** - Clean, simple designs for professionals
2. **Vintage Retro** - 70s nostalgia for vintage lovers
3. **Nature & Wildlife** - Majestic nature scenes
4. **Abstract Art** - Bold, colorful artistic designs
5. **Cyberpunk Futuristic** - Neon tech aesthetics
6. **Motivational Quotes** - Typography-based inspiration

### **Output Format**
Each prompt includes:
- **Prompt**: Detailed AI art generation instructions
- **Title**: Marketplace-ready product title
- **Tags**: SEO-optimized keywords
- **Description**: Customer-facing description

### **UI Features**
- ✅ Real-time generation progress
- ✅ One-click copy to clipboard
- ✅ Stats dashboard (prompt count, avg length)
- ✅ Responsive design (mobile-friendly)
- ✅ Auto-save to JSON files
- ✅ Beautiful gradient theme

---

## 📁 Directory Structure

```
prompter/
├── app/
│   ├── __init__.py
│   ├── main.py           # Flask app
│   ├── config.py         # Configuration
│   └── generator.py      # Claude API client
├── templates/
│   └── prompter.html     # Web UI
├── requirements.txt
├── install_runpod.sh
├── start.sh
├── .env.example
└── README.md
```

---

## 🔧 Configuration

### Required
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Optional
```env
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
CLAUDE_MODEL=claude-3-5-sonnet-20241022
PROMPTER_OUTPUT_DIR=/workspace/prompts
```

---

## 🎯 Usage Examples

### Example 1: Nature Theme
**Input:**
- Theme: nature
- Style: photorealistic, majestic
- Niche: outdoor enthusiasts
- Count: 5

**Output:**
```
Prompt: "A majestic bald eagle soaring over snow-capped mountains at golden hour, photorealistic style, dramatic lighting, ultra detailed feathers, cinematic composition..."
Title: "Freedom Flight - Majestic Eagle Art"
Tags: ["eagle", "nature", "wildlife", "mountains", "photorealistic"]
Description: "Stunning photorealistic eagle artwork perfect for nature lovers..."
```

### Example 2: Minimalist Modern
**Input:**
- Theme: minimalism
- Style: clean, geometric, simple
- Niche: young professionals
- Count: 3

**Output:**
```
Prompt: "Abstract minimalist geometric design with clean lines, muted pastel colors, modern aesthetic, simple shapes, negative space, bauhaus inspired..."
Title: "Geometric Harmony - Modern Minimalist"
Tags: ["minimalist", "geometric", "modern", "clean", "abstract"]
Description: "Sophisticated minimalist design for the modern professional..."
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/api/generate` | POST | Generate prompts |
| `/api/refine` | POST | Refine existing prompt |
| `/api/presets` | GET | Get preset configurations |
| `/health` | GET | Health check |

### Generate API Example
```bash
curl -X POST http://localhost:5001/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "cyberpunk",
    "style": "neon, futuristic",
    "niche": "tech enthusiasts",
    "count": 3,
    "product_type": "tshirt"
  }'
```

---

## 🎨 Integration with POD Pipeline

### Workflow
```
AI Prompter → ComfyUI → Gateway → Printify
```

1. **Generate Prompts** in Prompter UI
2. **Copy Prompt** to clipboard
3. **Paste into ComfyUI** for image generation
4. **Approve in Gateway** (human review)
5. **Publish to Printify** (automatic)

---

## 🐛 Troubleshooting

### Claude API not configured
```bash
# Check .env file
cat .env | grep ANTHROPIC_API_KEY

# Verify key format (starts with sk-ant-)
```

### Port already in use
```bash
# Change port in .env
FLASK_PORT=5002

# Or kill existing process
pkill -f "python app/main.py"
```

### Prompts not saving
```bash
# Check output directory permissions
ls -la /workspace/prompts

# Create manually if needed
mkdir -p /workspace/prompts
chmod 755 /workspace/prompts
```

---

## 📊 Example Session

```bash
# Install
cd prompter && ./install_runpod.sh

# Configure
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Start
./start.sh

# Output:
# 🎨 AI Auto-Prompter starting...
# 🤖 Claude Model: claude-3-5-sonnet-20241022
# ✓ Generator enabled
# 🌐 Listening on 0.0.0.0:5001
```

---

## 🎉 Summary

The **AI Auto-Prompter** is a professional prompt generation tool that:
- ✅ Uses Claude AI for creative prompts
- ✅ Optimizes for POD marketplace success
- ✅ Provides beautiful, intuitive UI
- ✅ Exports to JSON for workflow integration
- ✅ Runs on RunPod without issues

**Perfect for:** POD creators, designers, marketplace sellers

**Next:** Generate prompts → Create designs → Approve → Publish → Profit! 🚀

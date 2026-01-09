"""
AI Auto-Prompter - Main Flask Application
Web UI for generating creative POD design prompts
"""
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
load_dotenv()

# Import modules
from app import config
from app.generator import PromptGenerator

# Initialize Flask
app = Flask(__name__, template_folder='../templates')

# Initialize prompt generator
generator = None
if config.ANTHROPIC_API_KEY:
    try:
        generator = PromptGenerator(config.ANTHROPIC_API_KEY, config.CLAUDE_MODEL)
        print("✓ Claude prompt generator initialized")
    except Exception as e:
        print(f"✗ Generator failed: {e}")

@app.route('/')
def index():
    """Prompter UI"""
    return render_template('prompter.html')

@app.route('/api/generate', methods=['POST'])
def generate_prompts():
    """Generate prompts using Claude"""
    if not generator:
        return jsonify({"error": "Claude API not configured"}), 400

    data = request.json
    theme = data.get('theme', 'general')
    style = data.get('style', 'modern')
    niche = data.get('niche', 'general audience')
    count = int(data.get('count', 5))
    product_type = data.get('product_type', 'tshirt')

    try:
        prompts = generator.generate_prompts(
            theme=theme,
            style=style,
            niche=niche,
            count=count,
            product_type=product_type
        )

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(config.OUTPUT_DIR) / f"prompts_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(prompts, f, indent=2)

        return jsonify({
            "success": True,
            "prompts": prompts,
            "saved": str(output_file)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/refine', methods=['POST'])
def refine_prompt():
    """Refine an existing prompt"""
    if not generator:
        return jsonify({"error": "Claude API not configured"}), 400

    data = request.json
    original = data.get('original')
    improvements = data.get('improvements')

    if not original or not improvements:
        return jsonify({"error": "Missing original prompt or improvements"}), 400

    try:
        refined = generator.refine_prompt(original, improvements)
        return jsonify({
            "success": True,
            "prompt": refined
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/presets')
def get_presets():
    """Get preset combinations"""
    presets = [
        {
            "name": "Minimalist Modern",
            "theme": "minimalism",
            "style": "clean, modern, simple",
            "niche": "young professionals"
        },
        {
            "name": "Vintage Retro",
            "theme": "vintage",
            "style": "retro, 70s, nostalgic",
            "niche": "vintage enthusiasts"
        },
        {
            "name": "Nature & Wildlife",
            "theme": "nature",
            "style": "realistic, detailed, majestic",
            "niche": "nature lovers"
        },
        {
            "name": "Abstract Art",
            "theme": "abstract",
            "style": "bold, colorful, artistic",
            "niche": "art enthusiasts"
        },
        {
            "name": "Cyberpunk Futuristic",
            "theme": "cyberpunk",
            "style": "neon, futuristic, tech",
            "niche": "tech enthusiasts"
        },
        {
            "name": "Motivational Quotes",
            "theme": "typography",
            "style": "inspirational, modern typography",
            "niche": "self-improvement seekers"
        }
    ]
    return jsonify(presets)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "generator": generator is not None,
        "model": config.CLAUDE_MODEL if generator else None
    })

if __name__ == "__main__":
    print(f"🎨 AI Auto-Prompter starting...")
    print(f"🤖 Claude Model: {config.CLAUDE_MODEL}")
    print(f"💾 Output directory: {config.OUTPUT_DIR}")
    print(f"🔌 Generator: {'enabled' if generator else 'disabled'}")
    print(f"🌐 Listening on {config.FLASK_HOST}:{config.FLASK_PORT}")

    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )

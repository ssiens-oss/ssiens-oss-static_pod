# Claude + ComfyUI Auto Asset System

**Automated digital asset creation, marketing, and marketplace publishing powered by AI**

---

## 🎯 Overview

This system automates the entire digital asset pipeline from generation to sale:

1. **Generate** assets using ComfyUI on RunPod
2. **Create** SEO-optimized listings with Claude AI
3. **Upload** to Gumroad and Itch.io automatically
4. **Market** with AI-generated TikTok content
5. **Track** performance in Notion dashboards
6. **Analyze** and optimize with AI-powered kill list logic

Perfect for:
- Digital asset creators and sellers
- Game developers selling asset packs
- Content creators monetizing designs
- Entrepreneurs building passive income streams

---

## 📦 Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **asset_runner.py** | Generate assets via ComfyUI | RunPod integration, batch processing, auto-archiving |
| **listing_generator.py** | Create marketing copy | SEO titles, descriptions, tags, pricing suggestions |
| **marketplace_uploader.py** | Upload to marketplaces | Gumroad & Itch.io support, automated publishing |
| **tiktok_generator.py** | Generate social content | Video scripts, captions, comment replies, viral analysis |
| **kill_list_analyzer.py** | Product lifecycle mgmt | AI scoring, keep/optimize/kill recommendations |
| **notion_sync.py** | Dashboard integration | Pipeline tracking, performance metrics, sync |

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+**
2. **API Keys:**
   - [Anthropic Claude API](https://console.anthropic.com/)
   - [RunPod Account](https://www.runpod.io/) with ComfyUI pod
   - [Gumroad Access Token](https://app.gumroad.com/settings/advanced)
   - [Itch.io API Key](https://itch.io/user/settings/api-keys)
   - [Notion Integration](https://www.notion.so/my-integrations) (optional)

### Installation

```bash
# 1. Navigate to automation directory
cd automation

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment template
cp .env.example .env

# 4. Edit .env with your API keys
nano .env  # or use your preferred editor
```

### Configuration

Edit `.env` file:

```env
# Required
RUNPOD_API_KEY=rp_xxxxxxxxxxxxx
RUNPOD_POD_ID=xxxxxxxxxxxxx
RUNPOD_POD_IP=123.45.67.89
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# For marketplace uploads
GUMROAD_ACCESS_TOKEN=xxxxxxxxxxxxx
ITCHIO_API_KEY=xxxxxxxxxxxxx

# For dashboard tracking (optional)
NOTION_API_KEY=secret_xxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxx
```

---

## 💡 Usage Examples

### 1. Generate Assets

```bash
python asset_runner.py
```

This will:
- Start your RunPod pod
- Generate assets from prompts via ComfyUI
- Create a ZIP archive
- Generate metadata JSON
- Stop the pod (saves costs)

**Customize prompts:**
```python
from asset_runner import AssetRunner

runner = AssetRunner()
archive = runner.run(
    prompts=[
        "fantasy potion icons, vibrant colors, game UI style",
        "sci-fi HUD icons, neon glow, futuristic design",
        "magic spellbook icons, mystical symbols"
    ],
    archive_name="fantasy_ui_pack.zip"
)
```

### 2. Generate Listings

```bash
python listing_generator.py
```

Or use a template:

```python
from listing_generator import ListingGenerator
from pathlib import Path

generator = ListingGenerator()
listing = generator.generate_from_template(
    Path("templates/listing_gen_template.json")
)

# listing contains:
# - seo_title
# - short_description
# - long_description
# - tags
# - hashtags
# - pricing_suggestion
# - marketing_angles
```

### 3. Upload to Marketplaces

```bash
python marketplace_uploader.py
```

**Programmatic upload:**
```python
from marketplace_uploader import MarketplaceUploader
from pathlib import Path

uploader = MarketplaceUploader()
results = uploader.upload_to_all(
    title="Fantasy Potion Icons – Hand-Painted RPG UI Pack",
    short_description="32 vibrant potion icons for RPG games",
    long_description="Full description here...",
    file_path=Path("./archives/fantasy_potions.zip"),
    price_usd=4.99,
    tags=["gamedev", "icons", "rpg", "ui"],
    marketplaces=["gumroad", "itchio"]
)
```

### 4. Generate TikTok Content

```bash
python tiktok_generator.py
```

**Create video script:**
```python
from tiktok_generator import TikTokGenerator

generator = TikTokGenerator()

# Generate video script
script = generator.generate_video_script(
    asset_name="Fantasy Potion Icons Pack",
    theme="Hand-Painted RPG UI",
    key_features=["32 unique icons", "Vibrant colors", "Game-ready"],
    video_length=30
)

# Analyze viral potential
analysis = generator.analyze_viral_potential(script)
print(f"Viral probability: {analysis['viral_probability']}")

# Generate comment replies
replies = generator.generate_comment_replies("Fantasy Potion Icons Pack")
```

### 5. Analyze Performance (Kill List)

```bash
python kill_list_analyzer.py
```

**Analyze your portfolio:**
```python
from kill_list_analyzer import KillListAnalyzer

analyzer = KillListAnalyzer()

assets = [
    {
        "name": "Fantasy Potion Icons",
        "description": "32 hand-painted RPG icons",
        "revenue": 245.50,
        "revenue_last_30d": 78.00,
        "views": 3420,
        "downloads": 127,
        "age_days": 45,
        "production_cost": 20.00
    },
    # ... more assets
]

analysis = analyzer.analyze_portfolio(assets)

# Get recommendations
keep_list = analysis["keep"]
optimize_list = analysis["optimize"]
kill_list = analysis["kill"]

# Generate report
report = analyzer.generate_kill_list_report(analysis)
print(report)
```

### 6. Sync to Notion

```bash
python notion_sync.py
```

**Track pipeline:**
```python
from notion_sync import PipelineTracker

tracker = PipelineTracker()

# Track generation
tracker.track_generation(
    theme="Fantasy Potion Icons",
    asset_type="Icon Pack",
    prompts=["fantasy potion icons"],
    archive_path="./archives/fantasy_potions.zip"
)

# Update performance
tracker.track_performance(
    asset_name="Fantasy Potion Icons",
    revenue=145.50,
    views=2340,
    downloads=87,
    tiktok_views=1200
)
```

---

## 🔄 Complete Pipeline

**End-to-end workflow:**

```bash
# 1. Generate assets
python asset_runner.py

# 2. Create listing
python listing_generator.py

# 3. Upload to marketplaces
python marketplace_uploader.py

# 4. Generate TikTok content
python tiktok_generator.py

# 5. Track in Notion
python notion_sync.py

# 6. Later: Analyze performance
python kill_list_analyzer.py
```

Or create a master script:

```python
from asset_runner import AssetRunner
from listing_generator import ListingGenerator
from marketplace_uploader import MarketplaceUploader
from tiktok_generator import TikTokGenerator
from notion_sync import PipelineTracker

def create_and_publish_asset(theme, prompts, price_usd):
    """Complete pipeline: generate → list → upload → market → track"""

    # 1. Generate
    runner = AssetRunner()
    archive = runner.run(prompts, f"{theme.lower().replace(' ', '_')}.zip")

    # 2. Create listing
    generator = ListingGenerator()
    listing = generator.generate_listing(
        asset_type="Icon Pack",
        theme=theme,
        style="Hand-Painted",
        usage="Game Development",
        prompts=prompts
    )

    # 3. Upload
    uploader = MarketplaceUploader()
    results = uploader.upload_to_all(
        title=listing["seo_title"],
        short_description=listing["short_description"],
        long_description=listing["long_description"],
        file_path=archive,
        price_usd=price_usd,
        tags=listing["tags"]
    )

    # 4. Generate TikTok content
    tiktok = TikTokGenerator()
    script = tiktok.generate_video_script(theme, theme, listing["tags"][:3])

    # 5. Track in Notion
    tracker = PipelineTracker()
    tracker.track_generation(theme, "Icon Pack", prompts, str(archive))

    return {
        "archive": archive,
        "listing": listing,
        "upload_results": results,
        "tiktok_script": script
    }

# Use it
result = create_and_publish_asset(
    theme="Fantasy Potion Icons",
    prompts=["fantasy potion icons, vibrant, RPG UI"],
    price_usd=4.99
)
```

---

## 📊 Notion Dashboard Setup

### Database Structure

Create a Notion database with these properties:

| Property | Type | Description |
|----------|------|-------------|
| **Name** | Title | Asset name |
| **Asset Type** | Select | Icon Pack, UI Kit, VFX Pack, etc. |
| **Status** | Select | Generated, Listed, Published, Keep, Optimize, Kill |
| **Revenue** | Number | Total revenue (USD) |
| **Views** | Number | Total marketplace views |
| **Downloads** | Number | Total downloads |
| **TikTok Views** | Number | TikTok video views |
| **Claude Score** | Number | AI quality score (0-10) |
| **Marketplace** | Select | Gumroad, Itch.io, etc. |
| **Created** | Date | Creation date |
| **Last Updated** | Date | Last metrics update |
| **SEO Title** | Text | Generated SEO title |
| **Tags** | Multi-select | Asset tags |
| **Archive Path** | Text | File path |

### Get Database ID

1. Open your Notion database
2. Click "..." → "Copy link"
3. Extract ID from URL: `https://notion.so/xxxxxxxxxxxxx?v=...`
4. The `xxxxxxxxxxxxx` is your `NOTION_DATABASE_ID`

### Get API Key

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it "Asset Pipeline"
4. Copy the "Internal Integration Token"
5. Share your database with the integration

---

## 🎨 Templates

### Listing Template

`templates/listing_gen_template.json`:
```json
{
  "asset_type": "2D Icon Pack",
  "theme": "Fantasy Potions",
  "style": "Hand-Painted, Vibrant",
  "usage": "RPG UI, Game Development",
  "prompts": [
    "fantasy potion icons, vibrant colors",
    "magical elixirs, glowing effects"
  ],
  "additional_context": "32 unique icons, PNG, 512x512px"
}
```

### TikTok Template

`templates/tiktok_template.json`:
```json
{
  "asset_name": "Fantasy Potion Icons Pack",
  "theme": "Hand-Painted RPG UI",
  "key_features": [
    "32 unique icons",
    "Vibrant colors",
    "Game-ready"
  ],
  "target_audience": "indie game developers",
  "video_length": 30
}
```

---

## ⚙️ Configuration Reference

### RunPod Setup

1. Create ComfyUI pod on RunPod
2. Note the Pod ID and IP address
3. Ensure ComfyUI is running on port 8188
4. Configure API key in `.env`

### Gumroad Setup

1. Go to https://app.gumroad.com/settings/advanced
2. Create an application
3. Copy the access token
4. Add to `.env`

### Itch.io Setup

1. Go to https://itch.io/user/settings/api-keys
2. Generate new API key
3. Add to `.env`
4. **Optional:** Install [Butler CLI](https://itch.io/docs/butler/installing.html) for file uploads

---

## 📈 Performance Metrics

The kill list analyzer evaluates assets on:

### Key Metrics

- **ROI**: Return on investment percentage
- **Conversion Rate**: View-to-download ratio
- **Revenue per View**: Average revenue per view
- **Daily Revenue**: Average daily earnings
- **Trend**: Growth trajectory (strong_growth, steady, declining, dead)

### Recommendations

- **Keep**: High-performing assets worth maintaining
- **Optimize**: Underperforming assets with potential
- **Kill**: Failing assets to discontinue

### Scoring

Claude analyzes each asset and provides:
- Overall score (0-10)
- Recommendation with confidence level
- Specific action items for optimization
- Predicted 6-month revenue

---

## 🛠️ Troubleshooting

### RunPod Connection Issues

```python
# Test pod connection
from asset_runner import RunPodManager

manager = RunPodManager()
status = manager.get_pod_status()
print(status)
```

### Gumroad Upload Fails

- Verify access token is valid
- Check file size (max 2GB)
- Ensure product name is unique

### Itch.io Uploads

- Install Butler CLI for file uploads
- Authenticate: `butler login`
- Test: `butler push file.zip user/game:channel`

### Claude API Errors

- Verify API key
- Check rate limits
- Ensure sufficient credits

### Notion Sync Issues

- Verify integration has database access
- Check property names match exactly
- Ensure database ID is correct

---

## 💰 Cost Optimization

### RunPod

- Auto-stop pods after generation (saves $$$)
- Use CPU pods for ComfyUI (cheaper than GPU for simple assets)
- Batch multiple prompts in single session

### Claude API

- Use caching for repeated requests
- Lower temperature for analytical tasks (kill list)
- Higher temperature for creative tasks (TikTok)

### Marketplaces

- Free tiers: Itch.io (no fees for free assets)
- Gumroad: 10% fee on sales
- Consider pricing strategy based on Claude recommendations

---

## 🔐 Security

- **Never commit `.env` file** (use `.env.example`)
- Store API keys in environment variables
- Rotate keys periodically
- Use Notion integrations (not personal tokens)
- Limit RunPod API key permissions

---

## 📚 Advanced Usage

### Custom ComfyUI Workflows

Modify `asset_runner.py` to use custom ComfyUI workflows:

```python
def generate_with_workflow(self, workflow_json, params):
    payload = {
        "workflow": workflow_json,
        "params": params
    }
    response = requests.post(f"{self.base_url}/workflow", json=payload)
    return response.json()
```

### A/B Testing Listings

Generate multiple listings and test:

```python
listings = []
for i in range(3):
    listing = generator.generate_listing(...)
    listings.append(listing)

# Manually review and choose best
```

### Automated Performance Tracking

Set up a cron job:

```bash
# Update metrics daily
0 0 * * * cd /path/to/automation && python -c "
from kill_list_analyzer import KillListAnalyzer
from notion_sync import NotionDashboard

# Fetch from Notion
dashboard = NotionDashboard()
assets = dashboard.get_all_assets()

# Analyze
analyzer = KillListAnalyzer()
analysis = analyzer.analyze_portfolio(assets)

# Sync back to Notion
dashboard.sync_kill_list_analysis(analysis)
"
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional marketplace integrations (ArtStation, Creative Market)
- [ ] Instagram/Twitter content generation
- [ ] Automated A/B testing
- [ ] Revenue forecasting models
- [ ] Batch template processing
- [ ] Web dashboard UI
- [ ] Webhook notifications

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Credits

Built with:
- [Anthropic Claude API](https://www.anthropic.com/)
- [RunPod](https://www.runpod.io/)
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [Notion API](https://developers.notion.com/)
- [Gumroad API](https://gumroad.com/api)
- [Itch.io Butler](https://itch.io/docs/butler/)

---

## 📞 Support

- **Documentation**: This README
- **Issues**: GitHub Issues
- **API Docs**: [Anthropic Docs](https://docs.anthropic.com/)

---

**Happy automating! 🚀**

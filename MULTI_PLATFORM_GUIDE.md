# Multi-Platform Publishing Guide

## Overview

The POD Gateway now supports publishing to multiple print-on-demand platforms! Choose from:

- **Printify** - Fully automated API integration
- **Zazzle** - API integration with OAuth
- **Redbubble** - Manual workflow (no public API)

## Features

### POD-Optimized Prompts

The gateway automatically enhances your prompts for print-on-demand:

**Quality Enhancements:**
- High contrast for product visibility
- Bold, vibrant colors
- Centered composition
- Clean backgrounds
- Sharp details
- Eye-catching designs

**Negative Prompts Avoid:**
- Blurry or muddy colors
- Low contrast
- Small details that won't print well
- Text and watermarks
- Cluttered backgrounds

### Platform Selection

When you click "Publish" on an approved image:

1. Enter product title
2. **Select platform** (if multiple configured)
3. Platform-specific publish workflow

## Platform Configuration

### Printify (Automated)

**Full API integration** - Uploads images and creates products automatically.

**Setup in `.env`:**
```bash
PRINTIFY_API_KEY=your_printify_api_key
PRINTIFY_SHOP_ID=your_shop_id
PRINTIFY_BLUEPRINT_ID=77    # Product type (77 = Gildan Hoodie)
PRINTIFY_PROVIDER_ID=99     # Print provider (99 = Printify Choice)
```

**Features:**
- ✅ Automatic image upload
- ✅ Product creation
- ✅ Variant management (auto-limited to 100 max)
- ✅ Price control
- ✅ Direct product links

**Limitations:**
- Max 100 variants per product (Printify limit)
- Requires valid API key and shop

---

### Zazzle (API Integration)

**OAuth-based API** - Uploads and creates products via Zazzle API.

**Setup in `.env`:**
```bash
ZAZZLE_API_KEY=your_zazzle_api_key
ZAZZLE_API_SECRET=your_zazzle_api_secret
ZAZZLE_STORE_ID=your_store_id
ZAZZLE_PRODUCT_TYPE=tshirt  # Optional: tshirt, hoodie, poster, etc.
```

**Features:**
- ✅ Base64 image upload
- ✅ Product creation with departments
- ✅ Tag support
- ✅ Royalty percentage pricing

**Image Requirements:**
- Min resolution: 1800x1800px
- Max file size: 100MB
- Formats: PNG, JPEG

**Note:** Zazzle requires OAuth authentication. Get API credentials at https://www.zazzle.com/sell/developers

---

### Redbubble (Manual Workflow)

**No public API** - Manual upload workflow with guidance.

**Setup in `.env`:**
```bash
REDBUBBLE_USERNAME=your_username
```

**Features:**
- ✅ Image saved locally for upload
- ✅ Upload instructions in logs
- ✅ Direct link to upload page

**Image Requirements:**
- Min resolution: 2400px on shortest side
- Max file size: 100MB
- Formats: PNG, JPEG, GIF

**Workflow:**
1. Click "Publish" and select "Redbubble"
2. Check terminal logs for image path and upload URL
3. Manually upload at: https://www.redbubble.com/portfolio/images/new

---

## Usage

### Generate AI Design

1. Click "Generate AI Design"
2. Enter your prompt (e.g., "cyberpunk cat neon lights")
3. Gateway automatically enhances for POD quality
4. Wait for image download

### Approve Image

1. Review generated image in gallery
2. Click "✓ Approve"
3. Image status changes to "approved"

### Publish to Platform

1. Click "→ Publish" on approved image
2. Enter product title
3. **Select platform** (if multiple configured):
   ```
   Select publishing platform:

   1. Printify
   2. Zazzle
   3. Redbubble

   Enter number (default: 1): 2
   ```
4. Wait for upload (or follow manual instructions)
5. See success toast: "Published to Zazzle!"

### Platform-Specific Product URLs

After publishing, the gateway saves the product URL:

- **Printify:** `https://printify.com/app/products/{product_id}`
- **Zazzle:** `https://www.zazzle.com/pd/{product_id}`
- **Redbubble:** Manual upload page (https://www.redbubble.com/portfolio/images/new)

---

## API Endpoints

### Get Available Platforms

```bash
GET /api/platforms
```

**Response:**
```json
{
  "success": true,
  "platforms": [
    {
      "name": "printify",
      "display_name": "Printify",
      "configured": true
    },
    {
      "name": "zazzle",
      "display_name": "Zazzle",
      "configured": true
    },
    {
      "name": "redbubble",
      "display_name": "Redbubble",
      "configured": true
    }
  ]
}
```

### Publish to Platform

```bash
POST /api/publish/<image_id>
Content-Type: application/json

{
  "platform": "printify|zazzle|redbubble",
  "title": "Product Title",
  "description": "Optional description",
  "price_cents": 1999
}
```

**Response:**
```json
{
  "success": true,
  "product_id": "12345",
  "product_url": "https://printify.com/app/products/12345",
  "platform": "Printify",
  "status": "published"
}
```

---

## Architecture

### Platform System Design

The gateway uses a **strategy pattern** for platform abstraction:

```
BasePlatform (abstract)
├── PrintifyPlatform
├── ZazzlePlatform
└── RedbubblePlatform
```

**Base Interface:**
- `publish()` - Publish image to platform
- `is_configured()` - Check if platform is set up
- `get_product_url()` - Get product URL
- `validate_image()` - Check image requirements

**Factory Pattern:**
```python
platforms = {
    "printify": PrintifyPlatform(config),
    "zazzle": ZazzlePlatform(config),
    "redbubble": RedbubblePlatform(config)
}

# Select and publish
platform = platforms[selected_platform]
result = platform.publish(image_path, title, description, price)
```

### Files Structure

```
gateway/app/platforms/
├── __init__.py           # Package exports
├── base.py               # BasePlatform abstract class
├── printify.py           # Printify adapter
├── zazzle.py             # Zazzle integration
└── redbubble.py          # Redbubble manual workflow
```

---

## Adding New Platforms

### 1. Create Platform Class

Create `gateway/app/platforms/yourplatform.py`:

```python
from .base import BasePlatform, PublishResult
import logging

logger = logging.getLogger(__name__)


class YourPlatformPlatform(BasePlatform):
    """Your platform POD integration"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')

    def is_configured(self) -> bool:
        """Check if configured"""
        return bool(self.api_key)

    def publish(self, image_path: str, title: str,
                description: Optional[str] = None,
                tags: Optional[list] = None,
                price: Optional[int] = None,
                **kwargs) -> PublishResult:
        """Publish to platform"""
        try:
            # Your upload logic here
            product_id = self._upload_and_create(image_path, title)

            if product_id:
                return PublishResult(
                    success=True,
                    product_id=product_id,
                    product_url=self.get_product_url(product_id),
                    platform="YourPlatform"
                )
            else:
                return PublishResult(
                    success=False,
                    error="Upload failed",
                    platform="YourPlatform"
                )
        except Exception as e:
            logger.error(f"YourPlatform error: {e}")
            return PublishResult(
                success=False,
                error=str(e),
                platform="YourPlatform"
            )

    def get_product_url(self, product_id: str) -> str:
        """Get product URL"""
        return f"https://yourplatform.com/products/{product_id}"

    def validate_image(self, image_path: str) -> tuple[bool, str]:
        """Validate image requirements"""
        # Add platform-specific validation
        return True, ""
```

### 2. Register Platform

Update `gateway/app/platforms/__init__.py`:

```python
from .yourplatform import YourPlatformPlatform

__all__ = [
    'BasePlatform',
    'PlatformError',
    'PublishResult',
    'PrintifyPlatform',
    'ZazzlePlatform',
    'RedbubblePlatform',
    'YourPlatformPlatform',  # Add here
]
```

### 3. Initialize in main.py

Update `gateway/app/main.py`:

```python
# Import platform
from app.platforms import YourPlatformPlatform

# Initialize platform
yourplatform_api_key = os.getenv('YOURPLATFORM_API_KEY')
if yourplatform_api_key:
    try:
        yourplatform_config = {
            'api_key': yourplatform_api_key,
            # Add other config...
        }
        platforms['yourplatform'] = YourPlatformPlatform(yourplatform_config)
        logger.info("✓ YourPlatform initialized")
    except Exception as e:
        logger.error(f"✗ YourPlatform failed: {e}")
```

### 4. Add Environment Variables

Add to `.env`:

```bash
YOURPLATFORM_API_KEY=your_api_key
```

### 5. Test

```bash
# Restart gateway
pkill -f "python.*main.py"
cd ~/ssiens-oss-static_pod/gateway
export PYTHONPATH=$(pwd)
.venv/bin/python app/main.py

# Should see:
# ✓ YourPlatform initialized
# 📦 Configured platforms: printify, zazzle, redbubble, yourplatform
```

---

## Troubleshooting

### Platform Not Showing

**Issue:** Platform doesn't appear in selection list

**Solutions:**
1. Check `.env` has required credentials
2. Restart gateway after updating `.env`
3. Check terminal for "✓ Platform initialized" message
4. Check browser console for platform load errors

### Publish Fails

**Issue:** "Platform not configured" error

**Solutions:**
1. Verify all required environment variables are set
2. Check `is_configured()` returns `true`
3. Review platform-specific requirements

### Image Validation Errors

**Issue:** "Image resolution too low" or "File size too large"

**Platform Requirements:**

| Platform | Min Resolution | Max Size | Formats |
|----------|----------------|----------|---------|
| Printify | 1024x1024 | 50MB | PNG, JPEG |
| Zazzle | 1800x1800 | 100MB | PNG, JPEG |
| Redbubble | 2400px (shortest) | 100MB | PNG, JPEG, GIF |

**Solutions:**
1. Regenerate with higher resolution
2. Use image editing tool to resize/compress
3. Check prompt uses "high quality" keywords

---

## Best Practices

### 1. POD-Optimized Prompts

**Good Prompts:**
- "Bold geometric pattern, high contrast, vibrant colors, centered design"
- "Minimalist logo design, clean background, sharp lines, professional"
- "Retro sunset landscape, vivid colors, bold composition"

**Avoid:**
- Small text or fine details
- Low contrast designs
- Complex patterns with tiny elements
- Realistic photos (may have licensing issues)

### 2. Platform Selection

**Printify:** Best for automated bulk publishing
- Fast API integration
- Good for testing designs quickly
- Limited to their product catalog

**Zazzle:** Best for custom products
- Wide product variety
- Higher royalty potential
- More manual product customization

**Redbubble:** Best for artistic designs
- Large artist community
- Good organic traffic
- Manual upload = more control

### 3. Pricing Strategy

Different platforms use different pricing models:

**Printify:** Fixed price per product
- Set `price_cents` in API call
- Example: `"price_cents": 2499` ($24.99)

**Zazzle:** Royalty percentage
- Gateway converts price to % royalty
- Max 99% royalty

**Redbubble:** Artist margin
- Set markup % on Redbubble website
- Not controlled via API

---

## Next Steps

1. ✅ Configure your preferred platforms in `.env`
2. ✅ Restart the gateway
3. ✅ Generate test designs
4. ✅ Publish to each platform
5. ✅ Verify products appear in your stores
6. ✅ Connect platforms to sales channels (Etsy, Shopify, etc.)

---

## Support

### Platform Documentation

- **Printify API:** https://developers.printify.com/
- **Zazzle API:** https://www.zazzle.com/sell/developers
- **Redbubble:** https://help.redbubble.com/hc/en-us/articles/201579195

### Gateway Issues

For gateway bugs or feature requests:
https://github.com/anthropics/claude-code/issues

---

**Status:** ✅ MULTI-PLATFORM PUBLISHING READY
**Date:** 2026-01-18
**Version:** 2.0.0

Enjoy automated publishing to multiple POD platforms! 🚀

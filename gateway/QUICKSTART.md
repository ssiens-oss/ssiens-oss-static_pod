# POD Gateway Quick Start

The POD Gateway service is now ready to run!

## ✅ What Was Fixed

1. **Virtual Environment**: Gateway now automatically creates and uses `.venv`
2. **Python Dependencies**: Installs Flask, requests, Pillow in isolated venv
3. **Port Configuration**: Using port 8099 (5000 was in use)
4. **Config Validation**: Commented out invalid Printify Shop ID placeholder

## 🚀 Starting the Gateway

```bash
cd gateway
./start.sh
```

The gateway will:
- ✅ Create virtual environment (first run only)
- ✅ Install dependencies automatically
- ✅ Load configuration from `../.env`
- ✅ Start Flask server on port 8099

**Access**: http://localhost:8099

## 📊 Gateway Status

```
✅ Flask Server: Running on 0.0.0.0:8099
✅ Image Directory: /workspace/comfyui/output
✅ State File: /workspace/gateway/state.json
⚠️  Printify: Not configured (add API key + Shop ID)
✅ Shopify: Configured
✅ ComfyUI API: http://localhost:8188
```

## 📋 Configuration

The gateway loads from `.env` in the project root:

### Required for Full Functionality

```bash
# Printify (for product creation)
PRINTIFY_API_KEY=your_api_key_here
PRINTIFY_SHOP_ID=12345678  # Must be numeric

# ComfyUI (for image generation)
COMFYUI_API_URL=http://localhost:8188
# OR for RunPod:
RUNPOD_API_KEY=rpa_xxx...
RUNPOD_ENDPOINT_ID=xxxxxxxxx
```

### Optional

```bash
# Flask Server
FLASK_PORT=8099  # Default: 5000
FLASK_DEBUG=false

# Shopify
SHOPIFY_STORE_URL=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxx

# Product Settings
PRINTIFY_BLUEPRINT_ID=77  # Hoodie
PRINTIFY_PROVIDER_ID=39   # SwiftPOD
PRINTIFY_DEFAULT_PRICE_CENTS=3499  # $34.99
```

## 🌐 API Endpoints

Once running, access:

- **Health Check**: http://localhost:8099/health
- **Gallery**: http://localhost:8099/
- **Approve Image**: http://localhost:8099/approve/<image_id>
- **Delete Image**: http://localhost:8099/delete/<image_id>
- **Stats**: http://localhost:8099/stats

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Change port in .env
echo "FLASK_PORT=8099" >> ../.env

# Or kill existing process
lsof -ti:5000 | xargs kill -9
```

### Virtual Environment Issues

```bash
# Recreate venv
rm -rf .venv
./start.sh  # Will recreate automatically
```

### Missing Dependencies

```bash
# Activate venv and install manually
source .venv/bin/activate
pip install flask requests pillow python-dotenv
```

### Printify Not Working

```bash
# Add valid credentials to .env
PRINTIFY_API_KEY=your_api_key
PRINTIFY_SHOP_ID=12345678  # Numeric only!
```

## 📖 Workflow

1. **Generate Images**: Use ComfyUI or RunPod Serverless
2. **Review in Gateway**: http://localhost:8099
3. **Approve Images**: Click approve on images you like
4. **Auto-Publish**: Gateway creates Printify products automatically
5. **Sync to Shopify**: Products sync to your store

## 🎯 Next Steps

### For Development

```bash
cd gateway
./start.sh
# Gateway runs on http://localhost:8099
```

### For Production

```bash
# Use gunicorn or uwsgi
cd gateway
source .venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:8099 app.main:app
```

### With Docker

```bash
cd gateway
docker-compose up
# Runs gateway + ComfyUI + dependencies
```

## 🔗 Integration

The gateway integrates with:

- ✅ **ComfyUI** (local or RunPod)
- ✅ **Printify** (product creation)
- ✅ **Shopify** (store sync)
- ⚠️  **TikTok, Etsy, Instagram** (requires API keys)

---

## ✨ Summary

**Gateway is ready!** It will:
1. Monitor for new generated images
2. Show them in a web gallery
3. Let you approve/reject
4. Auto-create products on Printify
5. Sync to Shopify

Just add your Printify API key and start generating! 🚀

# Container Environment Setup

## Current Situation

Your container environment at `/workspace/pod` needs to pull the latest code from the `claude/inject-http-adapter-Aiv7c` branch.

The following features have been added:
- ✅ HTTPAdapter with retry logic for Printify API
- ✅ Gildan 18500 Hoodie as default template (Blueprint 165)
- ✅ Blueprint search utility
- ✅ Template switcher script
- ✅ Comprehensive documentation

## Quick Sync (Inside Container)

If you're inside the container at `/workspace/pod`, run:

```bash
cd /workspace/pod

# Fetch latest changes
git fetch origin claude/inject-http-adapter-Aiv7c

# Switch to the branch
git checkout claude/inject-http-adapter-Aiv7c

# Pull latest code
git pull origin claude/inject-http-adapter-Aiv7c

# Verify new files
ls -l scripts/find_printify_blueprint.py
ls -l docs/PRINTIFY_BLUEPRINTS.md
```

## Starting the Gateway (Inside Container)

The correct way to start Flask in the container:

```bash
cd /workspace/pod/gateway

# Set Python path and run Flask
PYTHONPATH=/workspace/pod/gateway python -m flask run --host=0.0.0.0 --port=5000
```

Or if you prefer using the app module directly:

```bash
cd /workspace/pod/gateway
PYTHONPATH=. flask run --host=0.0.0.0 --port=5000
```

Or run the Python file directly:

```bash
cd /workspace/pod/gateway
python app/main.py
```

## Testing the Blueprint Search

After syncing, test the new utility:

```bash
cd /workspace/pod

# Make sure PRINTIFY_API_KEY is set in your environment
export PRINTIFY_API_KEY="your-actual-api-key"
export PRINTIFY_SHOP_ID="your-shop-id"

# Search for Gildan 18500
python scripts/find_printify_blueprint.py --id 165 --providers
```

## Environment Variables

Make sure these are set in your container:

```bash
# Required
export PRINTIFY_API_KEY="your-actual-api-key"
export PRINTIFY_SHOP_ID="your-shop-id"

# Optional (these are now defaults)
export PRINTIFY_BLUEPRINT_ID=165       # Gildan 18500 Hoodie
export PRINTIFY_PROVIDER_ID=99         # SwiftPOD
export PRINTIFY_DEFAULT_PRICE_CENTS=3499  # $34.99
```

## If Git Pull Doesn't Work

If you can't pull in the container, manually copy files:

### Option 1: From Host to Container

```bash
# On your host machine (not in container)
docker cp /path/to/repo/scripts/find_printify_blueprint.py CONTAINER_ID:/workspace/pod/scripts/
docker cp /path/to/repo/scripts/set_product_template.sh CONTAINER_ID:/workspace/pod/scripts/
docker cp /path/to/repo/docs/PRINTIFY_BLUEPRINTS.md CONTAINER_ID:/workspace/pod/docs/
docker cp /path/to/repo/gateway/app/printify_client.py CONTAINER_ID:/workspace/pod/gateway/app/
docker cp /path/to/repo/gateway/app/config.py CONTAINER_ID:/workspace/pod/gateway/app/
docker cp /path/to/repo/.env CONTAINER_ID:/workspace/pod/.env
```

### Option 2: Rebuild Container

```bash
# From host, rebuild with latest code
docker build -t your-pod-gateway .
docker run -it your-pod-gateway
```

## Verifying the Setup

After syncing, verify everything is in place:

```bash
cd /workspace/pod

# Check files exist
ls -l scripts/find_printify_blueprint.py
ls -l scripts/set_product_template.sh
ls -l docs/PRINTIFY_BLUEPRINTS.md

# Check configuration
grep PRINTIFY_BLUEPRINT_ID .env
grep PRINTIFY_PROVIDER_ID .env

# Check Python can import modules
cd gateway
python -c "from app.printify_client import PrintifyClient; print('✅ Import successful')"
python -c "from app.config import config; print(f'✅ Blueprint: {config.printify.blueprint_id}')"
```

## Common Issues

### Issue: "Failed to find Flask application"

**Solution**: Set PYTHONPATH correctly

```bash
cd /workspace/pod/gateway
PYTHONPATH=/workspace/pod/gateway flask run --host=0.0.0.0 --port=5000
```

Or:

```bash
cd /workspace/pod/gateway
python app/main.py
```

### Issue: "Module not found"

**Solution**: Install dependencies

```bash
cd /workspace/pod
pip install -r requirements.txt
# or
pip install requests python-dotenv Flask Pillow
```

### Issue: Scripts not executable

**Solution**: Set permissions

```bash
chmod +x /workspace/pod/scripts/find_printify_blueprint.py
chmod +x /workspace/pod/scripts/set_product_template.sh
```

## Testing End-to-End

Once the gateway is running:

```bash
# 1. Check health endpoint
curl http://localhost:5000/health

# 2. List images
curl http://localhost:5000/api/images

# 3. Publish a test design (if you have an image)
curl -X POST http://localhost:5000/api/publish/your_image_id \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Gildan 18500 Hoodie", "price_cents": 3499}'
```

## What Changed

### New Default Template: Gildan 18500 Hoodie

Previously: Bella+Canvas 3001 T-Shirt (Blueprint 77, $19.99)
Now: Gildan 18500 Heavy Blend Hoodie (Blueprint 165, $34.99)

### New Files

- `scripts/find_printify_blueprint.py` - Search Printify catalog
- `scripts/set_product_template.sh` - Switch between templates
- `docs/PRINTIFY_BLUEPRINTS.md` - Blueprint reference guide
- Updated `gateway/app/printify_client.py` - Added HTTPAdapter with retry logic
- Updated `gateway/app/config.py` - New defaults for hoodie
- Updated `.env` and `.env.example` - Gildan 18500 configuration

## Next Steps

1. **Sync the code** (instructions above)
2. **Verify configuration** with the blueprint search tool
3. **Start the gateway** using the corrected Flask command
4. **Test with a design** to create a Gildan 18500 hoodie product

Need help? See `docs/PRINTIFY_BLUEPRINTS.md` for detailed blueprint information.

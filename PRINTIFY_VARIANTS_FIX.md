# Printify Blueprint Variants Fix

## Issue
Getting "Failed to fetch blueprint variants: Not Found" errors when trying to create Printify products.

## Root Cause
Printify's API requires specific **blueprint + provider** combinations. Not all providers support all blueprints, and using an invalid combination results in a 404 error.

## Solution
Based on testing with your Printify account (Store ID: 25860767), the following configuration works:

### Working Configuration
```env
PRINTIFY_TEE_BLUEPRINT_ID=12
PRINTIFY_TEE_PROVIDER_ID=50

PRINTIFY_HOODIE_BLUEPRINT_ID=77
PRINTIFY_HOODIE_PROVIDER_ID=50
```

**Provider 50 = Underground Threads** (supports both tee and hoodie blueprints)

## How to Apply on RunPod

### Quick Fix (One Command)
```bash
cat >> /workspace/app/.env <<'EOF'
PRINTIFY_TEE_BLUEPRINT_ID=12
PRINTIFY_TEE_PROVIDER_ID=50
PRINTIFY_HOODIE_BLUEPRINT_ID=77
PRINTIFY_HOODIE_PROVIDER_ID=50
EOF

./restart-services.sh
```

### Test After Restart
```bash
curl -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Bold streetwear graphic",
    "productTypes": ["tee","hoodie"],
    "autoPublish": true
  }'
```

Watch logs:
```bash
tail -f /workspace/logs/pod-engine.log
```

### Expected Success Output
```
[INFO] Creating Printify product for tee
[SUCCESS] ✓ Created Printify product
[INFO] Publishing product to Shopify via Printify
[SUCCESS] ✓ Published to Shopify

[INFO] Creating Printify product for hoodie
[SUCCESS] ✓ Created Printify product
[SUCCESS] ✓ Published to Shopify

[SUCCESS] ✅ Pipeline complete! Created 2 products
```

## How Provider IDs Were Discovered

The correct provider IDs were found by querying Printify's API:

```bash
# Test all providers for a blueprint to find which return HTTP 200
for provider_id in $(curl -s \
  https://api.printify.com/v1/catalog/blueprints/77/print_providers.json \
  -H "Authorization: Bearer $PRINTIFY_API_KEY" | \
  grep -oP '"id":\K\d+'); do

  status=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://api.printify.com/v1/catalog/blueprints/77/print_providers/$provider_id/variants.json" \
    -H "Authorization: Bearer $PRINTIFY_API_KEY")

  if [ "$status" = "200" ]; then
    echo "✅ Provider $provider_id works with blueprint 77"
  fi
done
```

## Alternative Providers (If Provider 50 Unavailable)

If provider 50 stops working or is unavailable in your region, you can test alternatives:

### For TEE (Blueprint 12)
Test with this command on your RunPod instance:
```bash
PRINTIFY_KEY=$(grep '^PRINTIFY_API_KEY=' /workspace/app/.env | cut -d= -f2-)

node <<EOF
const key = "${PRINTIFY_KEY}";
(async () => {
  const bp = 12;
  const headers = { Authorization: "Bearer " + key };
  const res = await fetch(
    "https://api.printify.com/v1/catalog/blueprints/" + bp + "/print_providers.json",
    { headers }
  );
  const json = await res.json();

  for (const p of (json.data || [])) {
    const r = await fetch(
      "https://api.printify.com/v1/catalog/blueprints/" + bp +
      "/print_providers/" + p.id + "/variants.json",
      { headers }
    );
    if (r.status === 200) {
      console.log("TEE provider", p.id, p.title, "-> VALID");
    }
  }
})();
EOF
```

### For HOODIE (Blueprint 77)
```bash
PRINTIFY_KEY=$(grep '^PRINTIFY_API_KEY=' /workspace/app/.env | cut -d= -f2-)

node <<EOF
const key = "${PRINTIFY_KEY}";
(async () => {
  const bp = 77;
  const headers = { Authorization: "Bearer " + key };
  const res = await fetch(
    "https://api.printify.com/v1/catalog/blueprints/" + bp + "/print_providers.json",
    { headers }
  );
  const json = await res.json();

  for (const p of (json.data || [])) {
    const r = await fetch(
      "https://api.printify.com/v1/catalog/blueprints/" + bp +
      "/print_providers/" + p.id + "/variants.json",
      { headers }
    );
    if (r.status === 200) {
      console.log("HOODIE provider", p.id, p.title, "-> VALID");
    }
  }
})();
EOF
```

## Verification Checklist

After applying the fix:

- [ ] `.env` contains all four Printify blueprint/provider variables
- [ ] Services restarted successfully
- [ ] Test job submitted without errors
- [ ] Logs show "Created Printify product" (not "Failed to fetch blueprint variants")
- [ ] Products appear in Printify dashboard
- [ ] Products sync to Shopify within 1-2 minutes

## Related Documentation

- [RUNPOD_COMPLETE_WALKTHROUGH.md](RUNPOD_COMPLETE_WALKTHROUGH.md) - Complete RunPod setup guide
- [POD_ENGINE_API.md](POD_ENGINE_API.md) - API reference
- [.env.example](.env.example) - Complete environment configuration template

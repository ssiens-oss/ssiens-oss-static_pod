# Printify Blueprint Reference

Quick reference for common Printify blueprint IDs and their recommended providers.

## Common Blueprints

### Gildan 18500 - Heavy Blend™ Hooded Sweatshirt 🔥
- **Blueprint ID**: `77`
- **Type**: Hoodie
- **Brand**: Gildan
- **Model**: 18500
- **Description**: Heavy Blend™ Hooded Sweatshirt - Most popular POD hoodie
- **Recommended Providers**:
  - **39** - SwiftPOD (US, reliable, fast shipping) ⭐
  - **99** - Printify Choice (Multi-region, automatic routing)
  - **29** - Monster Digital (US, premium quality)

### Gildan 5000 - Heavy Cotton T-Shirt
- **Blueprint ID**: `3`
- **Type**: T-Shirt
- **Brand**: Gildan
- **Model**: 5000
- **Description**: Classic heavy cotton t-shirt
- **Recommended Providers**:
  - **99** - SwiftPOD
  - **5** - Printify Choice
  - **3** - District Photo

### Bella+Canvas 3001 - Unisex Jersey T-Shirt
- **Blueprint ID**: `6` or `77`
- **Type**: T-Shirt
- **Brand**: Bella+Canvas
- **Model**: 3001
- **Description**: Premium soft unisex t-shirt
- **Recommended Providers**:
  - **99** - SwiftPOD
  - **16** - SPOKE Custom Products

### Gildan 64000 - Softstyle T-Shirt
- **Blueprint ID**: `380`
- **Type**: T-Shirt
- **Brand**: Gildan
- **Model**: 64000
- **Description**: Softer than standard Gildan, popular for DTG printing
- **Recommended Providers**:
  - **99** - SwiftPOD
  - **5** - Printify Choice

### Gildan 18000 - Heavy Blend™ Crewneck Sweatshirt
- **Blueprint ID**: `164`
- **Type**: Sweatshirt
- **Brand**: Gildan
- **Model**: 18000
- **Description**: Heavy Blend™ Crewneck (no hood)
- **Recommended Providers**:
  - **99** - SwiftPOD
  - **5** - Printify Choice

## Print Providers

### Provider 39 - SwiftPOD ⭐ (Recommended)
- **Location**: United States
- **Strengths**: Fast turnaround, reliable, good quality, 2-5 day shipping
- **Best For**: US market, standard products, Gildan 18500
- **Shipping**: 2-5 business days (US)

### Provider 99 - Printify Choice
- **Location**: Multi-region (automatic routing)
- **Strengths**: Global reach, automatic optimization, wide product range
- **Best For**: International orders, cost optimization
- **Shipping**: Varies by destination

### Provider 29 - Monster Digital
- **Location**: United States
- **Strengths**: Premium quality, DTG expertise
- **Best For**: High-quality prints, premium products
- **Shipping**: 3-7 business days (US)

### Provider 3 - District Photo
- **Location**: United States
- **Strengths**: Wide product range
- **Best For**: Specialty items
- **Shipping**: 2-5 business days (US)

## Configuration Examples

### For Gildan 18500 Hoodie (Most Popular POD Product) 🔥

```bash
# .env configuration
PRINTIFY_BLUEPRINT_ID=77
PRINTIFY_PROVIDER_ID=39  # SwiftPOD
PRINTIFY_DEFAULT_PRICE_CENTS=3499  # $34.99 (typical hoodie price)
```

### For Bella+Canvas 3001 T-Shirt (Premium Quality)

```bash
# .env configuration
PRINTIFY_BLUEPRINT_ID=6  # or 77 depending on variant
PRINTIFY_PROVIDER_ID=39  # SwiftPOD
PRINTIFY_DEFAULT_PRICE_CENTS=1999  # $19.99
```

### For Gildan 5000 T-Shirt (Budget Friendly)

```bash
# .env configuration
PRINTIFY_BLUEPRINT_ID=3
PRINTIFY_PROVIDER_ID=99
PRINTIFY_DEFAULT_PRICE_CENTS=1599  # $15.99
```

## Finding Blueprint IDs

Use the included utility script to search for specific products:

```bash
# Search for Gildan 18500
python scripts/find_printify_blueprint.py --search "gildan 18500" --providers

# Search for any hoodie
python scripts/find_printify_blueprint.py --search "hoodie" --providers

# Get details for specific blueprint ID
python scripts/find_printify_blueprint.py --id 165 --providers

# List all blueprints (warning: long output!)
python scripts/find_printify_blueprint.py --all
```

## Variant Fetching

The POD Gateway automatically fetches available variants (sizes, colors) for any blueprint/provider combination. You don't need to manually specify variant IDs.

The `PrintifyClient` will:
1. Query the Printify API for available variants
2. Filter for enabled and available variants
3. Cache results for performance
4. Apply your design to all available variants

## Pricing Recommendations

Based on typical POD pricing and market rates:

| Product Type | Blueprint | Suggested Retail | Base Cost* | Profit Margin |
|-------------|-----------|------------------|------------|---------------|
| Gildan 18500 Hoodie | 165 | $34.99-$44.99 | ~$22-25 | $10-20 |
| Bella+Canvas 3001 Tee | 77 | $19.99-$24.99 | ~$12-14 | $6-11 |
| Gildan 5000 Tee | 3 | $15.99-$19.99 | ~$9-11 | $5-9 |
| Gildan 64000 Tee | 380 | $17.99-$22.99 | ~$10-12 | $6-11 |

*Base cost varies by provider, quantity, and printing location

## Testing Configuration

To test your blueprint/provider configuration:

```bash
# 1. Update .env with your desired blueprint and provider
# 2. Restart the gateway
cd gateway && flask run

# 3. Test with a sample image
curl -X POST http://localhost:5000/api/publish/test_image_id \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Design", "price_cents": 3499}'
```

## Notes

- Blueprint and provider IDs are maintained by Printify and may change
- Always verify availability in your specific Printify shop
- Some providers may not support all blueprints
- Variant availability varies by provider and location
- Use the search script to get real-time, accurate information

## Resources

- [Printify API Documentation](https://developers.printify.com/)
- [Printify Catalog](https://printify.com/app/catalog)
- [Provider Comparison](https://printify.com/print-providers/)

---

Last Updated: 2026-01-14

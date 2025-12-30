"""
Automated Product Import Workflow
AliExpress → Shopify → TikTok Shop pipeline
"""
import asyncio
from typing import List, Dict, Any
from loguru import logger
from celery_app import app
from services.aliexpress_service import AliExpressService
from services.shopify_service import ShopifyService
from services.tiktok_service import TikTokService


@app.task(bind=True, max_retries=3)
def import_product_by_id(self, product_id: str, markup_percentage: float = 40.0):
    """
    Import single product from AliExpress to Shopify and TikTok

    Args:
        product_id: AliExpress product ID
        markup_percentage: Price markup (default 40%)

    Returns:
        Dict with Shopify and TikTok product IDs
    """
    try:
        logger.info(f"Starting import for AliExpress product: {product_id}")

        result = asyncio.run(_import_product_async(product_id, markup_percentage))

        logger.info(
            f"✅ Successfully imported product {product_id}: "
            f"Shopify ID {result['shopify_id']}, TikTok ID {result.get('tiktok_id', 'pending')}"
        )

        return result

    except Exception as e:
        logger.error(f"Failed to import product {product_id}: {e}")

        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


async def _import_product_async(product_id: str, markup_percentage: float) -> Dict[str, Any]:
    """Async implementation of product import"""

    ali_service = AliExpressService()
    shopify_service = ShopifyService()
    tiktok_service = TikTokService()

    # 1. Fetch product details from AliExpress
    logger.info(f"Fetching product {product_id} from AliExpress")
    ali_product = await ali_service.get_product_details(product_id)

    if not ali_product:
        raise ValueError(f"Product {product_id} not found on AliExpress")

    # 2. Calculate pricing with markup
    base_price = float(ali_product.get("target_sale_price", 0))
    selling_price = round(base_price * (1 + markup_percentage / 100), 2)

    logger.info(f"Pricing: ${base_price} → ${selling_price} ({markup_percentage}% markup)")

    # 3. Prepare Shopify product data
    shopify_data = {
        "title": ali_product.get("product_title"),
        "description": ali_product.get("detail", ""),
        "vendor": "AliExpress",
        "product_type": ali_product.get("category_name", "General"),
        "price": selling_price,
        "stock": ali_product.get("volume", 100),  # Will be normalized
        "sku": f"ALI-{product_id}",
        "images": [img.get("url") for img in ali_product.get("images", [])[:5]],
    }

    # 4. Create product in Shopify (with inventory normalization)
    logger.info("Creating product in Shopify")
    shopify_product = await shopify_service.create_product(shopify_data)
    shopify_id = shopify_product.get("id")

    # 5. Sync to TikTok Shop (with normalized inventory)
    logger.info("Syncing product to TikTok Shop")
    try:
        await tiktok_service.sync_products([int(shopify_id)])
        tiktok_id = f"TT-{shopify_id}"  # Simplified
    except Exception as e:
        logger.warning(f"TikTok sync failed (will retry later): {e}")
        tiktok_id = None

    return {
        "aliexpress_id": product_id,
        "shopify_id": shopify_id,
        "tiktok_id": tiktok_id,
        "base_price": base_price,
        "selling_price": selling_price,
        "margin": selling_price - base_price,
    }


@app.task
def import_products_bulk(product_ids: List[str], markup_percentage: float = 40.0):
    """
    Import multiple products in parallel

    Args:
        product_ids: List of AliExpress product IDs
        markup_percentage: Price markup

    Returns:
        Summary of imports
    """
    logger.info(f"Starting bulk import of {len(product_ids)} products")

    results = {
        "total": len(product_ids),
        "success": 0,
        "failed": 0,
        "errors": [],
    }

    # Queue each product as separate task
    for product_id in product_ids:
        try:
            import_product_by_id.delay(product_id, markup_percentage)
            results["success"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"{product_id}: {str(e)}")

    logger.info(f"Bulk import queued: {results['success']} tasks created")
    return results


@app.task
def research_trending_products():
    """
    Daily task: Research trending products and auto-import winners

    Searches multiple niches, finds high-quality products, imports top performers
    """
    logger.info("🔍 Starting daily product research")

    result = asyncio.run(_research_and_import())

    logger.info(f"✅ Research complete: {result}")
    return result


async def _research_and_import() -> Dict[str, Any]:
    """Research trending products and import winners"""

    ali_service = AliExpressService()

    # Target niches (can be configured in database)
    niches = [
        "wireless earbuds",
        "phone accessories",
        "fitness tracker",
        "eco-friendly yoga mat",
        "portable blender",
        "led strip lights",
        "smart watch",
        "phone stand",
    ]

    all_winners = []

    for niche in niches:
        try:
            logger.info(f"Researching: {niche}")

            # Search with quality filters
            products = await ali_service.search_products(
                keywords=niche,
                min_price=5,
                max_price=50,
                min_orders=1000,  # Proven sellers only
                limit=20,
            )

            # Filter for quality
            for product in products:
                volume = product.get("volume", 0)
                eval_rate = float(product.get("evaluation_rate", "0%").rstrip("%"))

                # Winner criteria: high rating + proven sales
                if eval_rate > 95 and volume > 2000:
                    all_winners.append({
                        "product_id": product.get("product_id"),
                        "title": product.get("product_title"),
                        "price": product.get("target_sale_price"),
                        "orders": volume,
                        "rating": eval_rate,
                        "niche": niche,
                    })

            # Rate limiting
            await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"Error researching {niche}: {e}")

    # Sort by orders (demand proxy)
    all_winners.sort(key=lambda x: x["orders"], reverse=True)

    # Auto-import top 10 winners
    top_winners = all_winners[:10]

    logger.info(f"Found {len(all_winners)} quality products, importing top 10")

    imported = 0
    for winner in top_winners:
        try:
            # Queue import task
            import_product_by_id.delay(winner["product_id"], markup_percentage=40.0)
            imported += 1
        except Exception as e:
            logger.error(f"Failed to queue import for {winner['product_id']}: {e}")

    return {
        "niches_searched": len(niches),
        "products_found": len(all_winners),
        "imported": imported,
        "top_winners": top_winners,
    }


@app.task
def cleanup_failed_imports():
    """
    Clean up products that failed to sync to all platforms

    Retries TikTok sync for Shopify products without TikTok listings
    """
    logger.info("Running failed import cleanup")

    result = asyncio.run(_cleanup_async())

    return result


async def _cleanup_async() -> Dict[str, Any]:
    """Retry failed platform syncs"""

    shopify_service = ShopifyService()
    tiktok_service = TikTokService()

    # Get all Shopify products
    products = await shopify_service.list_products(limit=250)

    retry_count = 0
    success_count = 0

    for product in products:
        # Check if product has TikTok listing (simplified check)
        # In production, you'd track this in a database

        product_id = product.get("id")

        try:
            # Retry TikTok sync
            await tiktok_service.sync_products([int(product_id)])
            success_count += 1

        except Exception as e:
            logger.warning(f"Retry failed for product {product_id}: {e}")

        retry_count += 1

        # Rate limiting
        await asyncio.sleep(1)

    return {
        "products_checked": len(products),
        "retry_attempted": retry_count,
        "retry_success": success_count,
    }

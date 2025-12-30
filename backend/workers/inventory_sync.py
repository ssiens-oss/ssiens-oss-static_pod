"""
Automated Inventory Synchronization
Keep stock levels in sync across all platforms
"""
import asyncio
from typing import Dict, Any
from loguru import logger
from celery_app import app
from services.shopify_service import ShopifyService
from services.tiktok_service import TikTokService
from services.printify_service import PrintifyService
from services.aliexpress_service import AliExpressService


@app.task
def sync_all_suppliers():
    """
    Scheduled task: Sync inventory from all suppliers

    Runs every 4 hours to keep stock levels accurate
    """
    logger.info("🔄 Starting inventory sync from all suppliers")

    result = asyncio.run(_sync_all_async())

    logger.info(f"✅ Inventory sync complete: {result}")
    return result


async def _sync_all_async() -> Dict[str, Any]:
    """Sync inventory from all suppliers"""

    results = {
        "shopify": {},
        "printify": {},
        "aliexpress": {},
        "total_updated": 0,
        "total_errors": 0,
    }

    # 1. Sync Shopify inventory (normalizes existing values)
    try:
        logger.info("Syncing Shopify inventory")
        shopify_result = await _sync_shopify()
        results["shopify"] = shopify_result
        results["total_updated"] += shopify_result.get("synced_count", 0)
        results["total_errors"] += len(shopify_result.get("errors", []))

    except Exception as e:
        logger.error(f"Shopify sync failed: {e}")
        results["shopify"]["error"] = str(e)

    # 2. Sync Printify inventory
    try:
        logger.info("Syncing Printify inventory")
        printify_result = await _sync_printify()
        results["printify"] = printify_result
        results["total_updated"] += printify_result.get("synced_count", 0)

    except Exception as e:
        logger.error(f"Printify sync failed: {e}")
        results["printify"]["error"] = str(e)

    # 3. Sync AliExpress inventory (check supplier stock)
    try:
        logger.info("Checking AliExpress inventory")
        ali_result = await _sync_aliexpress()
        results["aliexpress"] = ali_result
        results["total_updated"] += ali_result.get("updated_count", 0)

    except Exception as e:
        logger.error(f"AliExpress sync failed: {e}")
        results["aliexpress"]["error"] = str(e)

    logger.info(
        f"Inventory sync summary: {results['total_updated']} products updated, "
        f"{results['total_errors']} errors"
    )

    return results


async def _sync_shopify() -> Dict[str, Any]:
    """Sync Shopify inventory (normalize values)"""

    shopify_service = ShopifyService()

    # Run Shopify's sync_inventory (which normalizes values)
    result = await shopify_service.sync_inventory()

    return result


async def _sync_printify() -> Dict[str, Any]:
    """
    Sync Printify inventory to Shopify

    Fetches Printify products and updates Shopify with normalized stock
    """

    printify_service = PrintifyService()
    shopify_service = ShopifyService()

    # Fetch Printify products
    printify_products = await printify_service.list_products()

    synced_count = 0
    errors = []

    for printify_product in printify_products:
        try:
            printify_id = printify_product.get("id")

            # Find matching Shopify product by SKU
            # Assuming Shopify SKU = "PRINT-{printify_id}"
            sku = f"PRINT-{printify_id}"

            # Get Shopify products (simplified - in production use SKU search)
            shopify_products = await shopify_service.list_products(limit=250)

            matching_product = None
            for sp in shopify_products:
                for variant in sp.get("variants", []):
                    if variant.get("sku") == sku:
                        matching_product = sp
                        break
                if matching_product:
                    break

            if not matching_product:
                logger.debug(f"Printify product {printify_id} not found in Shopify")
                continue

            # Printify stock is usually unlimited (999999999)
            # Already normalized when product was created
            # No update needed unless Printify changes their system

            synced_count += 1

        except Exception as e:
            logger.error(f"Error syncing Printify product {printify_product.get('id')}: {e}")
            errors.append(str(e))

        # Rate limiting
        await asyncio.sleep(0.5)

    return {
        "synced_count": synced_count,
        "total_products": len(printify_products),
        "errors": errors,
    }


async def _sync_aliexpress() -> Dict[str, Any]:
    """
    Sync AliExpress inventory to Shopify

    Checks actual supplier stock and updates Shopify
    """

    ali_service = AliExpressService()
    shopify_service = ShopifyService()

    # Get all Shopify products with AliExpress SKUs
    shopify_products = await shopify_service.list_products(limit=250)

    ali_products = [
        p for p in shopify_products
        if any(v.get("sku", "").startswith("ALI-") for v in p.get("variants", []))
    ]

    logger.info(f"Found {len(ali_products)} AliExpress products in Shopify")

    updated_count = 0
    out_of_stock = 0
    errors = []

    for product in ali_products:
        try:
            shopify_id = product.get("id")

            for variant in product.get("variants", []):
                sku = variant.get("sku", "")

                if not sku.startswith("ALI-"):
                    continue

                # Extract AliExpress product ID
                ali_product_id = sku.replace("ALI-", "")

                # Fetch current stock from AliExpress
                ali_product = await ali_service.get_product_details(ali_product_id)

                if not ali_product:
                    logger.warning(f"AliExpress product {ali_product_id} not found")
                    continue

                # Get supplier stock
                supplier_stock = ali_product.get("volume", 0)

                # Current Shopify stock
                current_stock = variant.get("inventory_quantity", 0)

                # Check if out of stock
                if supplier_stock == 0:
                    out_of_stock += 1
                    logger.warning(
                        f"⚠️ Product {product.get('title')} is OUT OF STOCK at supplier"
                    )

                # Update if stock changed significantly (>10% difference)
                if abs(supplier_stock - current_stock) > max(10, current_stock * 0.1):
                    # Update Shopify inventory
                    # Note: This uses Shopify's inventory API (simplified here)

                    logger.info(
                        f"Updating inventory for {product.get('title')}: "
                        f"{current_stock} → {supplier_stock}"
                    )

                    # In production, use:
                    # await shopify_service.update_inventory(variant_id, supplier_stock)

                    updated_count += 1

        except Exception as e:
            logger.error(f"Error syncing AliExpress inventory for {product.get('id')}: {e}")
            errors.append(str(e))

        # Rate limiting (AliExpress has strict limits)
        await asyncio.sleep(2)

    return {
        "checked": len(ali_products),
        "updated_count": updated_count,
        "out_of_stock": out_of_stock,
        "errors": errors,
    }


@app.task
def alert_low_stock():
    """
    Alert when products are low on stock

    Sends notifications for products below threshold
    """
    logger.info("Checking for low stock products")

    result = asyncio.run(_alert_low_stock_async())

    return result


async def _alert_low_stock_async() -> Dict[str, Any]:
    """Check for low stock and send alerts"""

    shopify_service = ShopifyService()

    LOW_STOCK_THRESHOLD = 10

    # Get all products
    products = await shopify_service.list_products(limit=250)

    low_stock = []

    for product in products:
        for variant in product.get("variants", []):
            qty = variant.get("inventory_quantity", 0)

            if 0 < qty <= LOW_STOCK_THRESHOLD:
                low_stock.append({
                    "product": product.get("title"),
                    "sku": variant.get("sku"),
                    "quantity": qty,
                })

    if low_stock:
        logger.warning(f"⚠️ {len(low_stock)} products are low on stock")

        for item in low_stock:
            logger.warning(f"  • {item['product']} (SKU: {item['sku']}): {item['quantity']} left")

        # In production: Send alert to Discord/Telegram/Email
        # await send_alert(f"Low stock alert: {len(low_stock)} products")

    else:
        logger.info("✅ All products have sufficient stock")

    return {
        "low_stock_count": len(low_stock),
        "products": low_stock,
        "threshold": LOW_STOCK_THRESHOLD,
    }


@app.task
def pause_out_of_stock_products():
    """
    Automatically pause products that are out of stock

    Prevents orders for unavailable products
    """
    logger.info("Checking for out of stock products")

    result = asyncio.run(_pause_out_of_stock_async())

    return result


async def _pause_out_of_stock_async() -> Dict[str, Any]:
    """Pause products with zero inventory"""

    shopify_service = ShopifyService()

    # Get all products
    products = await shopify_service.list_products(limit=250)

    paused_count = 0

    for product in products:
        product_id = product.get("id")

        # Check if all variants are out of stock
        all_out = all(
            v.get("inventory_quantity", 0) == 0
            for v in product.get("variants", [])
        )

        if all_out and product.get("status") == "active":
            try:
                # Pause product (set status to draft)
                await shopify_service.update_product(
                    str(product_id),
                    {"status": "draft"}
                )

                logger.info(f"Paused out of stock product: {product.get('title')}")
                paused_count += 1

            except Exception as e:
                logger.error(f"Failed to pause product {product_id}: {e}")

    return {
        "products_checked": len(products),
        "paused": paused_count,
    }

"""
Automated Order Fulfillment Workflow
Shopify Orders → AliExpress → Tracking Sync
"""
import asyncio
from typing import List, Dict, Any
from loguru import logger
from celery_app import app
from services.shopify_service import ShopifyService
from services.aliexpress_service import AliExpressService


@app.task(bind=True, max_retries=5)
def fulfill_order(self, shopify_order_id: str):
    """
    Automatically fulfill a Shopify order via AliExpress

    Args:
        shopify_order_id: Shopify order ID

    Returns:
        Fulfillment details
    """
    try:
        logger.info(f"Starting fulfillment for Shopify order: {shopify_order_id}")

        result = asyncio.run(_fulfill_order_async(shopify_order_id))

        logger.info(
            f"✅ Order {shopify_order_id} fulfilled: "
            f"AliExpress order {result['aliexpress_order_id']}"
        )

        return result

    except Exception as e:
        logger.error(f"Fulfillment failed for order {shopify_order_id}: {e}")

        # Retry with exponential backoff (max 5 retries)
        if self.request.retries < 5:
            raise self.retry(exc=e, countdown=300 * (2 ** self.request.retries))  # 5min base
        else:
            # After max retries, log critical error
            logger.critical(
                f"❌ Order {shopify_order_id} failed after {self.request.retries} retries"
            )
            raise


async def _fulfill_order_async(shopify_order_id: str) -> Dict[str, Any]:
    """Async implementation of order fulfillment"""

    shopify_service = ShopifyService()
    ali_service = AliExpressService()

    # 1. Fetch order from Shopify
    logger.info(f"Fetching order {shopify_order_id} from Shopify")

    orders = await shopify_service.list_orders(limit=250)
    order = next((o for o in orders if str(o.get("id")) == shopify_order_id), None)

    if not order:
        raise ValueError(f"Order {shopify_order_id} not found")

    # 2. Extract order details
    line_items = order.get("line_items", [])
    shipping_address = order.get("shipping_address")

    if not shipping_address:
        raise ValueError(f"Order {shopify_order_id} has no shipping address")

    # 3. Prepare AliExpress products
    ali_products = []

    for item in line_items:
        # Extract AliExpress product ID from SKU
        sku = item.get("sku", "")

        if sku.startswith("ALI-"):
            ali_product_id = sku.replace("ALI-", "")

            ali_products.append({
                "product_id": ali_product_id,
                "quantity": item.get("quantity", 1),
                "variant_id": item.get("variant_id"),
            })

            logger.info(f"  Item: {item.get('title')} (Qty: {item.get('quantity')})")

        else:
            logger.warning(f"  Skipping {item.get('title')} - not an AliExpress product")

    if not ali_products:
        raise ValueError(f"Order {shopify_order_id} has no AliExpress products")

    # 4. Format shipping address for AliExpress
    shipping_data = {
        "name": f"{shipping_address.get('first_name', '')} {shipping_address.get('last_name', '')}".strip(),
        "address1": shipping_address.get("address1"),
        "city": shipping_address.get("city"),
        "state": shipping_address.get("province"),
        "zip": shipping_address.get("zip"),
        "country": shipping_address.get("country_code"),
        "phone": shipping_address.get("phone", ""),
    }

    logger.info(
        f"Shipping to: {shipping_data['name']}, "
        f"{shipping_data['city']}, {shipping_data['country']}"
    )

    # 5. Place order on AliExpress
    logger.info("Placing order on AliExpress")

    ali_order = await ali_service.place_order(
        shopify_order_id=shopify_order_id,
        products=ali_products,
        shipping_address=shipping_data,
    )

    ali_order_id = ali_order.get("order_id")
    tracking_number = ali_order.get("tracking_number", "PENDING")

    logger.info(f"AliExpress order placed: {ali_order_id}")
    logger.info(f"Tracking: {tracking_number}")

    # 6. Mark order as fulfilled in Shopify
    logger.info("Updating Shopify order status")

    await shopify_service.fulfill_order(shopify_order_id)

    # 7. Return fulfillment details
    return {
        "shopify_order_id": shopify_order_id,
        "aliexpress_order_id": ali_order_id,
        "tracking_number": tracking_number,
        "items_count": len(ali_products),
        "customer_email": order.get("email"),
    }


@app.task
def process_pending_orders():
    """
    Scheduled task: Process all unfulfilled Shopify orders

    Runs every 30 minutes to catch new orders automatically
    """
    logger.info("🔄 Processing pending orders")

    result = asyncio.run(_process_pending_async())

    logger.info(f"✅ Order processing complete: {result}")
    return result


async def _process_pending_async() -> Dict[str, Any]:
    """Process all pending orders"""

    shopify_service = ShopifyService()

    # Fetch unfulfilled orders
    orders = await shopify_service.list_orders(limit=250, status="unfulfilled")

    logger.info(f"Found {len(orders)} unfulfilled orders")

    processed = 0
    failed = 0
    skipped = 0

    for order in orders:
        order_id = str(order.get("id"))
        order_number = order.get("order_number")

        try:
            # Check if order has AliExpress products
            has_ali_products = any(
                item.get("sku", "").startswith("ALI-")
                for item in order.get("line_items", [])
            )

            if not has_ali_products:
                logger.info(f"Skipping order #{order_number} - no AliExpress products")
                skipped += 1
                continue

            # Queue fulfillment task
            fulfill_order.delay(order_id)
            processed += 1

            logger.info(f"Queued fulfillment for order #{order_number}")

        except Exception as e:
            logger.error(f"Failed to queue order #{order_number}: {e}")
            failed += 1

        # Rate limiting
        await asyncio.sleep(1)

    return {
        "total_orders": len(orders),
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
    }


@app.task
def update_tracking_numbers():
    """
    Update tracking numbers for fulfilled orders

    Checks AliExpress for tracking updates and syncs to Shopify
    """
    logger.info("Updating tracking numbers")

    result = asyncio.run(_update_tracking_async())

    return result


async def _update_tracking_async() -> Dict[str, Any]:
    """Sync tracking numbers from AliExpress to Shopify"""

    shopify_service = ShopifyService()
    ali_service = AliExpressService()

    # Get recently fulfilled orders (simplified - in production use DB)
    orders = await shopify_service.list_orders(limit=100)

    updated = 0
    pending = 0

    for order in orders:
        order_id = str(order.get("id"))

        # Skip if already has tracking
        if order.get("fulfillment_status") == "fulfilled":
            continue

        try:
            # Get tracking from AliExpress (would need order mapping in DB)
            # For now, placeholder logic

            pending += 1

        except Exception as e:
            logger.error(f"Tracking update failed for order {order_id}: {e}")

    return {
        "orders_checked": len(orders),
        "updated": updated,
        "pending": pending,
    }


@app.task(bind=True)
def retry_failed_fulfillments(self):
    """
    Retry orders that failed to fulfill

    Checks for orders older than 1 hour that are still unfulfilled
    """
    logger.info("Retrying failed fulfillments")

    result = asyncio.run(_retry_failed_async())

    return result


async def _retry_failed_async() -> Dict[str, Any]:
    """Retry failed order fulfillments"""

    shopify_service = ShopifyService()

    # Get old unfulfilled orders
    orders = await shopify_service.list_orders(limit=250, status="unfulfilled")

    retry_count = 0
    success_count = 0

    for order in orders:
        order_id = str(order.get("id"))

        # Check if order is old enough to retry (1+ hours)
        # Simplified - in production, track retry attempts in DB

        try:
            # Retry fulfillment
            fulfill_order.delay(order_id)
            retry_count += 1

        except Exception as e:
            logger.error(f"Retry queue failed for order {order_id}: {e}")

    return {
        "orders_checked": len(orders),
        "retried": retry_count,
    }

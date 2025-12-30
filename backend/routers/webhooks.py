"""
Webhook Handlers for Real-Time Event Processing
Shopify, TikTok, Stripe webhooks
"""
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import hmac
import hashlib
from loguru import logger

from config.settings import settings
from workers.order_fulfillment import fulfill_order
from services.shopify_service import ShopifyService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_shopify_webhook(data: bytes, hmac_header: str) -> bool:
    """Verify Shopify webhook signature"""
    if not settings.SHOPIFY_WEBHOOK_SECRET:
        logger.warning("SHOPIFY_WEBHOOK_SECRET not configured, skipping verification")
        return True

    calculated_hmac = hmac.new(
        settings.SHOPIFY_WEBHOOK_SECRET.encode("utf-8"),
        data,
        hashlib.sha256,
    ).digest().hex()

    return hmac.compare_digest(calculated_hmac, hmac_header)


@router.post("/shopify/orders/create")
async def shopify_order_created(
    request: Request,
    x_shopify_hmac_sha256: Optional[str] = Header(None),
):
    """
    Shopify webhook: Order created

    Automatically triggers fulfillment workflow
    """
    body = await request.body()

    # Verify webhook signature
    if not verify_shopify_webhook(body, x_shopify_hmac_sha256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    data = await request.json()

    order_id = str(data.get("id"))
    order_number = data.get("order_number")

    logger.info(f"📦 Shopify webhook: Order #{order_number} created (ID: {order_id})")

    # Check if order has AliExpress products
    has_ali_products = any(
        item.get("sku", "").startswith("ALI-")
        for item in data.get("line_items", [])
    )

    if has_ali_products:
        # Queue automatic fulfillment
        try:
            fulfill_order.delay(order_id)
            logger.info(f"✅ Queued automatic fulfillment for order #{order_number}")

        except Exception as e:
            logger.error(f"Failed to queue fulfillment for order #{order_number}: {e}")
            # Don't return error - webhook should still succeed

    else:
        logger.info(f"Order #{order_number} has no AliExpress products, skipping auto-fulfillment")

    return {"status": "received", "order_id": order_id}


@router.post("/shopify/orders/paid")
async def shopify_order_paid(
    request: Request,
    x_shopify_hmac_sha256: Optional[str] = Header(None),
):
    """
    Shopify webhook: Order paid

    Can trigger additional automation (e.g., priority fulfillment)
    """
    body = await request.body()

    if not verify_shopify_webhook(body, x_shopify_hmac_sha256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    data = await request.json()

    order_id = str(data.get("id"))
    order_number = data.get("order_number")

    logger.info(f"💰 Shopify webhook: Order #{order_number} paid")

    # Could trigger priority processing here

    return {"status": "received", "order_id": order_id}


@router.post("/shopify/products/update")
async def shopify_product_updated(
    request: Request,
    x_shopify_hmac_sha256: Optional[str] = Header(None),
):
    """
    Shopify webhook: Product updated

    Sync changes to TikTok Shop
    """
    body = await request.body()

    if not verify_shopify_webhook(body, x_shopify_hmac_sha256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    data = await request.json()

    product_id = data.get("id")
    title = data.get("title")

    logger.info(f"📝 Shopify webhook: Product '{title}' updated (ID: {product_id})")

    # Could trigger TikTok sync here
    # from workers.product_import import sync_to_tiktok
    # sync_to_tiktok.delay(product_id)

    return {"status": "received", "product_id": product_id}


@router.post("/shopify/inventory/update")
async def shopify_inventory_updated(
    request: Request,
    x_shopify_hmac_sha256: Optional[str] = Header(None),
):
    """
    Shopify webhook: Inventory level updated

    Sync to other platforms if needed
    """
    body = await request.body()

    if not verify_shopify_webhook(body, x_shopify_hmac_sha256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    data = await request.json()

    logger.info(f"📊 Shopify webhook: Inventory updated")

    # Could trigger low stock alerts
    # from workers.inventory_sync import check_low_stock
    # check_low_stock.delay()

    return {"status": "received"}


@router.post("/tiktok/orders")
async def tiktok_order_webhook(request: Request):
    """
    TikTok Shop webhook: New order

    Create order in Shopify and trigger fulfillment
    """
    data = await request.json()

    # TikTok webhook verification would go here
    # (check timestamp + signature)

    order_id = data.get("order_id")

    logger.info(f"🎵 TikTok webhook: Order {order_id} received")

    try:
        # Create order in Shopify from TikTok order data
        shopify_service = ShopifyService()

        # Convert TikTok order format to Shopify format
        # (simplified - in production, handle full mapping)

        logger.info(f"Creating Shopify order from TikTok order {order_id}")

        # Then trigger fulfillment
        # fulfill_order.delay(shopify_order_id)

    except Exception as e:
        logger.error(f"Error processing TikTok order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "received", "order_id": order_id}


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: Optional[str] = Header(None)):
    """
    Stripe webhook: Payment events

    Handle subscription updates, payment failures, etc.
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    body = await request.body()

    # Verify Stripe webhook signature
    try:
        import stripe

        stripe.api_key = settings.STRIPE_API_KEY

        event = stripe.Webhook.construct_event(
            payload=body,
            sig_header=stripe_signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )

    except Exception as e:
        logger.error(f"Stripe webhook verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]

    logger.info(f"💳 Stripe webhook: {event_type}")

    # Handle different event types
    if event_type == "payment_intent.succeeded":
        # Payment successful
        payment_intent = event["data"]["object"]
        logger.info(f"Payment succeeded: {payment_intent.get('id')}")

    elif event_type == "payment_intent.payment_failed":
        # Payment failed
        payment_intent = event["data"]["object"]
        logger.warning(f"Payment failed: {payment_intent.get('id')}")

        # Could send notification to admin

    elif event_type == "customer.subscription.deleted":
        # Subscription cancelled
        subscription = event["data"]["object"]
        logger.info(f"Subscription cancelled: {subscription.get('id')}")

    return {"status": "received", "event_type": event_type}


@router.get("/test")
async def test_webhook():
    """Test endpoint to verify webhooks are working"""
    return {
        "status": "ok",
        "message": "Webhook endpoint is operational",
        "endpoints": [
            "/webhooks/shopify/orders/create",
            "/webhooks/shopify/orders/paid",
            "/webhooks/shopify/products/update",
            "/webhooks/shopify/inventory/update",
            "/webhooks/tiktok/orders",
            "/webhooks/stripe/webhook",
        ],
    }

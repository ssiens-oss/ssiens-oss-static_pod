"""
Analytics and Monitoring Workers
Generate reports and health checks
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from loguru import logger
from celery_app import app
from services.shopify_service import ShopifyService
from services.tiktok_service import TikTokService


@app.task
def generate_daily_report():
    """
    Scheduled task: Generate daily performance report

    Runs at midnight UTC to summarize the previous day
    """
    logger.info("📊 Generating daily report")

    result = asyncio.run(_generate_report_async())

    logger.info(f"✅ Daily report complete: {result}")
    return result


async def _generate_report_async() -> Dict[str, Any]:
    """Generate comprehensive daily report"""

    shopify_service = ShopifyService()
    tiktok_service = TikTokService()

    # Date range: yesterday
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=1)

    report = {
        "date": str(end_date),
        "orders": {},
        "products": {},
        "revenue": {},
        "tiktok": {},
    }

    # 1. Orders Summary
    try:
        orders = await shopify_service.list_orders(limit=250)

        # Filter for yesterday's orders
        yesterday_orders = [
            o for o in orders
            if o.get("created_at", "").startswith(str(start_date))
        ]

        total_revenue = sum(
            float(o.get("total_price", 0))
            for o in yesterday_orders
        )

        fulfilled = [o for o in yesterday_orders if o.get("fulfillment_status") == "fulfilled"]
        pending = [o for o in yesterday_orders if o.get("fulfillment_status") != "fulfilled"]

        report["orders"] = {
            "total": len(yesterday_orders),
            "fulfilled": len(fulfilled),
            "pending": len(pending),
            "fulfillment_rate": round(len(fulfilled) / max(1, len(yesterday_orders)) * 100, 1),
        }

        report["revenue"] = {
            "total": round(total_revenue, 2),
            "average_order_value": round(total_revenue / max(1, len(yesterday_orders)), 2),
        }

    except Exception as e:
        logger.error(f"Error calculating orders: {e}")
        report["orders"]["error"] = str(e)

    # 2. Products Summary
    try:
        products = await shopify_service.list_products(limit=250)

        active_products = [p for p in products if p.get("status") == "active"]
        low_stock = []

        for product in active_products:
            for variant in product.get("variants", []):
                qty = variant.get("inventory_quantity", 0)
                if 0 < qty <= 10:
                    low_stock.append(product.get("title"))

        report["products"] = {
            "total": len(products),
            "active": len(active_products),
            "low_stock": len(low_stock),
        }

    except Exception as e:
        logger.error(f"Error calculating products: {e}")
        report["products"]["error"] = str(e)

    # 3. TikTok Analytics
    try:
        tiktok_analytics = await tiktok_service.get_analytics(
            start_date=str(start_date),
            end_date=str(end_date),
        )

        report["tiktok"] = tiktok_analytics

    except Exception as e:
        logger.error(f"Error fetching TikTok analytics: {e}")
        report["tiktok"]["error"] = str(e)

    # 4. Log summary
    logger.info(
        f"📊 Daily Report Summary:\n"
        f"  Orders: {report['orders'].get('total', 0)} "
        f"({report['orders'].get('fulfillment_rate', 0)}% fulfilled)\n"
        f"  Revenue: ${report['revenue'].get('total', 0)}\n"
        f"  Products: {report['products'].get('active', 0)} active, "
        f"{report['products'].get('low_stock', 0)} low stock"
    )

    # In production: Send report via email/Slack/Discord

    return report


@app.task
def health_check():
    """
    Scheduled task: System health check

    Runs every 5 minutes to verify all services are operational
    """
    result = asyncio.run(_health_check_async())

    if not result.get("healthy"):
        logger.error(f"❌ Health check failed: {result}")
    else:
        logger.debug(f"✅ Health check passed: {result}")

    return result


async def _health_check_async() -> Dict[str, Any]:
    """Check health of all services"""

    health = {
        "timestamp": datetime.utcnow().isoformat(),
        "healthy": True,
        "services": {},
    }

    # 1. Check Shopify
    try:
        shopify_service = ShopifyService()
        await shopify_service.list_products(limit=1)

        health["services"]["shopify"] = {"status": "ok"}

    except Exception as e:
        health["healthy"] = False
        health["services"]["shopify"] = {"status": "error", "error": str(e)}
        logger.error(f"Shopify health check failed: {e}")

    # 2. Check TikTok
    try:
        tiktok_service = TikTokService()
        await tiktok_service.list_products()

        health["services"]["tiktok"] = {"status": "ok"}

    except Exception as e:
        health["healthy"] = False
        health["services"]["tiktok"] = {"status": "error", "error": str(e)}
        logger.error(f"TikTok health check failed: {e}")

    # 3. Check Celery queue
    # Simplified - in production, check Redis connection and queue depth
    try:
        from celery_app import app as celery_app

        inspect = celery_app.control.inspect()
        stats = inspect.stats()

        if stats:
            health["services"]["celery"] = {"status": "ok", "workers": len(stats)}
        else:
            health["healthy"] = False
            health["services"]["celery"] = {"status": "error", "error": "No workers"}

    except Exception as e:
        health["healthy"] = False
        health["services"]["celery"] = {"status": "error", "error": str(e)}

    return health


@app.task
def calculate_profit_margins():
    """
    Calculate profit margins for all products

    Identifies best and worst performers
    """
    logger.info("Calculating profit margins")

    result = asyncio.run(_calculate_margins_async())

    return result


async def _calculate_margins_async() -> Dict[str, Any]:
    """Calculate profit margins"""

    shopify_service = ShopifyService()

    products = await shopify_service.list_products(limit=250)

    margins = []

    for product in products:
        for variant in product.get("variants", []):
            sku = variant.get("sku", "")
            selling_price = float(variant.get("price", 0))

            # Estimate cost based on SKU prefix
            if sku.startswith("ALI-"):
                # AliExpress: assume 40% markup
                cost = selling_price / 1.4
            elif sku.startswith("PRINT-"):
                # Printify: typical base cost
                cost = selling_price * 0.5
            else:
                cost = 0

            profit = selling_price - cost
            margin_pct = (profit / max(0.01, selling_price)) * 100

            margins.append({
                "product": product.get("title"),
                "sku": sku,
                "cost": round(cost, 2),
                "price": selling_price,
                "profit": round(profit, 2),
                "margin_pct": round(margin_pct, 1),
            })

    # Sort by margin percentage
    margins.sort(key=lambda x: x["margin_pct"], reverse=True)

    # Top and bottom performers
    top_5 = margins[:5]
    bottom_5 = margins[-5:]

    logger.info("Top 5 profit margins:")
    for item in top_5:
        logger.info(f"  {item['product']}: {item['margin_pct']}% (${item['profit']})")

    logger.info("Bottom 5 profit margins:")
    for item in bottom_5:
        logger.warning(f"  {item['product']}: {item['margin_pct']}% (${item['profit']})")

    return {
        "total_products": len(margins),
        "top_5": top_5,
        "bottom_5": bottom_5,
        "average_margin": round(sum(m["margin_pct"] for m in margins) / max(1, len(margins)), 1),
    }


@app.task
def identify_best_sellers():
    """
    Identify best-selling products

    Helps prioritize inventory and marketing
    """
    logger.info("Analyzing best sellers")

    result = asyncio.run(_best_sellers_async())

    return result


async def _best_sellers_async() -> Dict[str, Any]:
    """Find best-selling products"""

    shopify_service = ShopifyService()

    # Get recent orders
    orders = await shopify_service.list_orders(limit=250)

    # Count sales by product
    sales_count = {}

    for order in orders:
        for item in order.get("line_items", []):
            product_id = item.get("product_id")
            title = item.get("title")
            qty = item.get("quantity", 0)

            if product_id not in sales_count:
                sales_count[product_id] = {"title": title, "units": 0, "revenue": 0}

            sales_count[product_id]["units"] += qty
            sales_count[product_id]["revenue"] += float(item.get("price", 0)) * qty

    # Sort by units sold
    best_sellers = sorted(
        [{"product_id": k, **v} for k, v in sales_count.items()],
        key=lambda x: x["units"],
        reverse=True
    )[:10]

    logger.info("Top 10 Best Sellers:")
    for i, product in enumerate(best_sellers, 1):
        logger.info(
            f"  {i}. {product['title']}: {product['units']} units, "
            f"${product['revenue']:.2f} revenue"
        )

    return {
        "best_sellers": best_sellers,
        "total_products_sold": len(sales_count),
    }

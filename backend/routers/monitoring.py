"""
Monitoring and Dashboard API
System status, metrics, and control endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

from workers.product_import import import_product_by_id, import_products_bulk
from workers.order_fulfillment import fulfill_order, process_pending_orders
from workers.inventory_sync import sync_all_suppliers, alert_low_stock
from workers.analytics import (
    generate_daily_report,
    health_check,
    calculate_profit_margins,
    identify_best_sellers,
)

router = APIRouter(prefix="/monitor", tags=["monitoring"])


@router.get("/health")
async def get_health():
    """
    System health check

    Returns status of all services
    """
    result = health_check.delay()

    # Wait for result (short timeout)
    try:
        health_data = result.get(timeout=5)
        return health_data

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Health check timeout")


@router.get("/status")
async def get_system_status():
    """
    Overall system status

    Quick overview of platform health
    """
    from celery_app import app as celery_app

    try:
        # Check Celery workers
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        active_tasks = inspect.active()

        worker_count = len(stats) if stats else 0
        active_task_count = sum(len(tasks) for tasks in (active_tasks or {}).values())

        # Check scheduled tasks
        scheduled = inspect.scheduled()
        scheduled_count = sum(len(tasks) for tasks in (scheduled or {}).values())

        return {
            "status": "operational" if worker_count > 0 else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "celery": {
                "workers": worker_count,
                "active_tasks": active_task_count,
                "scheduled_tasks": scheduled_count,
            },
            "uptime": "N/A",  # Would track from app start time
        }

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/metrics")
async def get_metrics():
    """
    System metrics and performance data

    Returns operational metrics for dashboard
    """
    try:
        # Trigger analytics tasks
        report_task = generate_daily_report.delay()
        margins_task = calculate_profit_margins.delay()
        sellers_task = identify_best_sellers.delay()

        # Wait for results
        report = report_task.get(timeout=30)
        margins = margins_task.get(timeout=30)
        sellers = sellers_task.get(timeout=30)

        return {
            "daily_report": report,
            "profit_margins": margins,
            "best_sellers": sellers,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks")
async def get_active_tasks():
    """
    List active background tasks

    Shows what automation is currently running
    """
    from celery_app import app as celery_app

    try:
        inspect = celery_app.control.inspect()

        active = inspect.active() or {}
        scheduled = inspect.scheduled() or {}
        reserved = inspect.reserved() or {}

        return {
            "active": active,
            "scheduled": scheduled,
            "reserved": reserved,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/import")
async def trigger_import(product_id: str, markup: float = 40.0):
    """
    Manually trigger product import

    Args:
        product_id: AliExpress product ID
        markup: Price markup percentage

    Returns:
        Task ID for tracking
    """
    try:
        task = import_product_by_id.delay(product_id, markup)

        logger.info(f"Triggered import for product {product_id}, task: {task.id}")

        return {
            "task_id": task.id,
            "product_id": product_id,
            "status": "queued",
        }

    except Exception as e:
        logger.error(f"Failed to trigger import: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/import-bulk")
async def trigger_bulk_import(product_ids: List[str], markup: float = 40.0):
    """
    Manually trigger bulk product import

    Args:
        product_ids: List of AliExpress product IDs
        markup: Price markup percentage

    Returns:
        Summary of queued tasks
    """
    try:
        task = import_products_bulk.delay(product_ids, markup)

        logger.info(f"Triggered bulk import of {len(product_ids)} products, task: {task.id}")

        return {
            "task_id": task.id,
            "product_count": len(product_ids),
            "status": "queued",
        }

    except Exception as e:
        logger.error(f"Failed to trigger bulk import: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/fulfill-orders")
async def trigger_order_fulfillment():
    """
    Manually trigger order fulfillment

    Processes all pending orders immediately
    """
    try:
        task = process_pending_orders.delay()

        logger.info(f"Triggered order fulfillment, task: {task.id}")

        return {
            "task_id": task.id,
            "status": "queued",
        }

    except Exception as e:
        logger.error(f"Failed to trigger order fulfillment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/sync-inventory")
async def trigger_inventory_sync():
    """
    Manually trigger inventory sync

    Syncs inventory from all suppliers
    """
    try:
        task = sync_all_suppliers.delay()

        logger.info(f"Triggered inventory sync, task: {task.id}")

        return {
            "task_id": task.id,
            "status": "queued",
        }

    except Exception as e:
        logger.error(f"Failed to trigger inventory sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/check-low-stock")
async def trigger_low_stock_check():
    """
    Manually trigger low stock alert

    Checks for products below threshold
    """
    try:
        task = alert_low_stock.delay()

        logger.info(f"Triggered low stock check, task: {task.id}")

        return {
            "task_id": task.id,
            "status": "queued",
        }

    except Exception as e:
        logger.error(f"Failed to trigger low stock check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Get status of a specific task

    Args:
        task_id: Celery task ID

    Returns:
        Task status and result
    """
    from celery.result import AsyncResult
    from celery_app import app as celery_app

    try:
        task = AsyncResult(task_id, app=celery_app)

        return {
            "task_id": task_id,
            "status": task.state,
            "result": task.result if task.ready() else None,
            "info": task.info,
        }

    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/recent")
async def get_recent_logs(limit: int = 100):
    """
    Get recent system logs

    Args:
        limit: Number of log entries to return

    Returns:
        Recent log entries
    """
    # This is a simplified implementation
    # In production, you'd read from a log file or logging service

    return {
        "message": "Log retrieval not yet implemented",
        "note": "Use external log aggregation service (e.g., Datadog, CloudWatch)",
    }


@router.get("/stats/overview")
async def get_stats_overview():
    """
    Quick stats overview for dashboard

    Returns key metrics at a glance
    """
    try:
        from services.shopify_service import ShopifyService
        import asyncio

        shopify_service = ShopifyService()

        # Get counts asynchronously
        products = await shopify_service.list_products(limit=250)
        orders = await shopify_service.list_orders(limit=250)

        # Calculate quick stats
        total_products = len(products)
        active_products = len([p for p in products if p.get("status") == "active"])

        total_orders = len(orders)
        pending_orders = len([o for o in orders if o.get("fulfillment_status") != "fulfilled"])

        total_revenue = sum(float(o.get("total_price", 0)) for o in orders)

        return {
            "products": {
                "total": total_products,
                "active": active_products,
            },
            "orders": {
                "total": total_orders,
                "pending": pending_orders,
                "fulfilled": total_orders - pending_orders,
            },
            "revenue": {
                "total": round(total_revenue, 2),
                "average_order_value": round(total_revenue / max(1, total_orders), 2),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get stats overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

"""
Celery Application Configuration
Background task queue for automated dropshipping workflows
"""
from celery import Celery
from celery.schedules import crontab
from config.settings import settings

# Initialize Celery app
app = Celery(
    "staticwaves",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "workers.product_import",
        "workers.order_fulfillment",
        "workers.inventory_sync",
        "workers.analytics",
    ],
)

# Celery Configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # 55 min soft limit
    worker_prefetch_multiplier=1,  # One task at a time for reliability
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
)

# Scheduled Tasks (Cron-style)
app.conf.beat_schedule = {
    # Sync inventory from all suppliers every 4 hours
    "sync-inventory-4h": {
        "task": "workers.inventory_sync.sync_all_suppliers",
        "schedule": crontab(minute=0, hour="*/4"),
    },
    # Process pending orders every 30 minutes
    "fulfill-orders-30m": {
        "task": "workers.order_fulfillment.process_pending_orders",
        "schedule": crontab(minute="*/30"),
    },
    # Research trending products daily at 9 AM UTC
    "research-products-daily": {
        "task": "workers.product_import.research_trending_products",
        "schedule": crontab(hour=9, minute=0),
    },
    # Generate analytics report daily at midnight
    "analytics-daily": {
        "task": "workers.analytics.generate_daily_report",
        "schedule": crontab(hour=0, minute=0),
    },
    # Health check every 5 minutes
    "health-check-5m": {
        "task": "workers.analytics.health_check",
        "schedule": crontab(minute="*/5"),
    },
}

if __name__ == "__main__":
    app.start()

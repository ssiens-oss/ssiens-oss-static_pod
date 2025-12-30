"""
Example: Running Automated Workflows
Demonstrates how to trigger automation tasks programmatically
"""
import asyncio
import time
from loguru import logger

# Import Celery tasks
from workers.product_import import (
    import_product_by_id,
    import_products_bulk,
    research_trending_products,
)
from workers.order_fulfillment import (
    fulfill_order,
    process_pending_orders,
)
from workers.inventory_sync import (
    sync_all_suppliers,
    alert_low_stock,
)
from workers.analytics import (
    generate_daily_report,
    health_check,
    calculate_profit_margins,
    identify_best_sellers,
)


def example_1_manual_product_import():
    """
    Example 1: Manually import a specific product

    Use case: You found a winning product and want to add it immediately
    """
    print("\n" + "="*60)
    print("Example 1: Manual Product Import")
    print("="*60 + "\n")

    # AliExpress product ID you want to import
    product_id = "1005001234567890"  # Replace with real product ID
    markup_percentage = 40.0  # 40% markup

    print(f"Importing product: {product_id}")
    print(f"Markup: {markup_percentage}%")

    # Trigger import task (runs in background)
    task = import_product_by_id.delay(product_id, markup_percentage)

    print(f"\n✅ Task queued: {task.id}")
    print("Check status with: celery -A celery_app inspect active")

    # Optional: Wait for result (blocks until complete)
    # result = task.get(timeout=120)
    # print(f"Result: {result}")


def example_2_bulk_import():
    """
    Example 2: Bulk import multiple products

    Use case: You have a list of products to import at once
    """
    print("\n" + "="*60)
    print("Example 2: Bulk Product Import")
    print("="*60 + "\n")

    # List of AliExpress product IDs
    product_ids = [
        "1005001234567890",
        "1005009876543210",
        "1005005555555555",
    ]

    print(f"Importing {len(product_ids)} products in bulk")

    # Trigger bulk import
    task = import_products_bulk.delay(product_ids, markup_percentage=40.0)

    print(f"\n✅ Bulk import task queued: {task.id}")
    print(f"{len(product_ids)} import tasks will be created")


def example_3_auto_research():
    """
    Example 3: Trigger product research

    Use case: Manually run the daily research task
    """
    print("\n" + "="*60)
    print("Example 3: Product Research")
    print("="*60 + "\n")

    print("Researching trending products across multiple niches")
    print("This will search, filter, and auto-import top winners")

    # Trigger research task
    task = research_trending_products.delay()

    print(f"\n✅ Research task queued: {task.id}")
    print("This may take 5-10 minutes to complete")

    # Optional: Wait for result
    # result = task.get(timeout=600)
    # print(f"\nResults: {result['products_found']} products found")
    # print(f"Imported: {result['imported']} products")


def example_4_auto_fulfill_orders():
    """
    Example 4: Process all pending orders

    Use case: Immediately fulfill all unfulfilled orders
    """
    print("\n" + "="*60)
    print("Example 4: Auto-Fulfill Orders")
    print("="*60 + "\n")

    print("Processing all unfulfilled Shopify orders")
    print("Will place AliExpress orders and update tracking")

    # Trigger order processing
    task = process_pending_orders.delay()

    print(f"\n✅ Order fulfillment task queued: {task.id}")
    print("Fulfillment tasks will be created for each order")


def example_5_inventory_sync():
    """
    Example 5: Sync inventory from all suppliers

    Use case: Force inventory update across all platforms
    """
    print("\n" + "="*60)
    print("Example 5: Inventory Sync")
    print("="*60 + "\n")

    print("Syncing inventory from all suppliers:")
    print("  - Shopify (normalize values)")
    print("  - Printify (check POD stock)")
    print("  - AliExpress (verify supplier stock)")

    # Trigger inventory sync
    task = sync_all_suppliers.delay()

    print(f"\n✅ Inventory sync task queued: {task.id}")
    print("This may take 10-15 minutes for large catalogs")


def example_6_analytics():
    """
    Example 6: Generate analytics and reports

    Use case: Get performance metrics and insights
    """
    print("\n" + "="*60)
    print("Example 6: Analytics & Reports")
    print("="*60 + "\n")

    print("Generating analytics reports:")

    # Daily performance report
    report_task = generate_daily_report.delay()
    print(f"  📊 Daily report: {report_task.id}")

    # Profit margins analysis
    margins_task = calculate_profit_margins.delay()
    print(f"  💰 Profit margins: {margins_task.id}")

    # Best sellers
    sellers_task = identify_best_sellers.delay()
    print(f"  🏆 Best sellers: {sellers_task.id}")

    print("\n✅ Analytics tasks queued")


def example_7_monitoring():
    """
    Example 7: System health check

    Use case: Verify all services are operational
    """
    print("\n" + "="*60)
    print("Example 7: System Health Check")
    print("="*60 + "\n")

    print("Checking system health:")

    # Trigger health check
    task = health_check.delay()

    print(f"  ✅ Health check task: {task.id}")

    # Wait for result (quick check)
    try:
        result = task.get(timeout=10)

        if result.get("healthy"):
            print("\n✅ System is healthy")
        else:
            print("\n⚠️  System issues detected")

        print(f"\nServices status:")
        for service, status in result.get("services", {}).items():
            icon = "✅" if status.get("status") == "ok" else "❌"
            print(f"  {icon} {service}: {status.get('status')}")

    except Exception as e:
        print(f"\n❌ Health check failed: {e}")


def example_8_wait_for_result():
    """
    Example 8: Wait for task completion

    Use case: Synchronous operation (wait for result before continuing)
    """
    print("\n" + "="*60)
    print("Example 8: Wait for Task Result")
    print("="*60 + "\n")

    product_id = "1005001234567890"

    print(f"Importing product {product_id} and waiting for completion")

    # Start task
    task = import_product_by_id.delay(product_id, markup_percentage=40.0)

    print(f"Task ID: {task.id}")
    print("Waiting for result...")

    try:
        # Wait up to 2 minutes
        result = task.get(timeout=120)

        print("\n✅ Import complete!")
        print(f"  Shopify ID: {result.get('shopify_id')}")
        print(f"  TikTok ID: {result.get('tiktok_id')}")
        print(f"  Cost: ${result.get('base_price')}")
        print(f"  Price: ${result.get('selling_price')}")
        print(f"  Profit: ${result.get('margin')}")

    except Exception as e:
        print(f"\n❌ Task failed: {e}")


def example_9_check_task_status():
    """
    Example 9: Check status of running task

    Use case: Monitor a long-running task
    """
    print("\n" + "="*60)
    print("Example 9: Check Task Status")
    print("="*60 + "\n")

    # Start a task
    task = research_trending_products.delay()
    task_id = task.id

    print(f"Started research task: {task_id}")
    print("\nChecking status every 10 seconds:")

    # Poll status
    for i in range(6):  # Check for 1 minute
        status = task.state

        if status == "PENDING":
            print(f"  [{i*10}s] ⏳ Waiting to start...")
        elif status == "STARTED":
            print(f"  [{i*10}s] 🔄 Running...")
        elif status == "SUCCESS":
            print(f"  [{i*10}s] ✅ Complete!")
            result = task.result
            print(f"  Found {result.get('products_found', 0)} products")
            break
        elif status == "FAILURE":
            print(f"  [{i*10}s] ❌ Failed")
            break
        else:
            print(f"  [{i*10}s] Status: {status}")

        time.sleep(10)


def example_10_scheduled_tasks():
    """
    Example 10: View scheduled tasks

    Use case: See what automation is configured to run
    """
    print("\n" + "="*60)
    print("Example 10: Scheduled Tasks (Cron Jobs)")
    print("="*60 + "\n")

    from celery_app import app

    print("Configured scheduled tasks:\n")

    for task_name, task_config in app.conf.beat_schedule.items():
        task = task_config["task"]
        schedule = task_config["schedule"]

        print(f"📅 {task_name}")
        print(f"   Task: {task}")
        print(f"   Schedule: {schedule}")
        print()


def run_all_examples():
    """Run all examples (commented out by default)"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         StaticWaves Automation Examples                       ║
║         Automated Dropshipping Workflows                      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)

    print("\n⚠️  NOTE: Examples are demonstrations only")
    print("Uncomment the examples you want to run below\n")

    # Uncomment the examples you want to run:

    # example_1_manual_product_import()
    # example_2_bulk_import()
    # example_3_auto_research()
    # example_4_auto_fulfill_orders()
    # example_5_inventory_sync()
    # example_6_analytics()
    # example_7_monitoring()
    # example_8_wait_for_result()
    # example_9_check_task_status()
    example_10_scheduled_tasks()


if __name__ == "__main__":
    print("\nMake sure Celery workers are running:")
    print("  celery -A celery_app worker --loglevel=info\n")

    run_all_examples()

    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60 + "\n")

    print("Next steps:")
    print("  1. Uncomment examples you want to run")
    print("  2. Replace placeholder product IDs with real ones")
    print("  3. Monitor tasks: celery -A celery_app inspect active")
    print("  4. View results: celery -A celery_app inspect stats")
    print()

"""
Example: Automated Order Fulfillment
Automatically fulfill Shopify orders using AliExpress
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.aliexpress_service import AliExpressService
from services.shopify_service import ShopifyService
from loguru import logger


async def auto_fulfill_orders():
    """
    Monitor Shopify orders and automatically fulfill via AliExpress
    """

    ali_service = AliExpressService()
    shopify_service = ShopifyService()

    print("\n" + "="*60)
    print("🤖 Automated Order Fulfillment System")
    print("="*60 + "\n")

    # 1. Get unfulfilled orders from Shopify
    print("📦 Checking for unfulfilled orders...")

    try:
        orders = await shopify_service.list_orders(limit=50, status="unfulfilled")

        print(f"✅ Found {len(orders)} unfulfilled orders\n")

        if not orders:
            print("✨ No orders to fulfill. All caught up!")
            return

        # 2. Process each order
        for order in orders:
            order_id = order.get("id")
            order_number = order.get("order_number")
            customer_email = order.get("email")
            shipping_address = order.get("shipping_address")

            print(f"\n{'─'*60}")
            print(f"Processing Order #{order_number}")
            print(f"{'─'*60}")

            # 3. Get line items
            line_items = order.get("line_items", [])

            print(f"📋 Items: {len(line_items)}")

            # Prepare products for AliExpress
            ali_products = []

            for item in line_items:
                # Get AliExpress product ID from SKU or meta
                ali_product_id = item.get("sku")  # Assuming SKU = AliExpress ID

                if ali_product_id:
                    ali_products.append({
                        "product_id": ali_product_id,
                        "quantity": item.get("quantity"),
                        "variant_id": item.get("variant_id"),
                    })

                    print(f"  ✓ {item.get('title')} (Qty: {item.get('quantity')})")
                else:
                    print(f"  ⚠️  Skipping {item.get('title')} - No AliExpress ID")

            if not ali_products:
                print("⚠️  No AliExpress products found in order. Skipping.")
                continue

            # 4. Format shipping address
            if not shipping_address:
                print("❌ No shipping address. Cannot fulfill.")
                continue

            shipping_data = {
                "name": f"{shipping_address.get('first_name', '')} {shipping_address.get('last_name', '')}".strip(),
                "address1": shipping_address.get("address1"),
                "city": shipping_address.get("city"),
                "state": shipping_address.get("province"),
                "zip": shipping_address.get("zip"),
                "country": shipping_address.get("country_code"),
                "phone": shipping_address.get("phone", ""),
            }

            print(f"\n📬 Shipping to:")
            print(f"   {shipping_data['name']}")
            print(f"   {shipping_data['address1']}")
            print(f"   {shipping_data['city']}, {shipping_data['state']} {shipping_data['zip']}")

            # 5. Place order on AliExpress
            print("\n🚀 Placing order on AliExpress...")

            try:
                ali_order = await ali_service.place_order(
                    shopify_order_id=str(order_id),
                    products=ali_products,
                    shipping_address=shipping_data,
                )

                ali_order_id = ali_order.get("order_id")

                print(f"✅ AliExpress order placed: {ali_order_id}")

                # 6. Update Shopify with fulfillment
                tracking_number = ali_order.get("tracking_number", "PENDING")

                print(f"📦 Tracking: {tracking_number}")

                # Create fulfillment in Shopify
                await shopify_service.fulfill_order(str(order_id))

                print(f"✅ Shopify order #{order_number} marked as fulfilled")

                # 7. Notify customer (Shopify does this automatically)
                print(f"📧 Customer notification sent to {customer_email}")

            except Exception as e:
                logger.error(f"Failed to fulfill order {order_number}: {e}")
                print(f"❌ Error: {e}")
                continue

            # Rate limiting
            await asyncio.sleep(2)

        print("\n" + "="*60)
        print("✅ Order fulfillment complete!")
        print("="*60)

    except Exception as e:
        logger.error(f"Error in fulfillment process: {e}")
        print(f"\n❌ Error: {e}")


async def check_order_status(ali_order_id: str):
    """
    Check status of AliExpress order
    """

    ali_service = AliExpressService()

    print(f"\n🔍 Checking order status: {ali_order_id}\n")

    try:
        status = await ali_service.get_order_status(ali_order_id)

        print(f"Order Status: {status.get('order_status')}")
        print(f"Logistics Status: {status.get('logistics_status')}")
        print(f"Tracking Number: {status.get('tracking_number', 'N/A')}")
        print(f"Carrier: {status.get('carrier', 'N/A')}")
        print(f"Estimated Delivery: {status.get('estimated_delivery', 'N/A')}")

    except Exception as e:
        logger.error(f"Failed to get order status: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AliExpress Order Fulfillment")
    parser.add_argument(
        "--check-status",
        type=str,
        help="Check status of specific AliExpress order",
    )

    args = parser.parse_args()

    if args.check_status:
        asyncio.run(check_order_status(args.check_status))
    else:
        asyncio.run(auto_fulfill_orders())

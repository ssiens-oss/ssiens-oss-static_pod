"""
Example: AliExpress Product Research
Find winning products using the AliExpress API
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.aliexpress_service import AliExpressService
from loguru import logger


async def research_winning_products():
    """
    Research trending products with high profit potential
    """

    ali_service = AliExpressService()

    # Define search criteria
    niches = [
        "eco-friendly yoga mat",
        "wireless earbuds",
        "phone accessories",
        "fitness tracker",
        "portable blender",
    ]

    all_products = []

    for niche in niches:
        print(f"\n{'='*60}")
        print(f"🔍 Researching: {niche}")
        print('='*60)

        try:
            # Search products
            products = await ali_service.search_products(
                keywords=niche,
                min_price=5,
                max_price=50,
                min_orders=500,  # Proven sellers
                limit=10,
            )

            print(f"✅ Found {len(products)} products")

            # Filter for quality
            quality_products = []

            for product in products:
                # Extract metrics
                volume = product.get("volume", 0)
                eval_rate = float(product.get("evaluation_rate", "0%").rstrip("%"))
                price = float(product.get("target_sale_price", 0))

                # Calculate potential profit (40% markup)
                cost = price
                selling_price = round(cost * 1.4, 2)
                profit = round(selling_price - cost, 2)

                # Quality criteria
                if eval_rate > 95 and volume > 1000:
                    product_info = {
                        "niche": niche,
                        "title": product.get("product_title"),
                        "product_id": product.get("product_id"),
                        "cost": cost,
                        "selling_price": selling_price,
                        "profit": profit,
                        "profit_margin": f"{((profit/selling_price)*100):.1f}%",
                        "orders": volume,
                        "rating": f"{eval_rate}%",
                        "url": product.get("product_detail_url"),
                    }

                    quality_products.append(product_info)

            # Sort by profit
            quality_products.sort(key=lambda x: x["profit"], reverse=True)

            # Display top 3
            print(f"\n📊 Top 3 Winners in '{niche}':\n")

            for i, p in enumerate(quality_products[:3], 1):
                print(f"{i}. {p['title'][:50]}...")
                print(f"   💰 Cost: ${p['cost']} → Sell: ${p['selling_price']} (Profit: ${p['profit']})")
                print(f"   📦 Orders: {p['orders']:,} | ⭐ Rating: {p['rating']}")
                print(f"   🔗 {p['url']}\n")

            all_products.extend(quality_products)

        except Exception as e:
            logger.error(f"Error researching {niche}: {e}")

        # Rate limiting
        await asyncio.sleep(2)

    # Final summary
    print("\n" + "="*60)
    print("📈 RESEARCH SUMMARY")
    print("="*60)

    if all_products:
        # Sort all products by profit
        all_products.sort(key=lambda x: x["profit"], reverse=True)

        print(f"\n✅ Total quality products found: {len(all_products)}")
        print(f"\n🏆 TOP 5 BEST PROFIT MARGINS:\n")

        for i, p in enumerate(all_products[:5], 1):
            print(f"{i}. {p['title'][:50]}...")
            print(f"   Niche: {p['niche']}")
            print(f"   Profit: ${p['profit']} ({p['profit_margin']})")
            print(f"   Orders: {p['orders']:,} | Rating: {p['rating']}")
            print()

        # Calculate potential monthly revenue
        avg_daily_orders = 10  # Conservative estimate
        avg_profit = sum(p["profit"] for p in all_products[:5]) / 5
        monthly_revenue = avg_daily_orders * avg_profit * 30

        print(f"💵 POTENTIAL MONTHLY REVENUE:")
        print(f"   Average profit per product: ${avg_profit:.2f}")
        print(f"   If selling {avg_daily_orders} units/day: ${monthly_revenue:,.2f}/month")

    else:
        print("\n⚠️  No quality products found. Try different niches.")

    print("\n" + "="*60)


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         AliExpress Product Research Tool                      ║
║         Finding Winning Dropshipping Products                 ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)

    asyncio.run(research_winning_products())

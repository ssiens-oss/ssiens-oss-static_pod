"""
Payout Engine
Revenue sharing for creators
"""

import os
import json
from typing import Dict, List
from collections import defaultdict


class PayoutEngine:
    """Manages creator payouts"""

    def __init__(self, data_dir: str = "marketplace_data"):
        self.data_dir = data_dir
        self.revenue_share = 0.60  # 60% to creator, 40% to platform

    def calculate_earnings(self, creator_id: str) -> Dict:
        """
        Calculate creator earnings

        Args:
            creator_id: Creator ID

        Returns:
            Earnings breakdown
        """
        purchases_file = os.path.join(self.data_dir, "purchases.json")

        if not os.path.exists(purchases_file):
            return {
                "creator_id": creator_id,
                "total_revenue": 0,
                "creator_share": 0,
                "platform_share": 0,
                "sales_count": 0
            }

        with open(purchases_file, 'r') as f:
            purchases = json.load(f)

        # Load assets to get creator info
        assets_file = os.path.join(self.data_dir, "assets.json")
        with open(assets_file, 'r') as f:
            assets_data = json.load(f)

        # Map asset_id -> creator_id
        asset_creators = {a["id"]: a["creator_id"] for a in assets_data}

        # Calculate earnings for this creator
        total_revenue = 0
        sales_count = 0

        for purchase in purchases:
            asset_id = purchase["asset_id"]
            if asset_creators.get(asset_id) == creator_id:
                total_revenue += purchase["price_paid"]
                sales_count += 1

        creator_share = int(total_revenue * self.revenue_share)
        platform_share = total_revenue - creator_share

        return {
            "creator_id": creator_id,
            "total_revenue": total_revenue,
            "creator_share": creator_share,
            "platform_share": platform_share,
            "sales_count": sales_count
        }

    def process_payout(
        self,
        creator_id: str,
        method: str = "stripe"
    ) -> Dict:
        """
        Process payout to creator

        Args:
            creator_id: Creator to pay
            method: Payout method (stripe, paypal, etc.)

        Returns:
            Payout result
        """
        earnings = self.calculate_earnings(creator_id)

        if earnings["creator_share"] == 0:
            return {
                "success": False,
                "error": "No earnings to payout"
            }

        print(f"\n💰 Processing payout for {creator_id}...")
        print(f"  Amount: {earnings['creator_share']} tokens")
        print(f"  Method: {method}")

        # TODO: Integrate with Stripe Connect or PayPal
        # For now, record payout

        payout_record = {
            "creator_id": creator_id,
            "amount": earnings["creator_share"],
            "method": method,
            "status": "pending",
            "timestamp": self._timestamp()
        }

        self._record_payout(payout_record)

        print(f"✓ Payout initiated")

        return {
            "success": True,
            "payout_id": f"payout_{int(self._timestamp())}",
            "amount": earnings["creator_share"],
            "status": "pending"
        }

    def _record_payout(self, record: Dict):
        """Record payout transaction"""
        payouts_file = os.path.join(self.data_dir, "payouts.json")

        payouts = []
        if os.path.exists(payouts_file):
            with open(payouts_file, 'r') as f:
                payouts = json.load(f)

        payouts.append(record)

        with open(payouts_file, 'w') as f:
            json.dump(payouts, f, indent=2)

    def _timestamp(self) -> float:
        """Get timestamp"""
        import time
        return time.time()

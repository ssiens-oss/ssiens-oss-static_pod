"""POD-specific orchestrator integrating with existing pipeline."""

import os
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from antigravity.orchestrator import AntigravityOrchestrator
from antigravity.pod.offers import OfferFactory, compare_offers
from antigravity.pod.risk import assess_pod_risk, calculate_risk_score
from antigravity.models import PODOffer
from antigravity.integrations.slack import notify_slack, notify_slack_rich
from antigravity.integrations.email import notify_email
from antigravity.memory.provenance import record_provenance
from antigravity.memory.notion import log_decision_to_notion


class PODOrchestrator:
    """
    POD-specific orchestrator that combines Antigravity intelligence
    with existing Printify/Shopify pipeline.
    """

    def __init__(
        self,
        dry_run: bool = False,
        require_human: bool = True,
        enable_ab_testing: bool = True,
        default_brand: str = "StaticWaves",
    ):
        """
        Initialize POD orchestrator.

        Args:
            dry_run: If True, plan but don't execute
            require_human: If True, require human approval for publishing
            enable_ab_testing: If True, generate multiple variants
            default_brand: Default brand name
        """
        self.dry_run = dry_run
        self.require_human = require_human

        # Initialize Antigravity core
        self.antigravity = AntigravityOrchestrator(
            dry_run=dry_run,
            require_human=require_human,
            use_memory=True,
        )

        # Initialize offer factory
        self.offer_factory = OfferFactory(
            default_brand=default_brand,
            enable_ab_testing=enable_ab_testing,
        )

    def process_design(
        self,
        design_path: str,
        product_type: str = "hoodie",
        brand: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Process a new design through the intelligent pipeline.

        This is the main entry point that:
        1. Generates offer variants
        2. Assesses risks
        3. Consults AI models for decision-making
        4. Prepares for publishing

        Args:
            design_path: Path to design file
            product_type: Type of product (tshirt, hoodie)
            brand: Brand name

        Returns:
            Dict with processing results, or None if blocked
        """
        design_id = str(uuid.uuid4())[:8]

        print(f"\n{'='*70}")
        print(f"🎨 POD DESIGN PROCESSING")
        print(f"{'='*70}")
        print(f"Design: {design_path}")
        print(f"Product: {product_type}")
        print(f"Brand: {brand or 'StaticWaves'}")
        print(f"ID: {design_id}")
        print(f"{'='*70}\n")

        # Check if design file exists
        if not Path(design_path).exists():
            notify_slack(f"❌ Design file not found: {design_path}")
            return None

        # Step 1: Generate offers
        print("📋 Step 1: Generating offer variants...")
        offers = self.offer_factory.generate_variants(
            product_type=product_type,
            count=3,
            brand=brand,
        )

        comparison = compare_offers(offers)
        print(f"   Generated {comparison['count']} variants")
        print(f"   Price range: ${comparison['price_range']['min']:.2f} - ${comparison['price_range']['max']:.2f}")

        # Select best offer (for now, use first one)
        selected_offer = offers[0]
        print(f"\n📌 Selected offer:")
        print(f"   Title: {selected_offer.headline}")
        print(f"   Price: ${selected_offer.price:.2f}")
        print(f"   Tags: {', '.join(selected_offer.tags[:5])}")

        # Step 2: Risk assessment
        print(f"\n🔍 Step 2: Risk assessment...")
        risk_assessment = calculate_risk_score(design_path, selected_offer)

        print(f"   Risk Level: {risk_assessment['level'].upper()}")
        print(f"   Risk Score: {risk_assessment['score']}/100")

        if risk_assessment['warnings']:
            print(f"   Warnings:")
            for warning in risk_assessment['warnings']:
                print(f"     - {warning}")

        # Block if high risk
        if not risk_assessment['is_safe']:
            print(f"\n🛑 BLOCKED: Safety check failed")
            notify_slack_rich(
                title="🛑 POD Design Blocked",
                text=f"Design: {design_path}\nReason: Safety check failed",
                color="#ff0000",
                fields=[
                    {"title": "Risk Level", "value": risk_assessment['level']},
                    {"title": "Warnings", "value": str(len(risk_assessment['warnings']))},
                ]
            )
            return None

        # Step 3: AI decision-making
        print(f"\n🧠 Step 3: Consulting AI models...")

        task = (
            f"Evaluate POD product launch:\n"
            f"Product: {product_type}\n"
            f"Title: {selected_offer.headline}\n"
            f"Price: ${selected_offer.price}\n"
            f"Brand: {selected_offer.brand}\n"
            f"Risk Level: {risk_assessment['level']}\n\n"
            f"Should we proceed with this launch?"
        )

        plan = self.antigravity.execute(task)

        if not plan:
            print(f"\n❌ AI decision: Do not proceed")
            return None

        print(f"\n✅ AI decision: Approved for launch")

        # Step 4: Prepare metadata for publishing
        print(f"\n📦 Step 4: Preparing for publish...")

        result = {
            "design_id": design_id,
            "design_path": design_path,
            "product_type": product_type,
            "offer": selected_offer.dict(),
            "risk_assessment": risk_assessment,
            "ai_decision": {
                "approved": True,
                "confidence": plan.metadata.get("confidence", 0.0),
                "consensus": plan.metadata.get("consensus", ""),
            },
            "variants": [o.dict() for o in offers],
            "ready_for_publish": True,
        }

        # Log to Notion
        log_decision_to_notion(
            title=f"POD Design: {selected_offer.headline}",
            summary=(
                f"Product: {product_type}\n"
                f"Price: ${selected_offer.price}\n"
                f"Risk: {risk_assessment['level']}\n"
                f"AI Confidence: {plan.metadata.get('confidence', 0.0):.2%}"
            ),
            fields={
                "Product Type": product_type,
                "Price": selected_offer.price,
                "Risk Level": risk_assessment['level'],
            }
        )

        # Send success notification
        notify_slack_rich(
            title="✅ POD Design Approved",
            text=selected_offer.headline,
            color="#36a64f",
            fields=[
                {"title": "Product", "value": product_type},
                {"title": "Price", "value": f"${selected_offer.price}"},
                {"title": "Risk", "value": risk_assessment['level']},
                {"title": "AI Confidence", "value": f"{plan.metadata.get('confidence', 0.0):.1%}"},
            ]
        )

        print(f"\n✅ Processing complete!")
        print(f"   Design ID: {design_id}")
        print(f"   Ready for publish: {result['ready_for_publish']}")

        return result

    def batch_process(
        self,
        design_paths: List[str],
        product_type: str = "hoodie",
    ) -> List[Dict[str, Any]]:
        """
        Process multiple designs in batch.

        Args:
            design_paths: List of design file paths
            product_type: Product type

        Returns:
            List of processing results
        """
        print(f"\n🔄 Batch processing {len(design_paths)} designs...")

        results = []
        for i, path in enumerate(design_paths, 1):
            print(f"\n--- Processing {i}/{len(design_paths)} ---")

            result = self.process_design(path, product_type)
            if result:
                results.append(result)

        print(f"\n✅ Batch complete: {len(results)}/{len(design_paths)} approved")

        return results

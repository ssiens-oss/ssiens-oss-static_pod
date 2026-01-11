"""
Zazzle-specific POD orchestrator with Antigravity intelligence.

This module extends the base POD orchestrator to handle Zazzle-specific
operations while maintaining all the AI decision-making, risk assessment,
and verification capabilities.
"""

import uuid
from typing import Optional, Dict, Any, List
from pathlib import Path

from antigravity.orchestrator import AntigravityOrchestrator
from antigravity.pod.offers import OfferFactory
from antigravity.pod.risk import assess_pod_risk, calculate_risk_score
from antigravity.types import PODOffer
from antigravity.integrations.slack import notify_slack, notify_slack_rich
from antigravity.integrations.email import notify_email
from antigravity.integrations.zazzle import ZazzleClient, create_zazzle_product, ZAZZLE_TEMPLATES
from antigravity.memory.provenance import record_provenance
from antigravity.memory.notion import log_decision_to_notion


class ZazzlePODOrchestrator:
    """
    Zazzle-specific POD orchestrator with full Antigravity intelligence.

    This orchestrator:
    1. Generates multiple offer variants (A/B testing)
    2. Assesses risks (copyright, pricing, content)
    3. Consults AI models (GPT, Claude, Grok)
    4. Detects uncertainty and escalates when needed
    5. Publishes to Zazzle
    6. Verifies execution
    7. Learns from outcomes
    """

    def __init__(
        self,
        dry_run: bool = False,
        require_human: bool = True,
        enable_ab_testing: bool = True,
        default_brand: str = "StaticWaves",
        default_template: str = "tshirt_basic",
    ):
        """
        Initialize Zazzle POD orchestrator.

        Args:
            dry_run: If True, plan but don't execute
            require_human: If True, require human approval
            enable_ab_testing: If True, generate multiple variants
            default_brand: Default brand name
            default_template: Default Zazzle product template
        """
        self.dry_run = dry_run
        self.require_human = require_human
        self.default_template = default_template

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

        # Initialize Zazzle client
        try:
            self.zazzle_client = ZazzleClient()
            self.zazzle_available = True
        except Exception as e:
            print(f"Warning: Zazzle client not available: {e}")
            self.zazzle_available = False

    def process_design_for_zazzle(
        self,
        design_path: str,
        product_type: str = "tshirt",
        brand: Optional[str] = None,
        template: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Process a design for Zazzle with full AI intelligence.

        Args:
            design_path: Path to design file
            product_type: Zazzle product type (tshirt, hoodie, poster, etc.)
            brand: Brand name
            template: Zazzle template to use

        Returns:
            Dict with processing results, or None if blocked
        """
        design_id = str(uuid.uuid4())[:8]

        print(f"\n{'='*70}")
        print(f"🎨 ZAZZLE POD PROCESSING")
        print(f"{'='*70}")
        print(f"Design: {design_path}")
        print(f"Product: {product_type}")
        print(f"Brand: {brand or 'StaticWaves'}")
        print(f"Template: {template or self.default_template}")
        print(f"ID: {design_id}")
        print(f"{'='*70}\n")

        # Check if design file exists
        if not Path(design_path).exists():
            notify_slack(f"❌ Design file not found: {design_path}")
            return None

        # Get Zazzle template
        template_name = template or self.default_template
        try:
            zazzle_template = ZAZZLE_TEMPLATES.get(
                template_name,
                ZAZZLE_TEMPLATES["tshirt_basic"]
            )
        except Exception as e:
            print(f"Warning: Could not load template {template_name}, using default")
            zazzle_template = ZAZZLE_TEMPLATES["tshirt_basic"]

        # Step 1: Generate offers
        print("📋 Step 1: Generating Zazzle offer variants...")

        # Map product type to offer factory type
        offer_product_type = product_type
        if product_type not in ["tshirt", "hoodie"]:
            # For Zazzle-specific products, use closest match
            offer_product_type = "tshirt"

        offers = self.offer_factory.generate_variants(
            product_type=offer_product_type,
            count=3,
            brand=brand,
        )

        # Adjust pricing based on Zazzle template
        base_price = zazzle_template.get("price", 19.99)
        for i, offer in enumerate(offers):
            offer.price = base_price + (i * 5.0)  # Variant pricing

        print(f"   Generated {len(offers)} variants")
        print(f"   Price range: ${min(o.price for o in offers):.2f} - ${max(o.price for o in offers):.2f}")

        # Select best offer
        selected_offer = offers[0]
        print(f"\n📌 Selected offer:")
        print(f"   Title: {selected_offer.headline}")
        print(f"   Price: ${selected_offer.price:.2f}")
        print(f"   Royalty: {zazzle_template.get('royalty_percentage', 10.0)}%")

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
                title="🛑 Zazzle Design Blocked",
                text=f"Design: {design_path}\nReason: Safety check failed",
                color="#ff0000",
                fields=[
                    {"title": "Risk Level", "value": risk_assessment['level']},
                    {"title": "Product Type", "value": product_type},
                ]
            )
            return None

        # Step 3: AI decision-making
        print(f"\n🧠 Step 3: Consulting AI models...")

        task = (
            f"Evaluate Zazzle POD product launch:\n"
            f"Product: {product_type}\n"
            f"Title: {selected_offer.headline}\n"
            f"Price: ${selected_offer.price}\n"
            f"Royalty: {zazzle_template.get('royalty_percentage', 10.0)}%\n"
            f"Brand: {selected_offer.brand}\n"
            f"Platform: Zazzle\n"
            f"Risk Level: {risk_assessment['level']}\n\n"
            f"Should we proceed with this Zazzle launch?"
        )

        plan = self.antigravity.execute(task)

        if not plan:
            print(f"\n❌ AI decision: Do not proceed")
            return None

        print(f"\n✅ AI decision: Approved for Zazzle launch")

        # Step 4: Publish to Zazzle (if not dry run)
        zazzle_product = None

        if not self.dry_run and self.zazzle_available:
            print(f"\n📤 Step 4: Publishing to Zazzle...")

            try:
                zazzle_product = create_zazzle_product(
                    image_path=design_path,
                    title=selected_offer.headline,
                    description=selected_offer.description,
                    product_type=product_type,
                    price=selected_offer.price,
                    tags=selected_offer.tags,
                    royalty_percentage=zazzle_template.get("royalty_percentage", 10.0),
                )

                print(f"   ✅ Published to Zazzle")
                print(f"   Product ID: {zazzle_product.get('product_id')}")
                print(f"   URL: {zazzle_product.get('url')}")

            except Exception as e:
                print(f"   ❌ Zazzle publishing failed: {e}")
                notify_slack(f"❌ Zazzle publishing failed: {e}")
                return None
        else:
            print(f"\n📦 Step 4: Preparing for Zazzle publish (dry run)...")

        # Step 5: Prepare result
        result = {
            "design_id": design_id,
            "design_path": design_path,
            "product_type": product_type,
            "platform": "zazzle",
            "template": template_name,
            "offer": selected_offer.dict(),
            "risk_assessment": risk_assessment,
            "ai_decision": {
                "approved": True,
                "confidence": plan.metadata.get("confidence", 0.0),
                "consensus": plan.metadata.get("consensus", ""),
            },
            "variants": [o.dict() for o in offers],
            "zazzle_product": zazzle_product,
            "ready_for_publish": True,
        }

        # Log to Notion
        log_decision_to_notion(
            title=f"Zazzle POD: {selected_offer.headline}",
            summary=(
                f"Product: {product_type}\n"
                f"Price: ${selected_offer.price}\n"
                f"Royalty: {zazzle_template.get('royalty_percentage', 10.0)}%\n"
                f"Risk: {risk_assessment['level']}\n"
                f"AI Confidence: {plan.metadata.get('confidence', 0.0):.2%}"
            ),
            fields={
                "Platform": "Zazzle",
                "Product Type": product_type,
                "Price": selected_offer.price,
                "Risk Level": risk_assessment['level'],
            }
        )

        # Send success notification
        notify_slack_rich(
            title="✅ Zazzle Product Approved",
            text=selected_offer.headline,
            color="#36a64f",
            fields=[
                {"title": "Platform", "value": "Zazzle"},
                {"title": "Product", "value": product_type},
                {"title": "Price", "value": f"${selected_offer.price}"},
                {"title": "Royalty", "value": f"{zazzle_template.get('royalty_percentage', 10.0)}%"},
                {"title": "Risk", "value": risk_assessment['level']},
                {"title": "AI Confidence", "value": f"{plan.metadata.get('confidence', 0.0):.1%}"},
            ]
        )

        print(f"\n✅ Zazzle processing complete!")
        print(f"   Design ID: {design_id}")
        print(f"   Ready for publish: {result['ready_for_publish']}")

        if zazzle_product:
            print(f"   Zazzle URL: {zazzle_product.get('url')}")

        return result

    def batch_process_for_zazzle(
        self,
        design_paths: List[str],
        product_type: str = "tshirt",
        template: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process multiple designs for Zazzle in batch.

        Args:
            design_paths: List of design file paths
            product_type: Zazzle product type
            template: Zazzle template to use

        Returns:
            List of processing results
        """
        print(f"\n🔄 Batch processing {len(design_paths)} designs for Zazzle...")

        results = []
        for i, path in enumerate(design_paths, 1):
            print(f"\n--- Processing {i}/{len(design_paths)} ---")

            result = self.process_design_for_zazzle(
                path,
                product_type=product_type,
                template=template,
            )

            if result:
                results.append(result)

        print(f"\n✅ Batch complete: {len(results)}/{len(design_paths)} approved for Zazzle")

        return results

    def create_multiple_product_types(
        self,
        design_path: str,
        product_types: List[str],
        brand: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Create the same design across multiple Zazzle product types.

        This is useful for creating a full product line from one design.

        Args:
            design_path: Path to design file
            product_types: List of Zazzle product types
            brand: Brand name

        Returns:
            List of results for each product type
        """
        print(f"\n🎯 Creating {len(product_types)} Zazzle product types from design...")

        results = []

        for product_type in product_types:
            print(f"\n--- Creating {product_type} ---")

            result = self.process_design_for_zazzle(
                design_path=design_path,
                product_type=product_type,
                brand=brand,
            )

            if result:
                results.append(result)

        print(f"\n✅ Created {len(results)}/{len(product_types)} product types")

        return results

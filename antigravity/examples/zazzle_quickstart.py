#!/usr/bin/env python3
"""
Zazzle Quick Start Example

This example shows how to quickly integrate Zazzle into your POD pipeline
with full Antigravity intelligence.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from antigravity.pod.zazzle_orchestrator import ZazzlePODOrchestrator
from antigravity.integrations.zazzle import (
    ZazzleClient,
    create_zazzle_product,
    ZAZZLE_TEMPLATES,
)


def example_1_simple_upload():
    """Example 1: Simple Zazzle upload without AI orchestration."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Zazzle Upload")
    print("="*70 + "\n")

    # Quick upload - no AI decision-making
    product = create_zazzle_product(
        image_path="design.png",  # Replace with your design
        title="StaticWaves T-Shirt",
        description="Limited edition AI-generated streetwear design",
        product_type="tshirt",
        price=24.99,
        tags=["streetwear", "ai", "limited", "staticwaves"],
        royalty_percentage=15.0,
    )

    print(f"✅ Product created!")
    print(f"   Product ID: {product['product_id']}")
    print(f"   URL: {product['url']}")
    print(f"   Price: ${product['price']}")


def example_2_full_ai_orchestration():
    """Example 2: Full AI orchestration with Antigravity."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Full AI Orchestration")
    print("="*70 + "\n")

    # Initialize orchestrator with full AI intelligence
    orchestrator = ZazzlePODOrchestrator(
        dry_run=True,  # Set to False when ready
        require_human=True,
        enable_ab_testing=True,
        default_brand="StaticWaves",
    )

    # Process design with:
    # - Multi-model AI consultation (GPT + Claude)
    # - Risk assessment
    # - Uncertainty detection
    # - Human approval
    # - Verification
    # - Memory storage

    result = orchestrator.process_design_for_zazzle(
        design_path="design.png",  # Replace with your design
        product_type="hoodie",
        brand="StaticWaves",
        template="hoodie_premium",
    )

    if result and result['ready_for_publish']:
        print(f"\n✅ Design approved by AI!")
        print(f"   Confidence: {result['ai_decision']['confidence']:.1%}")
        print(f"   Risk Level: {result['risk_assessment']['level']}")

        if result.get('zazzle_product'):
            print(f"   Zazzle URL: {result['zazzle_product']['url']}")


def example_3_batch_processing():
    """Example 3: Batch process multiple designs."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Batch Processing")
    print("="*70 + "\n")

    orchestrator = ZazzlePODOrchestrator(
        dry_run=True,
        require_human=False,  # Auto-approve for batch
        default_brand="StaticWaves",
    )

    # Process multiple designs
    designs = [
        "design1.png",
        "design2.png",
        "design3.png",
    ]  # Replace with your designs

    # Filter to existing files
    existing_designs = [d for d in designs if Path(d).exists()]

    if existing_designs:
        results = orchestrator.batch_process_for_zazzle(
            design_paths=existing_designs,
            product_type="tshirt",
            template="tshirt_basic",
        )

        print(f"\n✅ Batch complete!")
        print(f"   Processed: {len(results)}/{len(existing_designs)}")
    else:
        print("⚠️  No design files found. Update paths in the script.")


def example_4_multi_product_types():
    """Example 4: Create multiple product types from one design."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Multi-Product Line")
    print("="*70 + "\n")

    orchestrator = ZazzlePODOrchestrator(
        dry_run=True,
        require_human=False,
        default_brand="StaticWaves",
    )

    # Create a full product line from one design
    results = orchestrator.create_multiple_product_types(
        design_path="design.png",  # Replace with your design
        product_types=[
            "tshirt",
            "hoodie",
            "poster",
            "mug",
            "sticker",
        ],
        brand="StaticWaves",
    )

    print(f"\n✅ Product line created!")
    print(f"   Created {len(results)} product types:")

    for result in results:
        product_type = result['product_type']
        offer = result['offer']
        print(f"   • {product_type}: ${offer['price']}")


def example_5_list_templates():
    """Example 5: List available Zazzle templates."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Available Templates")
    print("="*70 + "\n")

    print("Available Zazzle Templates:\n")

    for template_name, template_config in ZAZZLE_TEMPLATES.items():
        print(f"📋 {template_name}")
        print(f"   Product: {template_config['product_type']}")
        print(f"   Price: ${template_config['price']}")
        print(f"   Royalty: {template_config['royalty_percentage']}%")
        print()


def example_6_verify_product():
    """Example 6: Verify a Zazzle product."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Product Verification")
    print("="*70 + "\n")

    from antigravity.verification import verify_zazzle_product

    # Verify product is live on Zazzle
    result = verify_zazzle_product(
        product_id="your_product_id",  # Replace with actual product ID
        expected_title="StaticWaves Hoodie",
        expected_price=44.99,
        store_id=os.environ.get("ZAZZLE_STORE_ID"),
    )

    if result['success']:
        print("✅ Product verified!")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Price: {result.get('price', 'N/A')}")
    else:
        print("❌ Verification failed")
        for check in result.get('checks_failed', []):
            print(f"   • {check}")


def main():
    """Run all examples."""
    print("\n" + "🎨 ZAZZLE POD INTEGRATION - QUICK START EXAMPLES")
    print("="*70)

    # Check configuration
    if not os.environ.get("ZAZZLE_ASSOCIATE_ID") and not os.environ.get("ZAZZLE_API_KEY"):
        print("\n⚠️  WARNING: Zazzle credentials not configured")
        print("   Set ZAZZLE_ASSOCIATE_ID or ZAZZLE_API_KEY in .env")
        print("   Examples will run in demo mode.\n")

    try:
        # Run examples
        example_5_list_templates()

        print("\n💡 To run other examples:")
        print("   1. Update design paths in the script")
        print("   2. Configure Zazzle credentials in .env")
        print("   3. Uncomment the examples you want to run")
        print()

        # Uncomment to run examples:
        # example_1_simple_upload()
        # example_2_full_ai_orchestration()
        # example_3_batch_processing()
        # example_4_multi_product_types()
        # example_6_verify_product()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print("✅ Quick start examples complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

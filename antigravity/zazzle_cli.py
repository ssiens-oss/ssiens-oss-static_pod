"""Command-line interface for Zazzle POD operations."""

import os
import argparse
from pathlib import Path
from antigravity.pod.zazzle_orchestrator import ZazzlePODOrchestrator
from antigravity.watcher import watch_and_process


def run_single_design(args):
    """Process a single design for Zazzle."""
    print("\n🎨 Processing design for Zazzle")

    orchestrator = ZazzlePODOrchestrator(
        dry_run=args.dry_run,
        require_human=not args.auto_approve,
        enable_ab_testing=args.ab_testing,
        default_brand=args.brand,
        default_template=args.template,
    )

    result = orchestrator.process_design_for_zazzle(
        design_path=args.design,
        product_type=args.product_type,
        brand=args.brand,
        template=args.template,
    )

    if result:
        print(f"\n✅ Design processed for Zazzle")
        print(f"   Design ID: {result['design_id']}")
        print(f"   Ready for publish: {result['ready_for_publish']}")

        if result.get('zazzle_product'):
            zazzle_product = result['zazzle_product']
            print(f"   Zazzle Product ID: {zazzle_product.get('product_id')}")
            print(f"   Zazzle URL: {zazzle_product.get('url')}")
    else:
        print(f"\n❌ Design processing failed")


def run_batch(args):
    """Process multiple designs for Zazzle."""
    print(f"\n📦 Batch processing for Zazzle from: {args.directory}")

    orchestrator = ZazzlePODOrchestrator(
        dry_run=args.dry_run,
        require_human=not args.auto_approve,
        default_brand=args.brand,
        default_template=args.template,
    )

    # Find all image files
    design_dir = Path(args.directory)
    image_extensions = ['.png', '.jpg', '.jpeg', '.webp']

    design_files = []
    for ext in image_extensions:
        design_files.extend(design_dir.glob(f"*{ext}"))

    if not design_files:
        print(f"   No image files found")
        return

    print(f"   Found {len(design_files)} designs")

    results = orchestrator.batch_process_for_zazzle(
        design_paths=[str(f) for f in design_files],
        product_type=args.product_type,
        template=args.template,
    )

    print(f"\n📊 Batch complete:")
    print(f"   Processed: {len(results)}/{len(design_files)}")


def run_multi_product(args):
    """Create multiple product types from one design."""
    print(f"\n🎯 Creating multiple Zazzle product types")

    orchestrator = ZazzlePODOrchestrator(
        dry_run=args.dry_run,
        require_human=not args.auto_approve,
        default_brand=args.brand,
    )

    # Parse product types
    product_types = args.product_types.split(',')

    results = orchestrator.create_multiple_product_types(
        design_path=args.design,
        product_types=product_types,
        brand=args.brand,
    )

    print(f"\n📊 Multi-product creation complete:")
    print(f"   Created: {len(results)}/{len(product_types)} types")

    for result in results:
        product_type = result['product_type']
        zazzle_product = result.get('zazzle_product', {})
        url = zazzle_product.get('url', 'N/A')
        print(f"   ✅ {product_type}: {url}")


def run_watcher(args):
    """Watch directory for new designs."""
    print(f"\n👁️  Starting Zazzle watcher")
    print(f"   Directory: {args.watch_dir}")
    print(f"   Product type: {args.product_type}")
    print(f"   Template: {args.template}")

    orchestrator = ZazzlePODOrchestrator(
        dry_run=args.dry_run,
        require_human=not args.auto_approve,
        default_brand=args.brand,
        default_template=args.template,
    )

    def process_callback(file_path: str):
        """Callback for each new file."""
        orchestrator.process_design_for_zazzle(
            design_path=file_path,
            product_type=args.product_type,
            template=args.template,
        )

    watch_and_process(
        watch_dir=args.watch_dir,
        callback=process_callback,
        run_once=args.run_once,
    )


def main():
    """Main CLI entry point for Zazzle operations."""
    parser = argparse.ArgumentParser(
        description="Zazzle POD Orchestration with Antigravity AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single design
  python -m antigravity.zazzle_cli design path/to/design.png --product-type tshirt

  # Process with specific template
  python -m antigravity.zazzle_cli design design.png --template hoodie_premium

  # Create multiple product types
  python -m antigravity.zazzle_cli multi design.png --product-types tshirt,hoodie,mug

  # Process directory
  python -m antigravity.zazzle_cli batch --directory /path/to/designs

  # Watch directory
  python -m antigravity.zazzle_cli watch --watch-dir /data/comfyui/output

Environment Variables:
  ZAZZLE_ASSOCIATE_ID       - Zazzle Associate ID
  ZAZZLE_API_KEY            - Zazzle API key
  ZAZZLE_STORE_ID           - Your Zazzle store ID
  ZAZZLE_DEFAULT_TEMPLATE   - Default product template
        """
    )

    # Common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan but don't execute"
    )
    parent_parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Skip human approval"
    )
    parent_parser.add_argument(
        "--brand",
        default="StaticWaves",
        help="Brand name (default: StaticWaves)"
    )
    parent_parser.add_argument(
        "--product-type",
        choices=["tshirt", "hoodie", "poster", "mug", "sticker",
                 "phone_case", "tote_bag", "pillow", "mousepad", "keychain"],
        default="tshirt",
        help="Zazzle product type (default: tshirt)"
    )
    parent_parser.add_argument(
        "--template",
        choices=["tshirt_basic", "tshirt_premium", "hoodie_basic",
                 "hoodie_premium", "poster", "mug"],
        help="Zazzle product template (optional)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Single design command
    design_parser = subparsers.add_parser(
        "design",
        parents=[parent_parser],
        help="Process a single design for Zazzle"
    )
    design_parser.add_argument("design", help="Path to design file")
    design_parser.add_argument(
        "--ab-testing",
        action="store_true",
        help="Generate A/B testing variants"
    )

    # Multi-product command
    multi_parser = subparsers.add_parser(
        "multi",
        parents=[parent_parser],
        help="Create multiple product types from one design"
    )
    multi_parser.add_argument("design", help="Path to design file")
    multi_parser.add_argument(
        "--product-types",
        required=True,
        help="Comma-separated list of product types (e.g., tshirt,hoodie,mug)"
    )

    # Batch command
    batch_parser = subparsers.add_parser(
        "batch",
        parents=[parent_parser],
        help="Process multiple designs for Zazzle"
    )
    batch_parser.add_argument(
        "--directory",
        required=True,
        help="Directory containing designs"
    )

    # Watch command
    watch_parser = subparsers.add_parser(
        "watch",
        parents=[parent_parser],
        help="Watch directory for new designs"
    )
    watch_parser.add_argument(
        "--watch-dir",
        default=os.environ.get("COMFYUI_OUTPUT_DIR", "/data/comfyui/output"),
        help="Directory to watch"
    )
    watch_parser.add_argument(
        "--run-once",
        action="store_true",
        help="Process existing files and exit (don't watch)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Route to appropriate handler
    if args.command == "design":
        run_single_design(args)
    elif args.command == "multi":
        run_multi_product(args)
    elif args.command == "batch":
        run_batch(args)
    elif args.command == "watch":
        run_watcher(args)


if __name__ == "__main__":
    main()

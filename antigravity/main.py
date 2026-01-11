"""Main entry point for Antigravity POD system."""

import os
import argparse
from pathlib import Path
from antigravity.pod.orchestrator import PODOrchestrator
from antigravity.watcher import watch_and_process
from antigravity.gateway_bridge import integrate_with_gateway


def run_single_design(args):
    """Process a single design file."""
    print("\n🎨 Processing single design")

    orchestrator = PODOrchestrator(
        dry_run=args.dry_run,
        require_human=not args.auto_approve,
        enable_ab_testing=args.ab_testing,
        default_brand=args.brand,
    )

    result = orchestrator.process_design(
        design_path=args.design,
        product_type=args.product_type,
        brand=args.brand,
    )

    if result:
        print(f"\n✅ Design processed successfully")
        print(f"   Design ID: {result['design_id']}")
        print(f"   Ready for publish: {result['ready_for_publish']}")
    else:
        print(f"\n❌ Design processing failed")


def run_batch(args):
    """Process multiple design files."""
    print(f"\n📦 Batch processing from: {args.directory}")

    orchestrator = PODOrchestrator(
        dry_run=args.dry_run,
        require_human=not args.auto_approve,
        default_brand=args.brand,
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

    results = orchestrator.batch_process(
        design_paths=[str(f) for f in design_files],
        product_type=args.product_type,
    )

    print(f"\n📊 Batch complete:")
    print(f"   Processed: {len(results)}/{len(design_files)}")


def run_watcher(args):
    """Watch directory for new designs."""
    print(f"\n👁️  Starting watcher")
    print(f"   Directory: {args.watch_dir}")
    print(f"   Product type: {args.product_type}")

    orchestrator = PODOrchestrator(
        dry_run=args.dry_run,
        require_human=not args.auto_approve,
        default_brand=args.brand,
    )

    def process_callback(file_path: str):
        """Callback for each new file."""
        orchestrator.process_design(
            design_path=file_path,
            product_type=args.product_type,
        )

    watch_and_process(
        watch_dir=args.watch_dir,
        callback=process_callback,
        run_once=args.run_once,
    )


def run_gateway_integration(args):
    """Integrate with existing POD Gateway."""
    print("\n🔗 Gateway integration mode")

    integrate_with_gateway(
        watch_mode=args.watch,
        process_pending=not args.no_pending,
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Antigravity - Multi-Model AI POD Orchestration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single design
  python -m antigravity.main design path/to/design.png

  # Process directory
  python -m antigravity.main batch --directory /path/to/designs

  # Watch directory
  python -m antigravity.main watch --watch-dir /data/comfyui/output

  # Integrate with gateway
  python -m antigravity.main gateway --watch

Environment Variables:
  OPENAI_API_KEY            - OpenAI API key
  ANTHROPIC_API_KEY         - Anthropic Claude API key
  SLACK_WEBHOOK_URL         - Slack webhook for notifications
  EMAIL_TO, EMAIL_FROM      - Email configuration
  SMTP_HOST, SMTP_USER      - SMTP configuration
  NOTION_TOKEN, NOTION_DB_ID - Notion integration
  COMFYUI_OUTPUT_DIR        - ComfyUI output directory
  POD_STATE_FILE            - Gateway state file path
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
        choices=["tshirt", "hoodie"],
        default="hoodie",
        help="Product type (default: hoodie)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Single design command
    design_parser = subparsers.add_parser(
        "design",
        parents=[parent_parser],
        help="Process a single design"
    )
    design_parser.add_argument("design", help="Path to design file")
    design_parser.add_argument(
        "--ab-testing",
        action="store_true",
        help="Generate A/B testing variants"
    )

    # Batch command
    batch_parser = subparsers.add_parser(
        "batch",
        parents=[parent_parser],
        help="Process multiple designs"
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

    # Gateway command
    gateway_parser = subparsers.add_parser(
        "gateway",
        help="Integrate with existing POD Gateway"
    )
    gateway_parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuously watch for new designs"
    )
    gateway_parser.add_argument(
        "--no-pending",
        action="store_true",
        help="Skip processing pending designs"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Route to appropriate handler
    if args.command == "design":
        run_single_design(args)
    elif args.command == "batch":
        run_batch(args)
    elif args.command == "watch":
        run_watcher(args)
    elif args.command == "gateway":
        run_gateway_integration(args)


if __name__ == "__main__":
    main()

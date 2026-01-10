#!/usr/bin/env python3
"""
AIM Proofing Engine CLI
Command-line interface for AIM operations
"""
import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from app.aim_proofing import AIMProofingEngine, load_config
from app.aim_ai_analysis import AIImageAnalyzer
from app.aim_monitor import AIMMonitor
from app.state import StateManager


def analyze_image(args):
    """Analyze a single image"""
    config = load_config(args.config) if args.config else None
    engine = AIMProofingEngine(config)

    print(f"\n🔍 Analyzing: {args.image}")
    print("="*60)

    result = engine.analyze_image(args.image)

    # Display results
    print(f"\n📊 Quality Analysis:")
    print(f"   Overall Score: {result.quality_score.overall_score}/100")
    print(f"   Resolution: {result.quality_score.resolution_score}/100")
    print(f"   File Size: {result.quality_score.filesize_score}/100")
    print(f"   Format: {result.quality_score.format_score}/100")
    print(f"   Aspect Ratio: {result.quality_score.aspect_ratio_score}/100")
    print(f"   Corruption Check: {result.quality_score.corruption_score}/100")

    if result.quality_score.issues:
        print(f"\n⚠️  Issues:")
        for issue in result.quality_score.issues:
            print(f"   - {issue}")

    if result.quality_score.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in result.quality_score.recommendations:
            print(f"   - {rec}")

    print(f"\n🎯 Decision: {result.decision.upper()}")

    # AI analysis if requested
    if args.ai:
        print(f"\n🤖 AI Analysis:")
        analyzer = AIImageAnalyzer()

        if analyzer.is_available():
            ai_result = analyzer.analyze_image(args.image)

            if ai_result:
                print(f"   Commercial Score: {ai_result.get('commercial_suitability', 'N/A')}/100")
                print(f"   Content Safety: {'✓' if ai_result.get('content_safety') else '✗'}")
                print(f"   Quality: {ai_result.get('quality_assessment', 'N/A')}")
                print(f"   Recommendation: {ai_result.get('recommendation', 'N/A')}")

                if ai_result.get('suggested_title'):
                    print(f"\n   Suggested Title: {ai_result['suggested_title']}")

                if ai_result.get('strengths'):
                    print(f"\n   Strengths:")
                    for strength in ai_result['strengths']:
                        print(f"   + {strength}")

                if ai_result.get('weaknesses'):
                    print(f"\n   Weaknesses:")
                    for weakness in ai_result['weaknesses']:
                        print(f"   - {weakness}")
        else:
            print("   ⚠️  AI analysis not available (check ANTHROPIC_API_KEY)")

    # Save results if requested
    if args.output:
        output_data = {
            "filename": result.filename,
            "decision": result.decision,
            "quality_score": result.quality_score.overall_score,
            "details": {
                "resolution": result.quality_score.resolution_score,
                "filesize": result.quality_score.filesize_score,
                "format": result.quality_score.format_score,
                "aspect_ratio": result.quality_score.aspect_ratio_score,
                "corruption": result.quality_score.corruption_score
            },
            "issues": result.quality_score.issues,
            "recommendations": result.quality_score.recommendations,
            "metadata": result.quality_score.metadata
        }

        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\n💾 Results saved to: {args.output}")

    print()


def batch_analyze(args):
    """Analyze all images in a directory"""
    config = load_config(args.config) if args.config else None
    engine = AIMProofingEngine(config)

    print(f"\n🔍 Batch Analysis: {args.directory}")
    print("="*60)

    results = engine.batch_analyze(args.directory, args.pattern)

    # Generate report
    report = engine.generate_report(results)

    print(f"\n📊 Summary:")
    print(f"   Total Images: {report['total_images']}")
    print(f"   Auto-Approved: {report['auto_approved']} ({report['approval_rate']}%)")
    print(f"   Auto-Rejected: {report['auto_rejected']}")
    print(f"   Manual Review: {report['manual_review']}")
    print(f"   Average Quality: {report['average_quality_score']}/100")

    # Detailed results
    if args.verbose:
        print(f"\n📋 Detailed Results:")
        for item in report['results']:
            print(f"\n   {item['filename']}")
            print(f"      Score: {item['score']}/100")
            print(f"      Decision: {item['decision']}")
            if item['issues']:
                print(f"      Issues: {', '.join(item['issues'])}")

    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Report saved to: {args.output}")

    print()


def start_monitor(args):
    """Start AIM monitoring service"""
    config = load_config(args.config) if args.config else None

    # Load state manager if integrating with gateway
    state_manager = None
    if args.gateway_integration:
        from app import config as gateway_config
        state_manager = StateManager(gateway_config.STATE_FILE)

    monitor = AIMMonitor(args.config, state_manager)

    # Start monitoring
    directories = args.directories or config.get('watch_directories', []) if config else []

    if not directories:
        print("❌ No directories specified. Use --directories or configure in aim_config.json")
        sys.exit(1)

    monitor.start_monitoring(directories)


def test_config(args):
    """Test AIM configuration"""
    print(f"\n🧪 Testing Configuration: {args.config}")
    print("="*60)

    try:
        config = load_config(args.config)

        if not config:
            print("❌ Failed to load configuration")
            sys.exit(1)

        print("\n✅ Configuration loaded successfully")

        # Display key settings
        print(f"\n📋 Settings:")
        print(f"   Watch Directories: {len(config.get('watch_directories', []))}")

        for directory in config.get('watch_directories', []):
            exists = Path(directory).exists()
            status = "✓" if exists else "✗ (not found)"
            print(f"      - {directory} {status}")

        print(f"\n   Auto-Approval: {'Enabled' if config.get('auto_approval', {}).get('enabled') else 'Disabled'}")
        print(f"      Min Score: {config.get('auto_approval', {}).get('min_score', 0)}")

        print(f"\n   Auto-Rejection: {'Enabled' if config.get('auto_rejection', {}).get('enabled') else 'Disabled'}")
        print(f"      Max Score: {config.get('auto_rejection', {}).get('max_score', 0)}")

        print(f"\n   AI Analysis: {'Enabled' if config.get('ai_analysis', {}).get('enabled') else 'Disabled'}")

        # Test AI analyzer
        analyzer = AIImageAnalyzer()
        ai_status = "✓ Available" if analyzer.is_available() else "✗ Not available (check ANTHROPIC_API_KEY)"
        print(f"      Status: {ai_status}")

        print()

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="AIM Proofing Engine CLI - Automated Image Quality Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single image
  python aim_cli.py analyze image.png

  # Analyze with AI
  python aim_cli.py analyze image.png --ai

  # Batch analyze directory
  python aim_cli.py batch /path/to/images

  # Start monitoring service
  python aim_cli.py monitor --config aim_config.json

  # Test configuration
  python aim_cli.py test-config aim_config.json
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single image')
    analyze_parser.add_argument('image', help='Path to image file')
    analyze_parser.add_argument('--config', '-c', help='Path to AIM config file')
    analyze_parser.add_argument('--ai', action='store_true', help='Include AI analysis')
    analyze_parser.add_argument('--output', '-o', help='Save results to JSON file')
    analyze_parser.set_defaults(func=analyze_image)

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch analyze directory')
    batch_parser.add_argument('directory', help='Directory containing images')
    batch_parser.add_argument('--pattern', default='*.png', help='File pattern (default: *.png)')
    batch_parser.add_argument('--config', '-c', help='Path to AIM config file')
    batch_parser.add_argument('--output', '-o', help='Save report to JSON file')
    batch_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed results')
    batch_parser.set_defaults(func=batch_analyze)

    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start monitoring service')
    monitor_parser.add_argument('--config', '-c', help='Path to AIM config file')
    monitor_parser.add_argument('--directories', '-d', nargs='+', help='Directories to watch')
    monitor_parser.add_argument('--gateway-integration', '-g', action='store_true',
                              help='Enable POD Gateway integration')
    monitor_parser.set_defaults(func=start_monitor)

    # Test config command
    test_parser = subparsers.add_parser('test-config', help='Test configuration')
    test_parser.add_argument('config', help='Path to AIM config file')
    test_parser.set_defaults(func=test_config)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

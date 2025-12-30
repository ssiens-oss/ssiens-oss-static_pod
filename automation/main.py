#!/usr/bin/env python3
"""
Main Pipeline Orchestrator
Complete end-to-end automation: generate → list → upload → market → track
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional
import json

from asset_runner import AssetRunner
from listing_generator import ListingGenerator, QualityScorer
from marketplace_uploader import MarketplaceUploader
from tiktok_generator import TikTokGenerator
from notion_sync import PipelineTracker
from config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AssetPipeline:
    """Complete asset creation and publishing pipeline"""

    def __init__(self):
        self.asset_runner = AssetRunner()
        self.listing_gen = ListingGenerator()
        self.uploader = MarketplaceUploader()
        self.tiktok_gen = TikTokGenerator()
        self.tracker = PipelineTracker()
        self.output_dir = Path("./output")
        self.output_dir.mkdir(exist_ok=True)

    def run_complete_pipeline(
        self,
        theme: str,
        asset_type: str,
        prompts: List[str],
        style: str = "Hand-Painted",
        usage: str = "Game Development",
        price_usd: float = 4.99,
        marketplaces: Optional[List[str]] = None,
        skip_generation: bool = False,
        archive_path: Optional[Path] = None
    ) -> Dict:
        """
        Run complete pipeline from generation to tracking

        Args:
            theme: Asset theme (e.g., "Fantasy Potion Icons")
            asset_type: Type of asset (e.g., "Icon Pack")
            prompts: List of generation prompts
            style: Visual style description
            usage: Primary use case
            price_usd: Price in USD
            marketplaces: List of marketplaces to upload to
            skip_generation: Skip asset generation (use existing archive)
            archive_path: Path to existing archive (if skip_generation=True)

        Returns:
            Dictionary with results from each pipeline stage
        """
        logger.info("=" * 80)
        logger.info("ASSET PIPELINE - STARTING")
        logger.info("=" * 80)
        logger.info(f"Theme: {theme}")
        logger.info(f"Type: {asset_type}")
        logger.info(f"Prompts: {len(prompts)}")
        logger.info("=" * 80)

        results = {
            "theme": theme,
            "asset_type": asset_type,
            "success": False,
            "stages": {}
        }

        marketplaces = marketplaces or ["gumroad"]

        try:
            # STAGE 1: Generate Assets
            if not skip_generation:
                logger.info("\n[STAGE 1/6] Generating Assets...")
                archive = self.asset_runner.run(
                    prompts=prompts,
                    archive_name=f"{theme.lower().replace(' ', '_')}.zip",
                    auto_stop=True
                )

                if not archive:
                    logger.error("Asset generation failed")
                    return results

                results["stages"]["generation"] = {
                    "success": True,
                    "archive": str(archive)
                }
            else:
                archive = archive_path
                logger.info(f"\n[STAGE 1/6] Using existing archive: {archive}")
                results["stages"]["generation"] = {
                    "success": True,
                    "archive": str(archive),
                    "skipped": True
                }

            # STAGE 2: Generate Listing
            logger.info("\n[STAGE 2/6] Generating Listing...")
            listing = self.listing_gen.generate_listing(
                asset_type=asset_type,
                theme=theme,
                style=style,
                usage=usage,
                prompts=prompts,
                additional_context=f"Price: ${price_usd}"
            )

            if not listing:
                logger.error("Listing generation failed")
                return results

            # Save listing
            listing_path = self.output_dir / f"{theme.lower().replace(' ', '_')}_listing.json"
            self.listing_gen.save_listing(listing, listing_path)

            results["stages"]["listing"] = {
                "success": True,
                "data": listing,
                "path": str(listing_path)
            }

            # STAGE 3: Upload to Marketplaces
            logger.info("\n[STAGE 3/6] Uploading to Marketplaces...")
            upload_results = self.uploader.upload_to_all(
                title=listing.get("seo_title", theme),
                short_description=listing.get("short_description", ""),
                long_description=listing.get("long_description", ""),
                file_path=archive,
                price_usd=price_usd,
                tags=listing.get("tags", []),
                marketplaces=marketplaces
            )

            results["stages"]["upload"] = {
                "success": any(upload_results.values()),
                "results": upload_results
            }

            # STAGE 4: Generate TikTok Content
            logger.info("\n[STAGE 4/6] Generating TikTok Content...")
            tiktok_script = self.tiktok_gen.generate_video_script(
                asset_name=theme,
                theme=style,
                key_features=listing.get("tags", [])[:4],
                target_audience="indie game developers",
                video_length=30
            )

            # Analyze viral potential
            viral_analysis = {}
            if tiktok_script:
                viral_analysis = self.tiktok_gen.analyze_viral_potential(
                    tiktok_script,
                    asset_type.lower()
                )

            # Save TikTok content
            tiktok_path = self.output_dir / f"{theme.lower().replace(' ', '_')}_tiktok.json"
            if tiktok_script:
                tiktok_content = {
                    "script": tiktok_script,
                    "viral_analysis": viral_analysis
                }
                self.tiktok_gen.save_content(tiktok_content, tiktok_path)

            results["stages"]["tiktok"] = {
                "success": bool(tiktok_script),
                "script": tiktok_script,
                "viral_analysis": viral_analysis,
                "path": str(tiktok_path) if tiktok_script else None
            }

            # STAGE 5: Track in Notion
            logger.info("\n[STAGE 5/6] Tracking in Notion...")
            try:
                notion_entry = self.tracker.track_generation(
                    theme=theme,
                    asset_type=asset_type,
                    prompts=prompts,
                    archive_path=str(archive)
                )

                results["stages"]["notion"] = {
                    "success": notion_entry is not None,
                    "entry": notion_entry
                }
            except Exception as e:
                logger.warning(f"Notion tracking failed: {e}")
                results["stages"]["notion"] = {
                    "success": False,
                    "error": str(e)
                }

            # STAGE 6: Generate Summary Report
            logger.info("\n[STAGE 6/6] Generating Summary Report...")
            report = self._generate_summary_report(results, listing, tiktok_script)
            report_path = self.output_dir / f"{theme.lower().replace(' ', '_')}_report.txt"

            with open(report_path, 'w') as f:
                f.write(report)

            results["stages"]["report"] = {
                "success": True,
                "path": str(report_path)
            }

            results["success"] = True

            logger.info("\n" + "=" * 80)
            logger.info("ASSET PIPELINE - COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)

            return results

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            results["error"] = str(e)
            return results

    def _generate_summary_report(
        self,
        results: Dict,
        listing: Dict,
        tiktok_script: Dict
    ) -> str:
        """Generate human-readable summary report"""
        lines = []

        lines.append("=" * 80)
        lines.append("ASSET CREATION PIPELINE - SUMMARY REPORT")
        lines.append("=" * 80)
        lines.append(f"Asset: {results['theme']}")
        lines.append(f"Type: {results['asset_type']}")
        lines.append("")

        # Stage results
        lines.append("PIPELINE STAGES")
        lines.append("-" * 80)
        for stage_name, stage_data in results["stages"].items():
            status = "✓" if stage_data.get("success") else "✗"
            lines.append(f"{status} {stage_name.capitalize()}")

        lines.append("")

        # Listing details
        if listing:
            lines.append("LISTING DETAILS")
            lines.append("-" * 80)
            lines.append(f"Title: {listing.get('seo_title', 'N/A')}")
            lines.append(f"Short: {listing.get('short_description', 'N/A')}")
            lines.append(f"Price: {listing.get('pricing_suggestion', 'N/A')}")
            lines.append(f"Tags: {', '.join(listing.get('tags', [])[:10])}")
            lines.append("")

        # TikTok details
        if tiktok_script:
            lines.append("TIKTOK CONTENT")
            lines.append("-" * 80)
            lines.append(f"Hook: {tiktok_script.get('hook', 'N/A')}")
            lines.append(f"CTA: {tiktok_script.get('call_to_action', 'N/A')}")

            viral = results["stages"].get("tiktok", {}).get("viral_analysis", {})
            if viral:
                lines.append(f"Viral Probability: {viral.get('viral_probability', 'N/A')}")
                lines.append(f"Overall Score: {viral.get('overall_score', 'N/A')}/10")
            lines.append("")

        # Upload results
        upload_results = results["stages"].get("upload", {}).get("results", {})
        if upload_results:
            lines.append("MARKETPLACE UPLOADS")
            lines.append("-" * 80)
            for marketplace, success in upload_results.items():
                status = "✓" if success else "✗"
                lines.append(f"{status} {marketplace.capitalize()}")
            lines.append("")

        # Next steps
        lines.append("NEXT STEPS")
        lines.append("-" * 80)
        lines.append("1. Review generated listing and make any adjustments")
        lines.append("2. Record TikTok video using the generated script")
        lines.append("3. Post TikTok content with generated hashtags")
        lines.append("4. Monitor performance in Notion dashboard")
        lines.append("5. Run kill list analysis after 30 days")

        lines.append("")
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)

        return "\n".join(lines)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Asset Creation Pipeline")
    parser.add_argument("--theme", required=True, help="Asset theme name")
    parser.add_argument("--type", default="Icon Pack", help="Asset type")
    parser.add_argument("--prompts", nargs="+", required=True, help="Generation prompts")
    parser.add_argument("--style", default="Hand-Painted", help="Visual style")
    parser.add_argument("--usage", default="Game Development", help="Primary use case")
    parser.add_argument("--price", type=float, default=4.99, help="Price in USD")
    parser.add_argument("--marketplaces", nargs="+", default=["gumroad"], help="Target marketplaces")
    parser.add_argument("--skip-generation", action="store_true", help="Skip asset generation")
    parser.add_argument("--archive", type=Path, help="Path to existing archive")

    args = parser.parse_args()

    # Validate config
    errors = config.validate()
    if errors:
        logger.error("Configuration errors:")
        for error in errors:
            logger.error(f"  - {error}")
        sys.exit(1)

    # Run pipeline
    pipeline = AssetPipeline()
    results = pipeline.run_complete_pipeline(
        theme=args.theme,
        asset_type=args.type,
        prompts=args.prompts,
        style=args.style,
        usage=args.usage,
        price_usd=args.price,
        marketplaces=args.marketplaces,
        skip_generation=args.skip_generation,
        archive_path=args.archive
    )

    # Print summary
    if results["success"]:
        print("\n✓ Pipeline completed successfully!")
        print(f"Report: {results['stages']['report']['path']}")
        sys.exit(0)
    else:
        print("\n✗ Pipeline failed")
        if "error" in results:
            print(f"Error: {results['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()

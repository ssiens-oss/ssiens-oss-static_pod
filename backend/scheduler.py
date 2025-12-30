"""
Autonomous Scheduler - Run POD workflows on schedule
Supports hourly, daily, and custom schedules
"""

import schedule
import time
import logging
from datetime import datetime
from typing import List, Callable
from autonomous_pod import (
    Config,
    MultiLLMPromptGenerator,
    CrewAIOrchestrator,
    ComfyUIClient,
    PrintifyClient,
    SocialMediaPoster
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutomatedPODScheduler:
    """Scheduled automation for POD workflows"""

    def __init__(self, config: Config, themes: List[str]):
        self.config = config
        self.themes = themes
        self.theme_index = 0

        # Initialize components
        self.prompt_gen = MultiLLMPromptGenerator(config)
        self.crew = CrewAIOrchestrator(config, self.prompt_gen)
        self.comfyui = ComfyUIClient(config)
        self.printify = PrintifyClient(config)
        self.social = SocialMediaPoster(config)

        logger.info(f"Initialized scheduler with {len(themes)} themes")

    def run_single_workflow(self):
        """Execute one complete workflow"""
        # Cycle through themes
        theme = self.themes[self.theme_index]
        self.theme_index = (self.theme_index + 1) % len(self.themes)

        logger.info(f"\n{'='*80}")
        logger.info(f"SCHEDULED WORKFLOW - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Theme: {theme}")
        logger.info(f"{'='*80}\n")

        try:
            # Step 1: AI agents generate concept
            concept = self.crew.run_autonomous_workflow(theme)

            if not concept or concept.get('error'):
                logger.error(f"Failed to generate concept: {concept.get('error')}")
                return

            # Step 2: Generate image with ComfyUI
            prompts = concept.get('prompts', [])
            if not prompts:
                logger.error("No prompts generated")
                return

            main_prompt = prompts[0] if isinstance(prompts, list) else str(prompts)
            image_url = self.comfyui.generate_image(main_prompt)

            if not image_url:
                logger.error("Failed to generate image")
                return

            logger.info(f"Generated image: {image_url}")

            # Step 3: Upload to Printify
            upload_id = self.printify.upload_image(
                image_url,
                f"{theme.replace(' ', '_')}_{int(time.time())}.png"
            )

            if not upload_id:
                logger.error("Failed to upload image")
                return

            # Step 4: Create product
            product_id = self.printify.create_product(
                title=concept.get('title', f"{theme} Design"),
                description=concept.get('description', ''),
                image_id=upload_id,
                price=concept.get('price', 2999)
            )

            if not product_id:
                logger.error("Failed to create product")
                return

            logger.info(f"Created product: {product_id}")

            # Step 5: Publish to stores
            if self.printify.publish_product(product_id):
                logger.info("Product published successfully")

                # Step 6: Post to social media (best times: 7-9 PM)
                current_hour = datetime.now().hour
                if 19 <= current_hour <= 21:  # 7-9 PM
                    social_data = concept.get('social', {})
                    if social_data:
                        self.social.post_to_instagram(
                            image_url,
                            social_data.get('caption', f"New drop: {theme}!"),
                            social_data.get('hashtags', [])
                        )
                        logger.info("Posted to Instagram")
                else:
                    logger.info(f"Skipping social post (current hour: {current_hour}, optimal: 19-21)")

            logger.info(f"\n{'='*80}")
            logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info(f"{'='*80}\n")

        except Exception as e:
            logger.error(f"Workflow error: {e}", exc_info=True)

    def run_batch_workflow(self, count: int = 5):
        """Run multiple workflows in batch"""
        logger.info(f"Starting batch workflow: {count} designs")

        for i in range(count):
            logger.info(f"\n--- Batch {i+1}/{count} ---")
            self.run_single_workflow()
            time.sleep(30)  # 30s between batches

        logger.info("Batch workflow complete")

    def setup_schedules(self):
        """Configure scheduled tasks"""

        # Daily batch at 2 AM (low traffic time)
        schedule.every().day.at("02:00").do(self.run_batch_workflow, count=10)
        logger.info("Scheduled: Daily batch (10 designs) at 2:00 AM")

        # Hourly single design during business hours (9 AM - 6 PM)
        for hour in range(9, 19):
            schedule.every().day.at(f"{hour:02d}:00").do(self.run_single_workflow)
        logger.info("Scheduled: Hourly designs from 9 AM - 6 PM")

        # Prime social posting times (7 PM, 8 PM)
        schedule.every().day.at("19:00").do(self.run_single_workflow)
        schedule.every().day.at("20:00").do(self.run_single_workflow)
        logger.info("Scheduled: Extra designs at 7 PM and 8 PM (prime social times)")

    def start(self):
        """Start the scheduler"""
        self.setup_schedules()

        logger.info("\n" + "="*80)
        logger.info("AUTONOMOUS POD SCHEDULER STARTED")
        logger.info("="*80)
        logger.info(f"Active schedules: {len(schedule.get_jobs())}")
        logger.info("Press Ctrl+C to stop\n")

        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("\nScheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)
                time.sleep(300)  # Wait 5 min on error


def main():
    """Main entry point"""

    # Load configuration
    config = Config.load_from_file()

    # Define your design themes
    themes = [
        "cyberpunk streetwear",
        "retro 90s aesthetic",
        "minimalist typography",
        "abstract geometric patterns",
        "nature-inspired graphics",
        "anime street fashion",
        "grunge revival",
        "neon vaporwave",
        "brutalist design",
        "y2k futuristic"
    ]

    # Create and start scheduler
    scheduler = AutomatedPODScheduler(config, themes)

    # Uncomment to run immediate test
    # logger.info("Running test workflow...")
    # scheduler.run_single_workflow()

    # Start scheduled execution
    scheduler.start()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
StaticWaves Forge - RunPod Worker
Processes 3D asset generation jobs from Redis queue
"""

import os
import sys
import time
import json
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
WORKER_ID = os.getenv('WORKER_ID', 'worker-local')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', '/output'))
BLENDER_PATH = os.getenv('BLENDER_PATH', '/usr/bin/blender')

# Package paths
PACKAGE_DIR = Path('/worker/packages')

class AssetGenerationWorker:
    """Worker that processes asset generation jobs"""

    def __init__(self):
        self.worker_id = WORKER_ID
        self.jobs_processed = 0
        self.start_time = time.time()

    def run_blender_script(self, script_path: str, args: list = None) -> bool:
        """
        Run a Blender Python script headlessly

        Args:
            script_path: Path to the Python script
            args: Additional arguments to pass to the script

        Returns:
            True if successful, False otherwise
        """
        cmd = [
            BLENDER_PATH,
            '--background',
            '--python', str(script_path),
            '--'
        ]

        if args:
            cmd.extend(args)

        logger.info(f"Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info("Blender script completed successfully")
                logger.debug(result.stdout)
                return True
            else:
                logger.error(f"Blender script failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Blender script timed out")
            return False
        except Exception as e:
            logger.error(f"Error running Blender script: {e}")
            return False

    def process_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single asset generation job

        Args:
            job_data: Job configuration dictionary

        Returns:
            Result dictionary with output files and metadata
        """
        job_id = job_data.get('job_id', 'unknown')
        logger.info(f"Processing job {job_id}")

        # Extract job parameters
        prompt = job_data.get('prompt', '')
        asset_type = job_data.get('asset_type', 'prop')
        style = job_data.get('style', 'low-poly')
        seed = job_data.get('seed', int(time.time() * 1000) % 2147483647)
        include_rig = job_data.get('include_rig', False)
        include_animations = job_data.get('include_animations', [])
        export_formats = job_data.get('export_formats', ['glb'])

        # Create job output directory
        job_output_dir = OUTPUT_DIR / job_id
        job_output_dir.mkdir(parents=True, exist_ok=True)

        result = {
            'job_id': job_id,
            'status': 'processing',
            'output_files': {},
            'error': None
        }

        try:
            # Step 1: Generate asset
            logger.info(f"Step 1/4: Generating {asset_type} asset...")
            asset_file = job_output_dir / 'asset.blend'

            generate_script = PACKAGE_DIR / 'blender' / 'generate_asset.py'
            generate_args = [
                str(seed),
                asset_type,
                str(asset_file),
                style
            ]

            if not self.run_blender_script(generate_script, generate_args):
                raise Exception("Asset generation failed")

            # Step 2: Add rigging (if requested)
            if include_rig:
                logger.info("Step 2/4: Adding auto-rig...")
                rig_script = PACKAGE_DIR / 'blender' / 'auto_rig.py'

                if not self.run_blender_script(rig_script):
                    logger.warning("Rigging failed, continuing without rig")

            # Step 3: Add animations (if requested)
            if include_animations:
                logger.info(f"Step 3/4: Adding animations: {', '.join(include_animations)}")
                anim_script = PACKAGE_DIR / 'blender' / 'add_animation.py'

                for anim_type in include_animations:
                    anim_args = [anim_type, '60']
                    if not self.run_blender_script(anim_script, anim_args):
                        logger.warning(f"Animation '{anim_type}' failed, skipping")

            # Step 4: Export in requested formats
            logger.info(f"Step 4/4: Exporting to {', '.join(export_formats)}...")
            export_script = PACKAGE_DIR / 'blender' / 'export.py'

            for format_type in export_formats:
                output_file = job_output_dir / f"{job_id}.{format_type}"
                export_args = [
                    format_type,
                    str(output_file),
                    'true' if include_animations else 'false'
                ]

                if self.run_blender_script(export_script, export_args):
                    result['output_files'][format_type] = str(output_file)
                    logger.info(f"✅ Exported {format_type}: {output_file}")
                else:
                    logger.warning(f"Failed to export {format_type}")

            # Mark as completed
            result['status'] = 'completed'
            self.jobs_processed += 1

            logger.info(f"✅ Job {job_id} completed successfully")

        except Exception as e:
            logger.error(f"❌ Job {job_id} failed: {e}")
            result['status'] = 'failed'
            result['error'] = str(e)

        return result

    def run(self):
        """Main worker loop"""
        logger.info(f"🚀 Worker {self.worker_id} started")
        logger.info("Waiting for jobs...")

        # TODO: Implement Redis queue consumer
        # For now, this is a mock implementation

        while True:
            try:
                # In production:
                # 1. Connect to Redis
                # 2. Pop job from queue
                # 3. Process job
                # 4. Update job status in Redis
                # 5. Upload assets to S3
                # 6. Mark job complete

                # Mock: Sleep and wait
                time.sleep(5)

                # Health check endpoint would go here
                # Could use FastAPI to expose worker status

            except KeyboardInterrupt:
                logger.info("Worker shutting down...")
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(10)

        uptime = time.time() - self.start_time
        logger.info(f"Worker stopped. Processed {self.jobs_processed} jobs in {uptime:.0f}s")

if __name__ == "__main__":
    worker = AssetGenerationWorker()
    worker.run()

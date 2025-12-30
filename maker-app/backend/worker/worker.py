"""
Background worker for processing generation jobs
Polls database for queued jobs and processes them using generation services
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import GenerationJob
from app.services import image, video, music, book

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

POLL_INTERVAL = int(os.getenv("WORKER_POLL_INTERVAL", "2"))  # seconds
MAX_RETRIES = int(os.getenv("WORKER_MAX_RETRIES", "3"))


def process_job(job: GenerationJob, db):
    """Process a single generation job"""
    logger.info(f"Processing job {job.id} (type: {job.type})")

    try:
        # Update status to processing
        job.status = "processing"
        db.commit()

        # Route to appropriate service
        if job.type == "image":
            output_url = image.generate(job.id, job.prompt)
        elif job.type == "video":
            output_url = video.generate(job.id, job.prompt)
        elif job.type == "music":
            output_url = music.generate(job.id, job.prompt)
        elif job.type == "book":
            output_url = book.generate(job.id, job.prompt, job.output_format)
        else:
            raise ValueError(f"Unknown job type: {job.type}")

        # Update job with output
        job.status = "completed"
        job.output_url = output_url
        job.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"✓ Job {job.id} completed: {output_url}")

    except Exception as e:
        logger.error(f"✗ Job {job.id} failed: {e}")

        # Update job with error
        job.status = "failed"
        job.error_message = str(e)
        db.commit()


def run_worker():
    """Main worker loop"""
    logger.info("=" * 60)
    logger.info("StaticWaves Maker Worker Starting")
    logger.info("=" * 60)
    logger.info(f"Poll interval: {POLL_INTERVAL}s")
    logger.info(f"Max retries: {MAX_RETRIES}")
    logger.info("")

    while True:
        db = SessionLocal()

        try:
            # Find next queued job
            job = db.query(GenerationJob).filter_by(
                status="queued"
            ).order_by(GenerationJob.created_at).first()

            if job:
                process_job(job, db)
            else:
                # No jobs, sleep
                time.sleep(POLL_INTERVAL)

        except Exception as e:
            logger.error(f"Worker error: {e}")
            time.sleep(POLL_INTERVAL)

        finally:
            db.close()


def run_worker_with_queue_monitoring():
    """Worker with queue size monitoring for autoscaling"""
    logger.info("Worker with autoscaling support")

    while True:
        db = SessionLocal()

        try:
            # Check queue size
            queue_size = db.query(GenerationJob).filter_by(status="queued").count()
            processing = db.query(GenerationJob).filter_by(status="processing").count()

            logger.info(f"Queue: {queue_size} queued, {processing} processing")

            # Autoscale trigger (scale up if queue > 5)
            if queue_size > 5:
                logger.warning(f"High queue size: {queue_size}")
                # Trigger RunPod pod start (implement autoscaling logic)

            # Process next job
            job = db.query(GenerationJob).filter_by(
                status="queued"
            ).order_by(GenerationJob.created_at).first()

            if job:
                process_job(job, db)
            else:
                time.sleep(POLL_INTERVAL)

                # Scale down if idle (no jobs for extended period)
                if queue_size == 0 and processing == 0:
                    # Could trigger pod stop after idle timeout
                    pass

        except Exception as e:
            logger.error(f"Worker error: {e}")
            time.sleep(POLL_INTERVAL)

        finally:
            db.close()


if __name__ == "__main__":
    # Choose worker mode
    mode = os.getenv("WORKER_MODE", "simple")

    if mode == "autoscale":
        run_worker_with_queue_monitoring()
    else:
        run_worker()

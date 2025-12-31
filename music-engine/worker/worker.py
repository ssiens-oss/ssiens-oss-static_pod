"""
StaticWaves Music Worker - GPU-accelerated music generation

This worker:
1. Pulls jobs from Redis queue
2. Generates music using MusicGen
3. Re-synthesizes stems with DDSP
4. Mixes and exports final audio
"""

import redis
import json
import os
import sys
import time
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from musicgen_engine import generate_base_audio
from ddsp_synth import resynthesize_stems
from mixer import mix_and_export


# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/data/output")

# Ensure output directory exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def update_status(r: redis.Redis, job_id: str, status: str, progress: float = None):
    """Update job status in Redis"""
    r.set(f"job:{job_id}:status", status)
    if progress is not None:
        r.set(f"job:{job_id}:progress", str(progress))
    print(f"[{job_id}] Status: {status} ({progress}%)" if progress else f"[{job_id}] Status: {status}")


def process_job(r: redis.Redis, job_data: dict):
    """
    Process a single music generation job

    Pipeline:
    1. Generate base audio with MusicGen
    2. Re-synthesize stems with DDSP
    3. Mix and export
    """
    job_id = job_data["job_id"]
    spec = job_data["spec"]

    print(f"\n{'='*60}")
    print(f"Processing job: {job_id}")
    print(f"Spec: {json.dumps(spec, indent=2)}")
    print(f"{'='*60}\n")

    try:
        # Step 1: Generate base audio with MusicGen
        update_status(r, job_id, "running", 10)
        print(f"[{job_id}] Step 1/3: Generating base audio with MusicGen...")

        base_audio = generate_base_audio(spec)
        update_status(r, job_id, "running", 40)

        # Step 2: Re-synthesize stems with DDSP
        print(f"[{job_id}] Step 2/3: Re-synthesizing stems with DDSP...")
        stems = resynthesize_stems(base_audio, spec)
        update_status(r, job_id, "running", 70)

        # Step 3: Mix and export
        print(f"[{job_id}] Step 3/3: Mixing and exporting...")
        output_files = mix_and_export(job_id, stems, spec, OUTPUT_DIR)
        update_status(r, job_id, "running", 90)

        # Store output URLs
        output_urls = {
            name: f"/download/{job_id}/{name}"
            for name in output_files.keys()
        }
        r.set(f"job:{job_id}:outputs", json.dumps(output_urls))

        # Mark complete
        update_status(r, job_id, "completed", 100)
        print(f"[{job_id}] ✅ Job completed successfully!")
        print(f"[{job_id}] Outputs: {list(output_files.keys())}")

    except Exception as e:
        print(f"[{job_id}] ❌ Error: {str(e)}")
        update_status(r, job_id, "failed", 0)
        r.set(f"job:{job_id}:error", str(e))


def main():
    """Main worker loop"""
    print("🎵 StaticWaves Music Worker Starting...")
    print(f"Redis: {REDIS_HOST}:{REDIS_PORT}")
    print(f"Output: {OUTPUT_DIR}")
    print("Waiting for jobs...\n")

    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )

    # Test Redis connection
    try:
        r.ping()
        print("✅ Redis connection successful\n")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return

    # Main loop
    while True:
        try:
            # Block until job available (5s timeout)
            job = r.brpop("music_jobs", timeout=5)

            if not job:
                continue

            # Parse job data
            job_data = json.loads(job[1])

            # Process the job
            process_job(r, job_data)

        except KeyboardInterrupt:
            print("\n⚠️  Worker shutting down...")
            break
        except Exception as e:
            print(f"❌ Worker error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()

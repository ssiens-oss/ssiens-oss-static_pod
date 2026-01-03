"""
StaticWaves Forge - Worker Service
Processes asset generation jobs from Redis queue using Blender
"""

import os
import sys
import json
import time
import subprocess
import shutil
import signal
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import redis
import uuid

class WorkerConfig:
    """Worker configuration"""
    def __init__(self):
        self.worker_id = os.getenv('WORKER_ID', f"worker-{uuid.uuid4().hex[:8]}")
        self.worker_type = os.getenv('WORKER_TYPE', 'local')
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.queue_name = os.getenv('QUEUE_NAME', 'generation:normal')
        self.blender_path = os.getenv('BLENDER_PATH', 'blender')
        self.output_dir = Path(os.getenv('OUTPUT_DIR', '/workspace/generated_assets'))
        self.max_concurrent_jobs = int(os.getenv('MAX_CONCURRENT_JOBS', '1'))
        self.job_timeout = int(os.getenv('JOB_TIMEOUT', '600'))  # 10 minutes
        self.poll_interval = int(os.getenv('POLL_INTERVAL', '5'))  # 5 seconds


class Worker:
    """Asset generation worker"""

    def __init__(self, config: WorkerConfig):
        self.config = config
        self.redis_client = None
        self.running = False
        self.current_job_id = None
        self.jobs_completed = 0
        self.jobs_failed = 0
        self.start_time = datetime.now()

        print(f"🚀 Initializing Worker: {self.config.worker_id}")
        print(f"   Type: {self.config.worker_type}")
        print(f"   Redis: {self.config.redis_url}")
        print(f"   Queue: {self.config.queue_name}")
        print(f"   Blender: {self.config.blender_path}")
        print(f"   Output: {self.config.output_dir}")

        # Create output directory
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n⚠️  Received signal {signum}, shutting down gracefully...")
        self.stop()

    def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                self.config.redis_url,
                decode_responses=True
            )
            self.redis_client.ping()
            print(f"✅ Connected to Redis")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            return False

    def start(self):
        """Start the worker"""
        print(f"\n{'='*60}")
        print(f"🎨 StaticWaves Forge Worker Starting")
        print(f"{'='*60}\n")

        if not self.connect():
            return

        self.running = True
        self._register_worker()

        print(f"👀 Worker {self.config.worker_id} polling queue: {self.config.queue_name}")
        print(f"   Press Ctrl+C to stop\n")

        try:
            while self.running:
                self._poll_queue()
                time.sleep(self.config.poll_interval)
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        finally:
            self.stop()

    def stop(self):
        """Stop the worker"""
        if not self.running:
            return

        print(f"\n{'='*60}")
        print(f"🛑 Worker {self.config.worker_id} Shutting Down")
        print(f"{'='*60}")

        self.running = False
        self._unregister_worker()

        # Print statistics
        uptime = (datetime.now() - self.start_time).total_seconds()
        print(f"\n📊 Worker Statistics:")
        print(f"   Jobs Completed: {self.jobs_completed}")
        print(f"   Jobs Failed: {self.jobs_failed}")
        print(f"   Uptime: {uptime:.0f}s")
        print(f"   Success Rate: {self._success_rate():.1f}%\n")

        print("✅ Worker stopped cleanly")

    def _success_rate(self) -> float:
        """Calculate success rate"""
        total = self.jobs_completed + self.jobs_failed
        if total == 0:
            return 100.0
        return (self.jobs_completed / total) * 100

    def _register_worker(self):
        """Register worker with Redis"""
        worker_key = f"workers:{self.config.worker_id}"
        worker_data = {
            'worker_id': self.config.worker_id,
            'worker_type': self.config.worker_type,
            'status': 'idle',
            'started_at': self.start_time.isoformat(),
            'jobs_completed': 0,
            'jobs_failed': 0
        }
        self.redis_client.hset(worker_key, mapping=worker_data)
        self.redis_client.expire(worker_key, 300)  # 5 minute TTL

    def _unregister_worker(self):
        """Unregister worker from Redis"""
        worker_key = f"workers:{self.config.worker_id}"
        self.redis_client.delete(worker_key)

    def _update_worker_status(self, status: str, current_job: Optional[str] = None):
        """Update worker status in Redis"""
        worker_key = f"workers:{self.config.worker_id}"
        update_data = {
            'status': status,
            'jobs_completed': self.jobs_completed,
            'jobs_failed': self.jobs_failed,
            'last_updated': datetime.now().isoformat()
        }
        if current_job:
            update_data['current_job'] = current_job
        else:
            update_data['current_job'] = ''

        self.redis_client.hset(worker_key, mapping=update_data)
        self.redis_client.expire(worker_key, 300)

    def _poll_queue(self):
        """Poll the queue for jobs"""
        try:
            # Pop job from queue (blocking for 1 second)
            result = self.redis_client.blpop(self.config.queue_name, timeout=1)

            if result is None:
                return

            queue_name, job_data = result
            job = json.loads(job_data)

            self._process_job(job)

        except Exception as e:
            print(f"❌ Error polling queue: {e}")

    def _process_job(self, job: Dict):
        """Process a generation job"""
        job_id = job['job_id']
        self.current_job_id = job_id

        print(f"\n{'='*60}")
        print(f"🎨 Processing Job: {job_id}")
        print(f"   Prompt: {job.get('prompt', 'N/A')}")
        print(f"   Type: {job.get('asset_type', 'N/A')}")
        print(f"{'='*60}\n")

        self._update_worker_status('processing', job_id)
        self._update_job_status(job_id, 'processing', 0.0)

        try:
            # Create job output directory
            job_output_dir = self.config.output_dir / job_id
            job_output_dir.mkdir(parents=True, exist_ok=True)

            # Prepare job config for Blender
            job_config = {
                **job,
                'output_dir': str(job_output_dir)
            }

            # Save job config
            config_path = job_output_dir / 'job_config.json'
            with open(config_path, 'w') as f:
                json.dump(job_config, f, indent=2)

            # Execute Blender generation
            result = self._run_blender_generation(config_path)

            if result['status'] == 'success':
                print(f"✅ Job {job_id} completed successfully")
                self._update_job_status(
                    job_id,
                    'completed',
                    1.0,
                    result.get('metadata'),
                    result.get('output_files')
                )
                self.jobs_completed += 1
            else:
                print(f"❌ Job {job_id} failed")
                self._update_job_status(
                    job_id,
                    'failed',
                    0.0,
                    error_message=result.get('error')
                )
                self.jobs_failed += 1

        except Exception as e:
            print(f"❌ Job {job_id} failed with exception: {e}")
            self._update_job_status(job_id, 'failed', 0.0, error_message=str(e))
            self.jobs_failed += 1

        finally:
            self.current_job_id = None
            self._update_worker_status('idle')

    def _run_blender_generation(self, config_path: Path) -> Dict:
        """Run Blender generation script"""
        script_path = Path(__file__).parent / 'blender_scripts' / 'asset_generator.py'

        if not script_path.exists():
            return {
                'status': 'error',
                'error': f'Blender script not found: {script_path}'
            }

        # Build Blender command
        cmd = [
            self.config.blender_path,
            '--background',
            '--python', str(script_path),
            '--', str(config_path)
        ]

        print(f"🔧 Running Blender generation...")
        print(f"   Command: {' '.join(cmd)}\n")

        try:
            # Run Blender process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Monitor output for progress updates
            job_id = json.loads(config_path.read_text())['job_id']

            for line in process.stdout:
                line = line.strip()
                if line.startswith('PROGRESS:'):
                    _, progress, message = line.split(':', 2)
                    self._update_job_status(job_id, 'processing', float(progress), message=message)
                    print(f"   📊 {float(progress)*100:.0f}% - {message}")
                elif line.startswith('LOG:'):
                    _, message = line.split(':', 1)
                    print(f"   ℹ️  {message}")
                elif line.startswith('ERROR:'):
                    _, message = line.split(':', 1)
                    print(f"   ❌ {message}")
                elif line.startswith('SUCCESS:'):
                    _, result_path = line.split(':', 1)
                    result = json.loads(Path(result_path).read_text())
                    return result

            # Wait for process to complete
            process.wait(timeout=self.config.job_timeout)

            if process.returncode != 0:
                stderr = process.stderr.read()
                return {
                    'status': 'error',
                    'error': f'Blender exited with code {process.returncode}: {stderr}'
                }

            # Read result
            result_path = config_path.parent / 'result.json'
            if result_path.exists():
                return json.loads(result_path.read_text())
            else:
                return {
                    'status': 'error',
                    'error': 'No result file generated'
                }

        except subprocess.TimeoutExpired:
            process.kill()
            return {
                'status': 'error',
                'error': f'Job timeout after {self.config.job_timeout}s'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _update_job_status(
        self,
        job_id: str,
        status: str,
        progress: float,
        metadata: Optional[Dict] = None,
        output_files: Optional[Dict] = None,
        error_message: Optional[str] = None,
        message: Optional[str] = None
    ):
        """Update job status in Redis"""
        job_key = f"jobs:{job_id}"

        update_data = {
            'status': status,
            'progress': progress,
            'updated_at': datetime.now().isoformat()
        }

        if message:
            update_data['message'] = message

        if metadata:
            update_data['metadata'] = json.dumps(metadata)

        if output_files:
            update_data['output_files'] = json.dumps(output_files)

        if error_message:
            update_data['error_message'] = error_message

        self.redis_client.hset(job_key, mapping=update_data)

        # Publish progress update
        self.redis_client.publish(
            f"job_progress:{job_id}",
            json.dumps({
                'job_id': job_id,
                'status': status,
                'progress': progress,
                'message': message
            })
        )


def main():
    """Main entry point"""
    config = WorkerConfig()
    worker = Worker(config)
    worker.start()


if __name__ == "__main__":
    main()

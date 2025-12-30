"""
Asset Runner - ComfyUI via RunPod integration
Generates assets using ComfyUI running on RunPod pods
"""

import time
import os
import zipfile
import requests
import logging
from typing import List, Dict, Optional
from pathlib import Path
from config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RunPodManager:
    """Manages RunPod pod lifecycle and operations"""

    def __init__(self):
        self.api_key = config.runpod.api_key
        self.pod_id = config.runpod.pod_id
        self.pod_ip = config.runpod.pod_ip
        self.comfyui_port = config.runpod.comfyui_port
        self.base_url = "https://api.runpod.io/v1"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def start_pod(self, max_retries: int = 3) -> bool:
        """Start RunPod pod with retry logic"""
        logger.info(f"Starting pod {self.pod_id}...")

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/pods/{self.pod_id}/start",
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()
                logger.info("Pod started successfully")
                return True
            except requests.exceptions.RequestException as e:
                logger.warning(f"Start pod attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("Failed to start pod after all retries")
                    return False

    def stop_pod(self) -> bool:
        """Stop RunPod pod"""
        logger.info(f"Stopping pod {self.pod_id}...")

        try:
            response = requests.post(
                f"{self.base_url}/pods/{self.pod_id}/stop",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            logger.info("Pod stopped successfully")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to stop pod: {e}")
            return False

    def get_pod_status(self) -> Optional[Dict]:
        """Get pod status"""
        try:
            response = requests.get(
                f"{self.base_url}/pods/{self.pod_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get pod status: {e}")
            return None

    def wait_for_ready(self, timeout: int = 300, check_interval: int = 10) -> bool:
        """Wait for pod to be ready"""
        logger.info("Waiting for pod to be ready...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check ComfyUI health endpoint
                response = requests.get(
                    f"http://{self.pod_ip}:{self.comfyui_port}/system_stats",
                    timeout=5
                )
                if response.status_code == 200:
                    logger.info("Pod is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass

            logger.info(f"Pod not ready yet, checking again in {check_interval}s...")
            time.sleep(check_interval)

        logger.error("Pod did not become ready within timeout")
        return False


class ComfyUIGenerator:
    """Generates assets using ComfyUI API"""

    def __init__(self, pod_manager: RunPodManager):
        self.pod_manager = pod_manager
        self.base_url = f"http://{pod_manager.pod_ip}:{pod_manager.comfyui_port}"

    def generate_asset(
        self,
        prompt: str,
        output_format: str = "png",
        style: str = "icon",
        output_dir: str = "/workspace/icons",
        timeout: int = 120
    ) -> bool:
        """Generate single asset via ComfyUI"""
        logger.info(f"Generating asset: {prompt}")

        try:
            # ComfyUI workflow submission
            payload = {
                "prompt": prompt,
                "output_format": output_format,
                "style": style,
                "output_dir": output_dir
            }

            response = requests.post(
                f"{self.base_url}/prompt",
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"Asset generated: {result.get('prompt_id', 'unknown')}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate asset: {e}")
            return False

    def generate_batch(
        self,
        prompts: List[str],
        output_format: str = "png",
        style: str = "icon",
        output_dir: str = "/workspace/icons",
        delay_between: int = 5
    ) -> Dict[str, bool]:
        """Generate batch of assets"""
        results = {}

        for i, prompt in enumerate(prompts):
            logger.info(f"Generating asset {i + 1}/{len(prompts)}")
            success = self.generate_asset(prompt, output_format, style, output_dir)
            results[prompt] = success

            if i < len(prompts) - 1:  # Don't delay after last item
                time.sleep(delay_between)

        success_count = sum(1 for v in results.values() if v)
        logger.info(f"Batch complete: {success_count}/{len(prompts)} successful")

        return results


class AssetArchiver:
    """Handles asset packaging and archiving"""

    def __init__(self):
        self.output_dir = Path(config.asset.output_dir)
        self.archive_dir = Path(config.asset.archive_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def zip_assets(
        self,
        source_path: str,
        archive_name: str,
        file_pattern: str = "*.png"
    ) -> Optional[Path]:
        """Create zip archive of generated assets"""
        logger.info(f"Creating archive: {archive_name}")

        archive_path = self.archive_dir / archive_name
        source = Path(source_path)

        if not source.exists():
            logger.error(f"Source path does not exist: {source_path}")
            return None

        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                file_count = 0
                for file in source.glob(file_pattern):
                    zipf.write(file, file.name)
                    file_count += 1

                logger.info(f"Archived {file_count} files to {archive_name}")

            return archive_path

        except Exception as e:
            logger.error(f"Failed to create archive: {e}")
            return None

    def create_metadata(self, archive_path: Path, metadata: Dict) -> Path:
        """Create metadata file for archive"""
        import json

        metadata_path = archive_path.with_suffix('.json')

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Created metadata: {metadata_path}")
        return metadata_path


class AssetRunner:
    """Main asset generation orchestrator"""

    def __init__(self):
        self.pod_manager = RunPodManager()
        self.generator = ComfyUIGenerator(self.pod_manager)
        self.archiver = AssetArchiver()

    def run(
        self,
        prompts: List[str],
        archive_name: str = "asset_pack.zip",
        output_dir: str = "/workspace/icons",
        auto_stop: bool = True
    ) -> Optional[Path]:
        """Run complete asset generation pipeline"""
        logger.info("=" * 60)
        logger.info("Starting Asset Generation Pipeline")
        logger.info("=" * 60)

        try:
            # Step 1: Start pod
            if not self.pod_manager.start_pod():
                return None

            # Step 2: Wait for pod to be ready
            if not self.pod_manager.wait_for_ready():
                return None

            # Step 3: Generate assets
            results = self.generator.generate_batch(prompts, output_dir=output_dir)

            # Check if any assets were generated
            success_count = sum(1 for v in results.values() if v)
            if success_count == 0:
                logger.error("No assets were generated successfully")
                return None

            # Step 4: Wait for generation to complete
            logger.info("Waiting for asset generation to complete...")
            time.sleep(60)  # Allow time for all assets to be written

            # Step 5: Create archive
            archive_path = self.archiver.zip_assets(output_dir, archive_name)

            if archive_path:
                # Create metadata
                metadata = {
                    "prompts": prompts,
                    "total_prompts": len(prompts),
                    "successful": success_count,
                    "failed": len(prompts) - success_count,
                    "results": results,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                self.archiver.create_metadata(archive_path, metadata)

            logger.info("=" * 60)
            logger.info("Asset Generation Pipeline Complete")
            logger.info(f"Archive: {archive_path}")
            logger.info("=" * 60)

            return archive_path

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return None

        finally:
            if auto_stop:
                self.pod_manager.stop_pod()


def main():
    """Example usage"""
    runner = AssetRunner()

    prompts = [
        "fantasy potion icons, vibrant colors, game UI style",
        "sci-fi HUD icons, neon glow, futuristic",
        "magic spellbook icons, mystical, arcane symbols",
        "medieval weapon icons, detailed, RPG style",
        "nature element icons, earth fire water air"
    ]

    archive = runner.run(
        prompts=prompts,
        archive_name="fantasy_icon_pack.zip",
        auto_stop=True
    )

    if archive:
        print(f"\n✓ Success! Archive created at: {archive}")
    else:
        print("\n✗ Failed to generate assets")


if __name__ == "__main__":
    main()

"""
AIM Directory Monitoring System
Watches directories for new images and automatically processes them
"""
import os
import time
from pathlib import Path
from typing import List, Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
import json
from datetime import datetime

from app.aim_proofing import AIMProofingEngine, ProofingResult, load_config
from app.aim_ai_analysis import AIImageAnalyzer
from app.state import StateManager


class ImageEventHandler(FileSystemEventHandler):
    """Handles file system events for new images"""

    def __init__(self, aim_engine: 'AIMMonitor'):
        self.aim_engine = aim_engine
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

    def on_created(self, event):
        """Called when a new file is created"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if it's an image
        if file_path.suffix.lower() in self.image_extensions:
            print(f"📸 New image detected: {file_path.name}")
            # Wait a bit to ensure file is fully written
            time.sleep(1)
            self.aim_engine.process_image(str(file_path))


class AIMMonitor:
    """
    AIM (Automated Image Manipulation) Monitoring System
    Watches directories and automatically processes new images
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        state_manager: Optional[StateManager] = None
    ):
        """
        Initialize AIM Monitor

        Args:
            config_path: Path to AIM configuration file
            state_manager: POD Gateway state manager for integration
        """
        # Load configuration
        config_data = load_config(config_path) if config_path else None

        # Initialize components
        self.proofing_engine = AIMProofingEngine(config_data)
        self.ai_analyzer = AIImageAnalyzer()
        self.state_manager = state_manager
        self.config = config_data or self.proofing_engine.config

        # Monitoring state
        self.observers = []
        self.processed_images = set()
        self.results_cache = {}

        # Results directory
        self.results_dir = Path("aim_results")
        self.results_dir.mkdir(exist_ok=True)

    def add_watch_directory(self, directory: str):
        """
        Add directory to watch list

        Args:
            directory: Directory path to monitor
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            print(f"⚠️  Directory does not exist: {directory}")
            print(f"    Creating directory: {directory}")
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"    Failed to create directory: {e}")
                return

        print(f"👁️  Watching directory: {directory}")

        # Create observer
        event_handler = ImageEventHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(dir_path), recursive=False)
        observer.start()

        self.observers.append(observer)

    def process_image(self, image_path: str) -> Optional[ProofingResult]:
        """
        Process a single image through AIM pipeline

        Args:
            image_path: Path to image file

        Returns:
            ProofingResult or None if already processed
        """
        image_path = str(Path(image_path).resolve())

        # Skip if already processed
        if image_path in self.processed_images:
            return None

        print(f"\n{'='*60}")
        print(f"🔍 Processing: {Path(image_path).name}")
        print(f"{'='*60}")

        try:
            # 1. Quality Analysis
            print("📊 Running quality checks...")
            result = self.proofing_engine.analyze_image(image_path)

            print(f"   Quality Score: {result.quality_score.overall_score}/100")
            print(f"   Initial Decision: {result.decision}")

            # 2. AI Analysis (if enabled)
            if self._should_run_ai_analysis():
                print("🤖 Running AI analysis...")
                ai_result = self.ai_analyzer.analyze_image(image_path)

                if ai_result:
                    result.ai_analysis = ai_result
                    print(f"   Commercial Score: {ai_result.get('commercial_suitability', 'N/A')}/100")
                    print(f"   AI Recommendation: {ai_result.get('recommendation', 'N/A')}")

                    # Update decision based on AI
                    result.decision = self._make_final_decision(result)

            # 3. Integration with POD Gateway
            if self.state_manager and self._integration_enabled():
                self._update_gateway_state(result)

            # 4. Save results
            self._save_result(result)

            # 5. Take action based on decision
            self._execute_decision(result, image_path)

            # Mark as processed
            self.processed_images.add(image_path)
            self.results_cache[image_path] = result

            print(f"✅ Final Decision: {result.decision}")
            print(f"{'='*60}\n")

            return result

        except Exception as e:
            print(f"❌ Error processing {image_path}: {e}")
            return None

    def _should_run_ai_analysis(self) -> bool:
        """Check if AI analysis should be run"""
        if not self.ai_analyzer.is_available():
            return False

        ai_config = self.config.get('ai_analysis', {})
        return ai_config.get('enabled', False)

    def _make_final_decision(self, result: ProofingResult) -> str:
        """
        Make final decision combining quality and AI analysis

        Args:
            result: Proofing result with quality and AI data

        Returns:
            Final decision string
        """
        quality_score = result.quality_score.overall_score
        ai_analysis = result.ai_analysis

        auto_approval_config = self.config.get('auto_approval', {})
        auto_reject_config = self.config.get('auto_rejection', {})

        # Check auto-rejection criteria
        if auto_reject_config.get('enabled', False):
            if quality_score <= auto_reject_config.get('max_score', 40):
                return "auto_reject"

        # Check AI safety
        if ai_analysis:
            if not ai_analysis.get('content_safety', True):
                return "auto_reject"

            # AI recommendation override
            ai_rec = ai_analysis.get('recommendation', '').lower()
            if ai_rec == 'reject':
                return "auto_reject"

        # Check auto-approval criteria
        if auto_approval_config.get('enabled', False):
            min_quality = auto_approval_config.get('min_score', 85)

            if quality_score >= min_quality:
                # Check if AI analysis is required
                if auto_approval_config.get('require_ai_analysis', False):
                    if ai_analysis:
                        min_commercial = auto_approval_config.get('ai_min_commercial_score', 75)
                        commercial_score = ai_analysis.get('commercial_suitability', 0)

                        if commercial_score >= min_commercial:
                            return "auto_approve"
                else:
                    return "auto_approve"

        # Default to manual review
        return "manual_review"

    def _integration_enabled(self) -> bool:
        """Check if POD Gateway integration is enabled"""
        integration = self.config.get('integration', {})
        return integration.get('pod_gateway_enabled', False)

    def _update_gateway_state(self, result: ProofingResult):
        """
        Update POD Gateway state with AIM results

        Args:
            result: Proofing result
        """
        if not self.state_manager:
            return

        try:
            # Map AIM decision to gateway status
            status_map = {
                "auto_approve": "approved",
                "auto_reject": "rejected",
                "manual_review": "pending"
            }

            gateway_status = status_map.get(result.decision, "pending")

            # Add image to gateway state
            self.state_manager.add_image(
                result.image_id,
                result.filename,
                f"path/to/{result.filename}"
            )

            # Update status
            self.state_manager.set_image_status(result.image_id, gateway_status)

            # Add AIM metadata
            metadata = {
                "aim_quality_score": result.quality_score.overall_score,
                "aim_decision": result.decision,
                "aim_processed": result.timestamp
            }

            if result.ai_analysis:
                metadata["aim_ai_score"] = result.ai_analysis.get('commercial_suitability')
                metadata["aim_suggested_title"] = result.ai_analysis.get('suggested_title')

            self.state_manager.set_image_status(
                result.image_id,
                gateway_status,
                metadata
            )

            print(f"   ✓ Updated gateway state: {gateway_status}")

        except Exception as e:
            print(f"   ⚠️  Gateway integration error: {e}")

    def _save_result(self, result: ProofingResult):
        """Save analysis result to file"""
        result_file = self.results_dir / f"{result.image_id}_analysis.json"

        result_data = {
            "image_id": result.image_id,
            "filename": result.filename,
            "timestamp": result.timestamp,
            "decision": result.decision,
            "quality_score": {
                "overall": result.quality_score.overall_score,
                "resolution": result.quality_score.resolution_score,
                "filesize": result.quality_score.filesize_score,
                "format": result.quality_score.format_score,
                "aspect_ratio": result.quality_score.aspect_ratio_score,
                "corruption": result.quality_score.corruption_score,
                "issues": result.quality_score.issues,
                "recommendations": result.quality_score.recommendations,
                "metadata": result.quality_score.metadata
            },
            "ai_analysis": result.ai_analysis
        }

        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)

    def _execute_decision(self, result: ProofingResult, image_path: str):
        """
        Execute actions based on decision

        Args:
            result: Proofing result
            image_path: Path to image file
        """
        decision = result.decision

        if decision == "auto_approve":
            print(f"   ✓ Auto-approved for publishing")

        elif decision == "auto_reject":
            print(f"   ✗ Auto-rejected")
            # Optionally archive rejected images
            if self.config.get('monitoring', {}).get('archive_rejected', False):
                self._archive_image(image_path, "rejected")

        else:  # manual_review
            print(f"   ⏸️  Requires manual review")

    def _archive_image(self, image_path: str, category: str):
        """Archive image to category folder"""
        try:
            archive_dir = Path("aim_archive") / category
            archive_dir.mkdir(parents=True, exist_ok=True)

            source = Path(image_path)
            dest = archive_dir / source.name

            # Copy instead of move to preserve original
            import shutil
            shutil.copy2(source, dest)

            print(f"   📦 Archived to: {dest}")

        except Exception as e:
            print(f"   ⚠️  Archive failed: {e}")

    def scan_existing_images(self, directories: Optional[List[str]] = None):
        """
        Scan and process existing images in directories

        Args:
            directories: List of directories to scan (uses config if None)
        """
        if directories is None:
            directories = self.config.get('watch_directories', [])

        print(f"\n🔎 Scanning existing images...")

        total_processed = 0

        for directory in directories:
            dir_path = Path(directory)

            if not dir_path.exists():
                print(f"⚠️  Directory not found: {directory}")
                continue

            print(f"\n📁 Scanning: {directory}")

            # Find all image files
            image_files = []
            for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                image_files.extend(dir_path.glob(f"*{ext}"))

            print(f"   Found {len(image_files)} images")

            # Process each image
            for image_file in image_files:
                self.process_image(str(image_file))
                total_processed += 1

        print(f"\n✅ Processed {total_processed} images")

    def start_monitoring(self, directories: Optional[List[str]] = None):
        """
        Start monitoring directories

        Args:
            directories: List of directories to watch (uses config if None)
        """
        if directories is None:
            directories = self.config.get('watch_directories', [])

        print("\n🚀 AIM Proofing Engine Starting...")
        print(f"{'='*60}")

        # Add watchers
        for directory in directories:
            self.add_watch_directory(directory)

        # Process existing images first
        monitoring_config = self.config.get('monitoring', {})
        if monitoring_config.get('auto_process_new_images', True):
            self.scan_existing_images(directories)

        print(f"\n✓ AIM Engine is now monitoring {len(directories)} directories")
        print("  Press Ctrl+C to stop\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping AIM Engine...")
            self.stop_monitoring()

    def stop_monitoring(self):
        """Stop all directory observers"""
        for observer in self.observers:
            observer.stop()
            observer.join()

        print("✓ Monitoring stopped")

    def get_statistics(self) -> Dict:
        """Get processing statistics"""
        results = list(self.results_cache.values())

        if not results:
            return {
                "total_processed": 0,
                "auto_approved": 0,
                "auto_rejected": 0,
                "manual_review": 0
            }

        auto_approved = len([r for r in results if r.decision == "auto_approve"])
        auto_rejected = len([r for r in results if r.decision == "auto_reject"])
        manual_review = len([r for r in results if r.decision == "manual_review"])

        avg_quality = sum(r.quality_score.overall_score for r in results) / len(results)

        return {
            "total_processed": len(results),
            "auto_approved": auto_approved,
            "auto_rejected": auto_rejected,
            "manual_review": manual_review,
            "average_quality_score": round(avg_quality, 2),
            "approval_rate": round((auto_approved / len(results) * 100), 2)
        }

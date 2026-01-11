"""File system watcher for ComfyUI output directory."""

import os
import time
from pathlib import Path
from typing import Optional, Callable, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


class ComfyUIWatcher(FileSystemEventHandler):
    """Watch ComfyUI output directory for new designs."""

    def __init__(
        self,
        watch_dir: str,
        callback: Callable[[str], None],
        extensions: Optional[List[str]] = None,
        debounce_seconds: float = 2.0,
    ):
        """
        Initialize watcher.

        Args:
            watch_dir: Directory to watch
            callback: Function to call when new file is detected
            extensions: List of file extensions to watch (default: ['.png', '.jpg', '.jpeg'])
            debounce_seconds: Seconds to wait before processing (to ensure file is fully written)
        """
        super().__init__()
        self.watch_dir = watch_dir
        self.callback = callback
        self.extensions = extensions or ['.png', '.jpg', '.jpeg', '.webp']
        self.debounce_seconds = debounce_seconds
        self.processed_files = set()

        # Ensure watch directory exists
        Path(watch_dir).mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        """Handle file creation event."""
        if event.is_directory:
            return

        file_path = event.src_path

        # Check if file has valid extension
        if not any(file_path.lower().endswith(ext) for ext in self.extensions):
            return

        # Check if already processed
        if file_path in self.processed_files:
            return

        print(f"📁 New file detected: {file_path}")

        # Debounce: wait for file to be fully written
        time.sleep(self.debounce_seconds)

        # Verify file still exists and has size > 0
        if not self._is_valid_file(file_path):
            print(f"   ⚠️  File not valid or was deleted")
            return

        # Mark as processed
        self.processed_files.add(file_path)

        # Process the file
        try:
            print(f"   ✅ Processing...")
            self.callback(file_path)
        except Exception as e:
            print(f"   ❌ Processing failed: {e}")
            # Remove from processed so it can be retried
            self.processed_files.discard(file_path)

    def _is_valid_file(self, file_path: str) -> bool:
        """Check if file is valid and ready to process."""
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            if path.stat().st_size == 0:
                return False
            return True
        except Exception:
            return False


def start_watcher(
    watch_dir: str,
    callback: Callable[[str], None],
    run_once: bool = False,
) -> Optional[Observer]:
    """
    Start watching directory for new files.

    Args:
        watch_dir: Directory to watch
        callback: Function to call for each new file
        run_once: If True, process existing files and exit (don't watch)

    Returns:
        Observer instance if watching, None if run_once
    """
    watch_dir = os.path.expanduser(watch_dir)

    if not os.path.exists(watch_dir):
        print(f"Creating watch directory: {watch_dir}")
        os.makedirs(watch_dir, exist_ok=True)

    if run_once:
        # Process existing files once
        print(f"Processing existing files in {watch_dir}...")
        handler = ComfyUIWatcher(watch_dir, callback)

        for ext in handler.extensions:
            for file_path in Path(watch_dir).glob(f"*{ext}"):
                print(f"Found: {file_path}")
                try:
                    callback(str(file_path))
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

        return None

    # Start continuous watching
    print(f"👁️  Starting watcher on: {watch_dir}")
    print(f"   Watching for: {', '.join(ComfyUIWatcher(watch_dir, callback).extensions)}")

    event_handler = ComfyUIWatcher(watch_dir, callback)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()

    print(f"   ✅ Watcher started")

    return observer


def watch_and_process(
    watch_dir: str,
    callback: Callable[[str], None],
    run_once: bool = False,
):
    """
    Watch directory and process files. Blocks until interrupted.

    Args:
        watch_dir: Directory to watch
        callback: Function to call for each new file
        run_once: If True, process existing files and exit
    """
    observer = start_watcher(watch_dir, callback, run_once=run_once)

    if observer is None:
        # run_once mode, already processed
        return

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️  Stopping watcher...")
        observer.stop()

    observer.join()
    print("✅ Watcher stopped")


if __name__ == "__main__":
    # Example usage
    def example_callback(file_path: str):
        print(f"Would process: {file_path}")

    watch_dir = os.environ.get("COMFYUI_OUTPUT_DIR", "/data/comfyui/output")

    print("ComfyUI Output Watcher")
    print("=" * 50)
    print(f"Watch directory: {watch_dir}")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    watch_and_process(watch_dir, example_callback)

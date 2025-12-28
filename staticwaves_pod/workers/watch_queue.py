"""
Queue watcher for StaticWaves POD
Monitors incoming queue and triggers processing
"""
import time
from pathlib import Path
from core.logger import get_logger

log = get_logger("QUEUE_WATCHER")

QUEUE_DIR = Path("queues/incoming")

def watch():
    log.info("Watching queue for new designs...")
    while True:
        files = list(QUEUE_DIR.glob("*.png"))
        if files:
            log.info(f"Found {len(files)} files in queue")
        time.sleep(5)

if __name__ == "__main__":
    watch()

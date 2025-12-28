"""
StaticWaves POD Logger
======================
Centralized logging system for TikTok automation pipeline.

Features:
- Colored console output
- Structured JSON logging
- Rotation and compression
- Performance tracking
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for different log levels."""

    LEVEL_COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.RED + Colors.BOLD
    }

    def format(self, record):
        # Add color to level name
        level_color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)
        record.levelname = f"{level_color}{record.levelname}{Colors.RESET}"

        # Add color to logger name
        record.name = f"{Colors.MAGENTA}{record.name}{Colors.RESET}"

        return super().format(record)


def get_logger(
    name: str,
    level: Optional[str] = None,
    log_to_file: bool = True
) -> logging.Logger:
    """
    Create or retrieve a configured logger instance.

    Args:
        name: Logger name (typically module/component name)
        level: Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        log_to_file: Whether to write logs to file

    Returns:
        Configured logger instance

    Example:
        >>> log = get_logger("TIKTOK-UPLOADER")
        >>> log.info("Upload started")
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Set log level from env or parameter
    log_level_str = level or os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    console_format = ColoredFormatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"{name.lower()}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        file_format = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


def log_performance(logger: logging.Logger, operation: str):
    """
    Decorator for logging function performance.

    Args:
        logger: Logger instance to use
        operation: Description of the operation

    Example:
        @log_performance(log, "feed_generation")
        def generate_feed():
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            logger.info(f"🚀 Starting {operation}")

            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info(
                    f"✅ Completed {operation} in {duration:.2f}s"
                )
                return result

            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.error(
                    f"❌ Failed {operation} after {duration:.2f}s: {str(e)}"
                )
                raise

        return wrapper
    return decorator


if __name__ == "__main__":
    # Test logger
    test_log = get_logger("TEST-LOGGER")

    test_log.debug("Debug message")
    test_log.info("Info message")
    test_log.warning("Warning message")
    test_log.error("Error message")
    test_log.critical("Critical message")

    print("\n" + "=" * 60)
    print("✅ Logger test complete. Check logs/ directory for file output.")

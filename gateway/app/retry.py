"""
Retry logic with exponential backoff for external API calls
"""
import time
import logging
from typing import Callable, Any, Optional
from functools import wraps
import random

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior"""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )

        # Add jitter
        if self.jitter:
            delay = delay * (0.5 + random.random())

        return delay


def retry_with_backoff(
    config: RetryConfig = None,
    exceptions: tuple = (Exception,),
    on_retry: Callable[[Exception, int], None] = None
):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        config: Retry configuration (uses default if None)
        exceptions: Tuple of exception types to catch
        on_retry: Optional callback called on each retry

    Example:
        @retry_with_backoff(
            config=RetryConfig(max_attempts=3),
            exceptions=(requests.RequestException,)
        )
        def call_external_api():
            response = requests.get('https://api.example.com')
            response.raise_for_status()
            return response.json()
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt < config.max_attempts - 1:
                        delay = config.get_delay(attempt)

                        logger.warning(
                            f"Attempt {attempt + 1}/{config.max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )

                        # Call retry callback if provided
                        if on_retry:
                            on_retry(e, attempt)

                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {config.max_attempts} attempts failed for {func.__name__}: {e}"
                        )

            # All attempts failed, raise last exception
            raise last_exception

        return wrapper
    return decorator


class AsyncRetryManager:
    """
    Manager for handling async retries.

    Useful for operations that need to be retried later
    (e.g., failed webhook deliveries, sync checks)
    """

    def __init__(self):
        self.pending_retries = []
        self.max_queue_size = 1000

    def schedule_retry(
        self,
        operation: Callable,
        retry_at: float,
        max_retries: int = 3,
        current_attempt: int = 0,
        metadata: dict = None
    ):
        """
        Schedule operation for retry.

        Args:
            operation: Function to retry
            retry_at: Timestamp when to retry
            max_retries: Maximum retry attempts
            current_attempt: Current attempt number
            metadata: Optional metadata for tracking
        """
        if len(self.pending_retries) >= self.max_queue_size:
            logger.warning("Retry queue full, dropping retry")
            return

        self.pending_retries.append({
            'operation': operation,
            'retry_at': retry_at,
            'max_retries': max_retries,
            'current_attempt': current_attempt,
            'metadata': metadata or {}
        })

    def process_pending(self):
        """Process pending retries that are due"""
        current_time = time.time()
        remaining = []

        for retry in self.pending_retries:
            if retry['retry_at'] <= current_time:
                # Time to retry
                try:
                    retry['operation']()
                    logger.info(f"Retry successful: {retry.get('metadata')}")

                except Exception as e:
                    # Retry failed
                    attempt = retry['current_attempt'] + 1

                    if attempt < retry['max_retries']:
                        # Schedule another retry
                        delay = 2 ** attempt  # Exponential backoff
                        retry['retry_at'] = current_time + delay
                        retry['current_attempt'] = attempt
                        remaining.append(retry)
                        logger.warning(f"Retry attempt {attempt} failed, will retry in {delay}s")
                    else:
                        logger.error(f"Max retries exceeded: {retry.get('metadata')}")
            else:
                # Not yet due
                remaining.append(retry)

        self.pending_retries = remaining

    def get_stats(self) -> dict:
        """Get retry queue statistics"""
        return {
            'pending_count': len(self.pending_retries),
            'max_queue_size': self.max_queue_size
        }


# Global retry manager
retry_manager = AsyncRetryManager()


# Convenience functions
def retry_api_call(func: Callable, max_attempts: int = 3) -> Any:
    """
    Retry an API call with default configuration.

    Args:
        func: Function to call
        max_attempts: Maximum attempts

    Returns:
        Function result

    Raises:
        Last exception if all attempts fail
    """
    config = RetryConfig(max_attempts=max_attempts)

    @retry_with_backoff(config=config)
    def wrapper():
        return func()

    return wrapper()

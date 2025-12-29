#!/usr/bin/env python3
"""Retry logic with exponential backoff"""
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

def create_retry_decorator(max_attempts=5, min_wait=1, max_wait=30):
    """
    Create a retry decorator with exponential backoff

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds
        max_wait: Maximum wait time in seconds

    Returns:
        Retry decorator
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(min=min_wait, max=max_wait),
        retry=retry_if_exception_type((requests.exceptions.RequestException, ConnectionError))
    )

# Standard retry decorator for API calls
api_retry = create_retry_decorator()

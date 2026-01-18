"""
Image caching layer for performance optimization
"""
import os
import time
import hashlib
import threading
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ImageCache:
    """
    In-memory cache for generated images.

    Caches:
    - Image metadata
    - Generation parameters
    - File paths

    Benefits:
    - Faster image listing
    - Reduced disk I/O
    - Deduplication detection
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize image cache.

        Args:
            max_size: Maximum number of items to cache
            ttl_seconds: Time to live for cache entries
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get item from cache.

        Args:
            key: Cache key

        Returns:
            Cached item or None if not found/expired
        """
        with self.lock:
            if key not in self.cache:
                return None

            entry = self.cache[key]
            cached_at = entry.get('cached_at', 0)

            # Check if expired
            if time.time() - cached_at > self.ttl_seconds:
                del self.cache[key]
                return None

            # Update access time
            entry['accessed_at'] = time.time()
            return entry.get('data')

    def set(self, key: str, data: Dict[str, Any]):
        """
        Set item in cache.

        Args:
            key: Cache key
            data: Data to cache
        """
        with self.lock:
            # Evict oldest if at capacity
            if len(self.cache) >= self.max_size:
                self._evict_oldest()

            self.cache[key] = {
                'data': data,
                'cached_at': time.time(),
                'accessed_at': time.time()
            }

    def invalidate(self, key: str):
        """Remove item from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]

    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()

    def _evict_oldest(self):
        """Evict least recently accessed item"""
        if not self.cache:
            return

        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].get('accessed_at', 0)
        )
        del self.cache[oldest_key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'ttl_seconds': self.ttl_seconds
            }


class PromptHashCache:
    """
    Cache for detecting duplicate prompts.

    Uses hash of prompt parameters to detect when the same
    image generation request has been made before.
    """

    def __init__(self):
        self.cache: Dict[str, str] = {}  # hash -> image_id
        self.lock = threading.Lock()

    def hash_prompt(self, prompt: str, width: int, height: int, steps: int, cfg_scale: float, seed: int = None) -> str:
        """
        Generate hash for prompt parameters.

        Args:
            prompt: Prompt text
            width: Image width
            height: Image height
            steps: Sampling steps
            cfg_scale: CFG scale
            seed: Random seed (if specified)

        Returns:
            Hash string
        """
        # Create canonical representation
        parts = [
            f"prompt:{prompt}",
            f"width:{width}",
            f"height:{height}",
            f"steps:{steps}",
            f"cfg:{cfg_scale:.2f}"
        ]

        if seed is not None:
            parts.append(f"seed:{seed}")

        canonical = "|".join(parts)

        # Generate hash
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    def get_duplicate(self, prompt_hash: str) -> Optional[str]:
        """
        Check if prompt has been generated before.

        Args:
            prompt_hash: Prompt hash

        Returns:
            Image ID if found, None otherwise
        """
        with self.lock:
            return self.cache.get(prompt_hash)

    def record(self, prompt_hash: str, image_id: str):
        """
        Record generated prompt.

        Args:
            prompt_hash: Prompt hash
            image_id: Generated image ID
        """
        with self.lock:
            self.cache[prompt_hash] = image_id

    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()


# Global cache instances
image_cache = ImageCache(max_size=1000, ttl_seconds=3600)
prompt_cache = PromptHashCache()

"""
Rate limiting for API endpoints
"""
import time
from typing import Dict, Tuple
from functools import wraps
from flask import request, jsonify
import threading


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window algorithm.

    Thread-safe implementation for multi-threaded Flask applications.
    """

    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.lock = threading.Lock()

    def _get_client_id(self) -> str:
        """Get client identifier from request"""
        # Try X-Forwarded-For header first (for proxy/load balancer)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()

        # Fall back to remote_addr
        return request.remote_addr or 'unknown'

    def _clean_old_requests(self, client_id: str, window_seconds: int):
        """Remove requests older than the time window"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds

        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > cutoff_time
            ]

    def is_allowed(
        self,
        max_requests: int,
        window_seconds: int,
        client_id: str = None
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is allowed under rate limit.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            client_id: Optional client identifier (uses IP if not provided)

        Returns:
            Tuple of (is_allowed, info_dict)
            info_dict contains: remaining, reset_at, limit
        """
        if client_id is None:
            client_id = self._get_client_id()

        current_time = time.time()

        with self.lock:
            # Clean old requests
            self._clean_old_requests(client_id, window_seconds)

            # Get current request count
            if client_id not in self.requests:
                self.requests[client_id] = []

            request_count = len(self.requests[client_id])

            # Calculate reset time
            if request_count > 0:
                oldest_request = min(self.requests[client_id])
                reset_at = oldest_request + window_seconds
            else:
                reset_at = current_time + window_seconds

            # Check if allowed
            if request_count < max_requests:
                # Add current request
                self.requests[client_id].append(current_time)

                return True, {
                    'limit': max_requests,
                    'remaining': max_requests - request_count - 1,
                    'reset_at': int(reset_at),
                    'reset_in_seconds': int(reset_at - current_time)
                }
            else:
                return False, {
                    'limit': max_requests,
                    'remaining': 0,
                    'reset_at': int(reset_at),
                    'reset_in_seconds': int(reset_at - current_time)
                }

    def reset(self, client_id: str = None):
        """Reset rate limit for a client"""
        if client_id is None:
            client_id = self._get_client_id()

        with self.lock:
            if client_id in self.requests:
                del self.requests[client_id]


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests: int, window_seconds: int):
    """
    Decorator for rate limiting Flask routes.

    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds

    Example:
        @app.route('/api/generate', methods=['POST'])
        @rate_limit(max_requests=10, window_seconds=60)
        def generate_image():
            ...

    Returns 429 Too Many Requests if limit exceeded.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            allowed, info = rate_limiter.is_allowed(max_requests, window_seconds)

            # Add rate limit headers to response
            response_headers = {
                'X-RateLimit-Limit': str(info['limit']),
                'X-RateLimit-Remaining': str(info['remaining']),
                'X-RateLimit-Reset': str(info['reset_at'])
            }

            if not allowed:
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'limit': info['limit'],
                    'reset_in_seconds': info['reset_in_seconds'],
                    'message': f'Rate limit exceeded. Try again in {info["reset_in_seconds"]} seconds.'
                })
                response.status_code = 429
                for key, value in response_headers.items():
                    response.headers[key] = value
                return response

            # Call the actual function
            result = f(*args, **kwargs)

            # Add rate limit headers to successful response
            if hasattr(result, 'headers'):
                for key, value in response_headers.items():
                    result.headers[key] = value

            return result

        return decorated_function
    return decorator


class TieredRateLimiter:
    """
    Multi-tier rate limiter with different limits for different operations.

    Example tiers:
    - Tier 1 (generation): 10 requests/hour
    - Tier 2 (approval/publish): 100 requests/hour
    - Tier 3 (read-only): 1000 requests/hour
    """

    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}

    def get_limiter(self, tier: str) -> RateLimiter:
        """Get or create rate limiter for a tier"""
        if tier not in self.limiters:
            self.limiters[tier] = RateLimiter()
        return self.limiters[tier]

    def check_limit(
        self,
        tier: str,
        max_requests: int,
        window_seconds: int,
        client_id: str = None
    ) -> Tuple[bool, Dict[str, any]]:
        """Check rate limit for a specific tier"""
        limiter = self.get_limiter(tier)
        return limiter.is_allowed(max_requests, window_seconds, client_id)


# Global tiered rate limiter
tiered_limiter = TieredRateLimiter()


# Predefined rate limits for different endpoint types
RATE_LIMITS = {
    'generation': {
        'max_requests': 10,
        'window_seconds': 3600,  # 10 per hour
        'description': 'Image generation endpoints'
    },
    'publishing': {
        'max_requests': 50,
        'window_seconds': 3600,  # 50 per hour
        'description': 'Publishing endpoints'
    },
    'approval': {
        'max_requests': 100,
        'window_seconds': 3600,  # 100 per hour
        'description': 'Approval/rejection endpoints'
    },
    'read': {
        'max_requests': 1000,
        'window_seconds': 3600,  # 1000 per hour
        'description': 'Read-only endpoints'
    }
}


def tiered_rate_limit(tier: str):
    """
    Decorator for tiered rate limiting.

    Args:
        tier: Tier name ('generation', 'publishing', 'approval', 'read')

    Example:
        @app.route('/api/generate', methods=['POST'])
        @tiered_rate_limit('generation')
        def generate_image():
            ...
    """
    if tier not in RATE_LIMITS:
        raise ValueError(f"Unknown rate limit tier: {tier}")

    config = RATE_LIMITS[tier]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            allowed, info = tiered_limiter.check_limit(
                tier,
                config['max_requests'],
                config['window_seconds']
            )

            # Add rate limit headers
            response_headers = {
                'X-RateLimit-Limit': str(info['limit']),
                'X-RateLimit-Remaining': str(info['remaining']),
                'X-RateLimit-Reset': str(info['reset_at']),
                'X-RateLimit-Tier': tier
            }

            if not allowed:
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'tier': tier,
                    'limit': info['limit'],
                    'reset_in_seconds': info['reset_in_seconds'],
                    'message': f'Rate limit exceeded for {tier} tier. Try again in {info["reset_in_seconds"]} seconds.'
                })
                response.status_code = 429
                for key, value in response_headers.items():
                    response.headers[key] = value
                return response

            # Call the actual function
            result = f(*args, **kwargs)

            # Add rate limit headers to successful response
            if hasattr(result, 'headers'):
                for key, value in response_headers.items():
                    result.headers[key] = value

            return result

        return decorated_function
    return decorator

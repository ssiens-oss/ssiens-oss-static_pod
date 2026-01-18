"""
Flask middleware for request/response processing, logging, CORS, etc.
"""
import time
import logging
import uuid
from flask import request, g
from functools import wraps
import json

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware for logging HTTP requests and responses.

    Logs:
    - Request method, path, headers, body
    - Response status, duration
    - Request ID for tracing
    """

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    @staticmethod
    def before_request():
        """Called before each request"""
        # Generate unique request ID
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()

        # Log request
        logger.info(
            f"[{g.request_id}] {request.method} {request.path}",
            extra={
                'request_id': g.request_id,
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'unknown')
            }
        )

        # Log request body for non-GET requests (except large payloads)
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_length = request.content_length or 0
            if content_length > 0 and content_length < 10000:  # Log if < 10KB
                try:
                    body = request.get_json(silent=True)
                    if body:
                        # Redact sensitive fields
                        safe_body = _redact_sensitive_fields(body)
                        logger.debug(
                            f"[{g.request_id}] Request body: {json.dumps(safe_body)}",
                            extra={'request_id': g.request_id}
                        )
                except Exception:
                    pass

    @staticmethod
    def after_request(response):
        """Called after each request"""
        if hasattr(g, 'request_id') and hasattr(g, 'start_time'):
            duration = time.time() - g.start_time

            # Add request ID to response headers
            response.headers['X-Request-ID'] = g.request_id

            # Log response
            logger.info(
                f"[{g.request_id}] {response.status_code} {request.method} {request.path} "
                f"({duration * 1000:.2f}ms)",
                extra={
                    'request_id': g.request_id,
                    'status_code': response.status_code,
                    'duration_ms': duration * 1000,
                    'method': request.method,
                    'path': request.path
                }
            )

        return response


def _redact_sensitive_fields(data: dict) -> dict:
    """Redact sensitive fields from request body"""
    sensitive_keys = [
        'password', 'token', 'secret', 'api_key', 'apikey',
        'access_token', 'refresh_token', 'private_key'
    ]

    redacted = data.copy()
    for key in redacted:
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            redacted[key] = '***REDACTED***'

    return redacted


class CORSMiddleware:
    """
    CORS (Cross-Origin Resource Sharing) middleware.

    Handles preflight OPTIONS requests and adds CORS headers.
    """

    def __init__(
        self,
        app=None,
        origins='*',
        methods=None,
        headers=None,
        max_age=3600
    ):
        self.origins = origins
        self.methods = methods or ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
        self.headers = headers or ['Content-Type', 'Authorization', 'X-Request-ID']
        self.max_age = max_age

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.after_request(self.add_cors_headers)

    def add_cors_headers(self, response):
        """Add CORS headers to response"""
        # Get origin from request
        origin = request.headers.get('Origin')

        # Check if origin is allowed
        if self.origins == '*':
            response.headers['Access-Control-Allow-Origin'] = '*'
        elif origin and origin in self.origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Vary'] = 'Origin'

        # Add other CORS headers
        response.headers['Access-Control-Allow-Methods'] = ', '.join(self.methods)
        response.headers['Access-Control-Allow-Headers'] = ', '.join(self.headers)
        response.headers['Access-Control-Max-Age'] = str(self.max_age)

        # Allow credentials
        response.headers['Access-Control-Allow-Credentials'] = 'true'

        return response


class SecurityHeadersMiddleware:
    """
    Add security headers to responses.

    Headers:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security (if HTTPS)
    """

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.after_request(self.add_security_headers)

    @staticmethod
    def add_security_headers(response):
        """Add security headers to response"""
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'

        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # HSTS (if HTTPS)
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Content Security Policy (basic)
        response.headers['Content-Security-Policy'] = "default-src 'self'"

        return response


class HealthCheckBypassMiddleware:
    """
    Bypass certain middleware for health check endpoints.

    Useful to prevent health checks from triggering rate limits,
    logging noise, etc.
    """

    HEALTH_PATHS = ['/health', '/healthz', '/ping', '/ready']

    @staticmethod
    def is_health_check() -> bool:
        """Check if current request is a health check"""
        return request.path in HealthCheckBypassMiddleware.HEALTH_PATHS


def conditional_middleware(condition_func):
    """
    Decorator to conditionally apply middleware.

    Args:
        condition_func: Function that returns True if middleware should apply

    Example:
        @conditional_middleware(lambda: not HealthCheckBypassMiddleware.is_health_check())
        def my_middleware():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if condition_func():
                return f(*args, **kwargs)
            # Skip middleware, call next in chain
            return None
        return decorated_function
    return decorator


class RequestMetricsCollector:
    """
    Collect request metrics for monitoring.

    Metrics collected:
    - Request count by endpoint
    - Response time by endpoint
    - Status code distribution
    - Error rate
    """

    def __init__(self):
        self.metrics = {
            'request_count': {},
            'response_times': {},
            'status_codes': {},
            'errors': 0
        }

    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """Record request metrics"""
        endpoint = f"{method} {path}"

        # Increment request count
        if endpoint not in self.metrics['request_count']:
            self.metrics['request_count'][endpoint] = 0
        self.metrics['request_count'][endpoint] += 1

        # Record response time
        if endpoint not in self.metrics['response_times']:
            self.metrics['response_times'][endpoint] = []
        self.metrics['response_times'][endpoint].append(duration)

        # Record status code
        if status_code not in self.metrics['status_codes']:
            self.metrics['status_codes'][status_code] = 0
        self.metrics['status_codes'][status_code] += 1

        # Count errors (5xx)
        if status_code >= 500:
            self.metrics['errors'] += 1

    def get_metrics(self) -> dict:
        """Get current metrics"""
        # Calculate averages
        avg_response_times = {}
        for endpoint, times in self.metrics['response_times'].items():
            if times:
                avg_response_times[endpoint] = sum(times) / len(times)

        return {
            'request_count': self.metrics['request_count'],
            'avg_response_times_ms': avg_response_times,
            'status_codes': self.metrics['status_codes'],
            'total_errors': self.metrics['errors']
        }

    def reset(self):
        """Reset all metrics"""
        self.metrics = {
            'request_count': {},
            'response_times': {},
            'status_codes': {},
            'errors': 0
        }


# Global metrics collector
metrics_collector = RequestMetricsCollector()


class MetricsMiddleware:
    """Middleware to collect request metrics"""

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.after_request(self.collect_metrics)

    @staticmethod
    def collect_metrics(response):
        """Collect metrics after request"""
        if hasattr(g, 'start_time') and not HealthCheckBypassMiddleware.is_health_check():
            duration = (time.time() - g.start_time) * 1000  # Convert to ms
            metrics_collector.record_request(
                request.method,
                request.path,
                response.status_code,
                duration
            )
        return response


def setup_middleware(app, enable_cors=True, cors_origins='*'):
    """
    Setup all middleware for the Flask app.

    Args:
        app: Flask application instance
        enable_cors: Whether to enable CORS
        cors_origins: Allowed CORS origins

    Returns:
        Flask app with middleware configured
    """
    # Request logging
    RequestLoggingMiddleware(app)

    # CORS
    if enable_cors:
        CORSMiddleware(app, origins=cors_origins)

    # Security headers
    SecurityHeadersMiddleware(app)

    # Metrics collection
    MetricsMiddleware(app)

    return app

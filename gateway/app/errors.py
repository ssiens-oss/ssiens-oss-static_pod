"""
Comprehensive error handling with standardized error codes
"""
from typing import Dict, Any, Optional
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base class for API errors"""

    def __init__(
        self,
        message: str,
        code: str = "API_ERROR",
        status_code: int = 500,
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response"""
        error_dict = {
            'error': self.message,
            'code': self.code
        }
        if self.details:
            error_dict['details'] = self.details
        return error_dict


class ValidationError(APIError):
    """Validation error (400)"""

    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details or {}
        )
        if field:
            self.details['field'] = field


class NotFoundError(APIError):
    """Resource not found (404)"""

    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} '{identifier}' not found"

        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details={'resource': resource, 'identifier': identifier}
        )


class ConflictError(APIError):
    """Resource conflict (409)"""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            details=details
        )


class UnauthorizedError(APIError):
    """Unauthorized access (401)"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401
        )


class ForbiddenError(APIError):
    """Forbidden access (403)"""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403
        )


class RateLimitError(APIError):
    """Rate limit exceeded (429)"""

    def __init__(self, reset_in_seconds: int):
        super().__init__(
            message=f"Rate limit exceeded. Try again in {reset_in_seconds} seconds.",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={'reset_in_seconds': reset_in_seconds}
        )


class ExternalServiceError(APIError):
    """External service error (502)"""

    def __init__(self, service: str, message: str = None):
        super().__init__(
            message=message or f"{service} service unavailable",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details={'service': service}
        )


class InternalServerError(APIError):
    """Internal server error (500)"""

    def __init__(self, message: str = "Internal server error", details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            code="INTERNAL_SERVER_ERROR",
            status_code=500,
            details=details
        )


def register_error_handlers(app):
    """
    Register error handlers for Flask app.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        """Handle custom API errors"""
        logger.error(f"API Error ({error.code}): {error.message}", exc_info=True)
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors"""
        response = jsonify({
            'error': 'Endpoint not found',
            'code': 'ENDPOINT_NOT_FOUND',
            'path': str(error)
        })
        response.status_code = 404
        return response

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors"""
        response = jsonify({
            'error': 'Method not allowed',
            'code': 'METHOD_NOT_ALLOWED'
        })
        response.status_code = 405
        return response

    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal Server Error: {error}", exc_info=True)
        response = jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_SERVER_ERROR'
        })
        response.status_code = 500
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected errors"""
        logger.error(f"Unexpected Error: {error}", exc_info=True)
        response = jsonify({
            'error': 'An unexpected error occurred',
            'code': 'UNEXPECTED_ERROR'
        })
        response.status_code = 500
        return response


# Common error response builders
def error_response(
    message: str,
    code: str = "ERROR",
    status_code: int = 400,
    **kwargs
) -> tuple:
    """
    Build error response tuple.

    Args:
        message: Error message
        code: Error code
        status_code: HTTP status code
        **kwargs: Additional fields to include in response

    Returns:
        Tuple of (jsonify response, status_code)
    """
    response_data = {
        'error': message,
        'code': code
    }
    response_data.update(kwargs)

    return jsonify(response_data), status_code


def success_response(
    data: Dict[str, Any] = None,
    message: str = None,
    status_code: int = 200
) -> tuple:
    """
    Build success response tuple.

    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code

    Returns:
        Tuple of (jsonify response, status_code)
    """
    response_data = {'success': True}

    if message:
        response_data['message'] = message

    if data:
        response_data.update(data)

    return jsonify(response_data), status_code

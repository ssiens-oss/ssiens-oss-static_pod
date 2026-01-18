"""
Request validation and input sanitization utilities
"""
from typing import Dict, Any, Tuple, Optional, List
import re
from functools import wraps
from flask import request, jsonify


class ValidationError(Exception):
    """Raised when validation fails"""
    def __init__(self, message: str, field: str = None, code: str = "VALIDATION_ERROR"):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)


def sanitize_string(value: str, max_length: int = 1000, allow_newlines: bool = False) -> str:
    """
    Sanitize string input.

    Args:
        value: Input string
        max_length: Maximum allowed length
        allow_newlines: Whether to allow newline characters

    Returns:
        Sanitized string

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError("Value must be a string", code="INVALID_TYPE")

    # Trim whitespace
    value = value.strip()

    # Remove null bytes
    value = value.replace('\x00', '')

    # Remove newlines if not allowed
    if not allow_newlines:
        value = value.replace('\n', ' ').replace('\r', ' ')

    # Check length
    if len(value) > max_length:
        raise ValidationError(
            f"String too long (max {max_length} characters)",
            code="STRING_TOO_LONG"
        )

    return value


def validate_prompt(prompt: str) -> str:
    """
    Validate and sanitize prompt text.

    Args:
        prompt: Prompt text

    Returns:
        Sanitized prompt

    Raises:
        ValidationError: If validation fails
    """
    prompt = sanitize_string(prompt, max_length=2000, allow_newlines=False)

    if len(prompt) == 0:
        raise ValidationError("Prompt cannot be empty", field="prompt", code="EMPTY_PROMPT")

    if len(prompt) < 3:
        raise ValidationError(
            "Prompt too short (minimum 3 characters)",
            field="prompt",
            code="PROMPT_TOO_SHORT"
        )

    # Check for suspicious patterns (basic XSS prevention)
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            raise ValidationError(
                "Prompt contains potentially dangerous content",
                field="prompt",
                code="DANGEROUS_CONTENT"
            )

    return prompt


def validate_integer(
    value: Any,
    field: str,
    min_value: int = None,
    max_value: int = None,
    default: int = None
) -> int:
    """
    Validate integer input.

    Args:
        value: Value to validate
        field: Field name (for error messages)
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        default: Default value if None

    Returns:
        Validated integer

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        if default is not None:
            return default
        raise ValidationError(f"{field} is required", field=field, code="REQUIRED_FIELD")

    if not isinstance(value, int):
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(
                f"{field} must be an integer",
                field=field,
                code="INVALID_INTEGER"
            )

    if min_value is not None and value < min_value:
        raise ValidationError(
            f"{field} must be at least {min_value}",
            field=field,
            code="VALUE_TOO_SMALL"
        )

    if max_value is not None and value > max_value:
        raise ValidationError(
            f"{field} must be at most {max_value}",
            field=field,
            code="VALUE_TOO_LARGE"
        )

    return value


def validate_float(
    value: Any,
    field: str,
    min_value: float = None,
    max_value: float = None,
    default: float = None
) -> float:
    """
    Validate float input.

    Args:
        value: Value to validate
        field: Field name (for error messages)
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        default: Default value if None

    Returns:
        Validated float

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        if default is not None:
            return default
        raise ValidationError(f"{field} is required", field=field, code="REQUIRED_FIELD")

    if not isinstance(value, (int, float)):
        try:
            value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(
                f"{field} must be a number",
                field=field,
                code="INVALID_FLOAT"
            )

    if min_value is not None and value < min_value:
        raise ValidationError(
            f"{field} must be at least {min_value}",
            field=field,
            code="VALUE_TOO_SMALL"
        )

    if max_value is not None and value > max_value:
        raise ValidationError(
            f"{field} must be at most {max_value}",
            field=field,
            code="VALUE_TOO_LARGE"
        )

    return value


def validate_enum(
    value: Any,
    field: str,
    allowed_values: List[str],
    default: str = None,
    case_sensitive: bool = False
) -> str:
    """
    Validate enum/choice input.

    Args:
        value: Value to validate
        field: Field name (for error messages)
        allowed_values: List of allowed values
        default: Default value if None
        case_sensitive: Whether to enforce case sensitivity

    Returns:
        Validated value

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        if default is not None:
            return default
        raise ValidationError(f"{field} is required", field=field, code="REQUIRED_FIELD")

    if not isinstance(value, str):
        value = str(value)

    # Normalize for comparison
    compare_value = value if case_sensitive else value.lower()
    compare_allowed = allowed_values if case_sensitive else [v.lower() for v in allowed_values]

    if compare_value not in compare_allowed:
        raise ValidationError(
            f"{field} must be one of: {', '.join(allowed_values)}",
            field=field,
            code="INVALID_ENUM_VALUE"
        )

    # Return original case from allowed_values if not case-sensitive
    if not case_sensitive:
        idx = compare_allowed.index(compare_value)
        return allowed_values[idx]

    return value


def validate_image_id(image_id: str) -> str:
    """
    Validate image ID format.

    Args:
        image_id: Image ID to validate

    Returns:
        Validated image ID

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(image_id, str):
        raise ValidationError("Image ID must be a string", field="image_id", code="INVALID_TYPE")

    # Allow alphanumeric, underscore, hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', image_id):
        raise ValidationError(
            "Image ID contains invalid characters",
            field="image_id",
            code="INVALID_IMAGE_ID"
        )

    if len(image_id) > 100:
        raise ValidationError(
            "Image ID too long (max 100 characters)",
            field="image_id",
            code="IMAGE_ID_TOO_LONG"
        )

    return image_id


def validate_batch_id(batch_id: str) -> str:
    """
    Validate batch ID format.

    Args:
        batch_id: Batch ID to validate

    Returns:
        Validated batch ID

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(batch_id, str):
        raise ValidationError("Batch ID must be a string", field="batch_id", code="INVALID_TYPE")

    # Must start with "batch_"
    if not batch_id.startswith("batch_"):
        raise ValidationError(
            "Batch ID must start with 'batch_'",
            field="batch_id",
            code="INVALID_BATCH_ID"
        )

    # Rest should be alphanumeric
    suffix = batch_id[6:]  # Remove "batch_" prefix
    if not re.match(r'^[a-zA-Z0-9]+$', suffix):
        raise ValidationError(
            "Batch ID contains invalid characters",
            field="batch_id",
            code="INVALID_BATCH_ID"
        )

    return batch_id


def validate_request_json(required_fields: List[str] = None) -> callable:
    """
    Decorator to validate that request has valid JSON and required fields.

    Args:
        required_fields: List of required field names

    Example:
        @app.route('/api/endpoint', methods=['POST'])
        @validate_request_json(required_fields=['prompt', 'style'])
        def endpoint():
            data = request.get_json()
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check Content-Type
            if not request.is_json:
                return jsonify({
                    "error": "Content-Type must be application/json",
                    "code": "INVALID_CONTENT_TYPE"
                }), 400

            # Parse JSON
            data = request.get_json(silent=True)
            if data is None:
                return jsonify({
                    "error": "Invalid JSON in request body",
                    "code": "INVALID_JSON"
                }), 400

            # Check required fields
            if required_fields:
                missing = [field for field in required_fields if field not in data]
                if missing:
                    return jsonify({
                        "error": f"Missing required fields: {', '.join(missing)}",
                        "code": "MISSING_REQUIRED_FIELDS",
                        "missing_fields": missing
                    }), 400

            return f(*args, **kwargs)
        return decorated_function
    return decorator


class GenerateRequestValidator:
    """Validator for /api/generate requests"""

    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Tuple]]:
        """
        Validate generate request data.

        Args:
            data: Request data

        Returns:
            Tuple of (validated_data, error_response)
            If validation passes, error_response is None
            If validation fails, error_response is (json, status_code)
        """
        try:
            validated = {}

            # Validate prompt (required)
            if "prompt" not in data:
                raise ValidationError("Prompt is required", field="prompt", code="REQUIRED_FIELD")
            validated["prompt"] = validate_prompt(data["prompt"])

            # Validate optional strings
            validated["style"] = sanitize_string(
                data.get("style", ""),
                max_length=200
            ) if data.get("style") else ""

            validated["genre"] = sanitize_string(
                data.get("genre", ""),
                max_length=200
            ) if data.get("genre") else ""

            # Validate batch_size
            validated["batch_size"] = validate_integer(
                data.get("batch_size", 1),
                "batch_size",
                min_value=1,
                max_value=25,
                default=1
            )

            # Validate dimensions
            validated["width"] = validate_integer(
                data.get("width", 4500),
                "width",
                min_value=512,
                max_value=8192,
                default=4500
            )

            validated["height"] = validate_integer(
                data.get("height", 5400),
                "height",
                min_value=512,
                max_value=8192,
                default=5400
            )

            # Validate sampling parameters
            validated["steps"] = validate_integer(
                data.get("steps", 30),
                "steps",
                min_value=10,
                max_value=100,
                default=30
            )

            validated["cfg_scale"] = validate_float(
                data.get("cfg_scale", 2.0),
                "cfg_scale",
                min_value=0.1,
                max_value=20.0,
                default=2.0
            )

            # Validate seed (optional)
            if "seed" in data and data["seed"] is not None:
                validated["seed"] = validate_integer(
                    data["seed"],
                    "seed",
                    min_value=0,
                    max_value=2**32 - 1
                )
            else:
                validated["seed"] = None

            # Validate client_id (optional)
            if "client_id" in data and data["client_id"]:
                validated["client_id"] = sanitize_string(
                    data["client_id"],
                    max_length=100
                )
            else:
                validated["client_id"] = None

            return validated, None

        except ValidationError as e:
            error_response = jsonify({
                "error": e.message,
                "code": e.code,
                "field": e.field
            }), 400
            return None, error_response


class PublishRequestValidator:
    """Validator for /api/publish requests"""

    VALID_PLATFORMS = ["printify", "zazzle", "redbubble"]

    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Tuple]]:
        """
        Validate publish request data.

        Args:
            data: Request data

        Returns:
            Tuple of (validated_data, error_response)
        """
        try:
            validated = {}

            # Validate title (optional, auto-generated if not provided)
            if data.get("title"):
                validated["title"] = sanitize_string(
                    data["title"],
                    max_length=200
                )
            else:
                validated["title"] = ""

            # Validate description (optional)
            if data.get("description"):
                validated["description"] = sanitize_string(
                    data["description"],
                    max_length=5000,
                    allow_newlines=True
                )
            else:
                validated["description"] = ""

            # Validate product_type (required)
            if "product_type" not in data:
                raise ValidationError(
                    "product_type is required",
                    field="product_type",
                    code="REQUIRED_FIELD"
                )

            validated["product_type"] = sanitize_string(
                data["product_type"],
                max_length=100
            )

            # Validate platform
            validated["platform"] = validate_enum(
                data.get("platform", "printify"),
                "platform",
                allowed_values=PublishRequestValidator.VALID_PLATFORMS,
                default="printify",
                case_sensitive=False
            )

            # Validate price (optional)
            if "price_cents" in data and data["price_cents"] is not None:
                validated["price_cents"] = validate_integer(
                    data["price_cents"],
                    "price_cents",
                    min_value=100,  # $1.00 minimum
                    max_value=100000  # $1000.00 maximum
                )
            else:
                validated["price_cents"] = None

            return validated, None

        except ValidationError as e:
            error_response = jsonify({
                "error": e.message,
                "code": e.code,
                "field": e.field
            }), 400
            return None, error_response

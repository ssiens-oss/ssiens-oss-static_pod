"""
API versioning support
"""
from flask import Blueprint, request, jsonify
from functools import wraps
from typing import Callable
import re


class APIVersion:
    """API version information"""

    def __init__(self, major: int, minor: int, patch: int = 0):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self):
        return f"v{self.major}.{self.minor}.{self.patch}"

    def __repr__(self):
        return f"APIVersion({self.major}, {self.minor}, {self.patch})"

    def __eq__(self, other):
        return (self.major == other.major and
                self.minor == other.minor and
                self.patch == other.patch)

    def __lt__(self, other):
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other

    @classmethod
    def from_string(cls, version_str: str):
        """
        Parse version string.

        Args:
            version_str: Version string (e.g., "v1.0.0", "1.0", "v2")

        Returns:
            APIVersion instance
        """
        # Remove 'v' prefix if present
        version_str = version_str.lstrip('v')

        # Split into parts
        parts = version_str.split('.')
        major = int(parts[0]) if len(parts) > 0 else 1
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0

        return cls(major, minor, patch)


class VersionedBlueprint:
    """
    Create versioned API blueprints.

    Example:
        v1 = VersionedBlueprint('api', version=APIVersion(1, 0))
        v2 = VersionedBlueprint('api', version=APIVersion(2, 0))

        @v1.route('/generate', methods=['POST'])
        def generate_v1():
            # v1 implementation
            ...

        @v2.route('/generate', methods=['POST'])
        def generate_v2():
            # v2 implementation with new features
            ...
    """

    def __init__(self, name: str, version: APIVersion, **kwargs):
        self.version = version
        self.blueprint = Blueprint(
            f"{name}_{version.major}_{version.minor}",
            __name__,
            url_prefix=f"/api/v{version.major}",
            **kwargs
        )

    def route(self, rule: str, **options):
        """Decorator for adding routes"""
        return self.blueprint.route(rule, **options)

    def get_blueprint(self):
        """Get Flask blueprint"""
        return self.blueprint


def version_required(min_version: str = None, max_version: str = None):
    """
    Decorator to enforce API version requirements.

    Args:
        min_version: Minimum required version (e.g., "1.0")
        max_version: Maximum allowed version (e.g., "2.0")

    Example:
        @app.route('/api/v1/endpoint')
        @version_required(min_version="1.0", max_version="1.9")
        def endpoint():
            ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract version from URL path
            version_match = re.search(r'/api/v(\d+)(?:\.(\d+))?', request.path)

            if not version_match:
                return jsonify({
                    'error': 'API version not specified',
                    'code': 'VERSION_NOT_SPECIFIED'
                }), 400

            major = int(version_match.group(1))
            minor = int(version_match.group(2)) if version_match.group(2) else 0

            current_version = APIVersion(major, minor)

            # Check minimum version
            if min_version:
                min_ver = APIVersion.from_string(min_version)
                if current_version < min_ver:
                    return jsonify({
                        'error': f'API version {current_version} is too old. Minimum: {min_ver}',
                        'code': 'VERSION_TOO_OLD',
                        'current_version': str(current_version),
                        'min_version': str(min_ver)
                    }), 400

            # Check maximum version
            if max_version:
                max_ver = APIVersion.from_string(max_version)
                if current_version > max_ver:
                    return jsonify({
                        'error': f'API version {current_version} is not supported. Maximum: {max_ver}',
                        'code': 'VERSION_NOT_SUPPORTED',
                        'current_version': str(current_version),
                        'max_version': str(max_ver)
                    }), 400

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def get_api_version_info() -> dict:
    """
    Get API version information.

    Returns:
        Dictionary with version info
    """
    return {
        'current_version': 'v1.0.0',
        'supported_versions': ['v1.0.0'],
        'deprecated_versions': [],
        'version_policy': 'Breaking changes require major version bump'
    }


# Version migration helpers
class VersionMigrator:
    """
    Helper for migrating data between API versions.

    Example:
        migrator = VersionMigrator()

        @migrator.register('1.0', '2.0')
        def migrate_generate_request(data):
            # Transform v1 request to v2 format
            if 'prompt' in data:
                data['text_prompt'] = data.pop('prompt')
            return data
    """

    def __init__(self):
        self.migrations = {}

    def register(self, from_version: str, to_version: str):
        """Register a migration function"""
        def decorator(f: Callable) -> Callable:
            key = (from_version, to_version)
            self.migrations[key] = f
            return f
        return decorator

    def migrate(self, data: dict, from_version: str, to_version: str) -> dict:
        """
        Migrate data from one version to another.

        Args:
            data: Data to migrate
            from_version: Source version
            to_version: Target version

        Returns:
            Migrated data
        """
        key = (from_version, to_version)
        if key in self.migrations:
            return self.migrations[key](data)

        # No migration needed or available
        return data


# Global migrator
migrator = VersionMigrator()

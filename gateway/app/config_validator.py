"""
Environment-based configuration validation
"""
import os
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConfigValidationError:
    """Configuration validation error"""
    field: str
    error: str
    severity: str  # 'error', 'warning'


class ConfigValidator:
    """
    Validate environment configuration.

    Ensures required environment variables are set and valid.
    """

    REQUIRED_VARS = [
        'IMAGE_DIR',
        'STATE_FILE',
    ]

    OPTIONAL_VARS = {
        'PRINTIFY_API_KEY': 'Printify integration disabled',
        'PRINTIFY_SHOP_ID': 'Printify integration disabled',
        'RUNPOD_API_KEY': 'RunPod serverless disabled',
        'RUNPOD_ENDPOINT_ID': 'RunPod serverless disabled',
        'COMFYUI_API_URL': 'Direct ComfyUI disabled'
    }

    def validate(self) -> tuple[bool, List[ConfigValidationError]]:
        """
        Validate configuration.

        Returns:
            Tuple of (is_valid, list of errors/warnings)
        """
        errors = []

        # Check required variables
        for var in self.REQUIRED_VARS:
            if not os.getenv(var):
                errors.append(ConfigValidationError(
                    field=var,
                    error=f'Required environment variable {var} is not set',
                    severity='error'
                ))

        # Check optional variables and warn if missing
        for var, message in self.OPTIONAL_VARS.items():
            if not os.getenv(var):
                errors.append(ConfigValidationError(
                    field=var,
                    error=message,
                    severity='warning'
                ))

        # Validate IMAGE_DIR exists or can be created
        image_dir = os.getenv('IMAGE_DIR')
        if image_dir:
            if not os.path.exists(image_dir):
                try:
                    os.makedirs(image_dir, exist_ok=True)
                    logger.info(f"Created image directory: {image_dir}")
                except Exception as e:
                    errors.append(ConfigValidationError(
                        field='IMAGE_DIR',
                        error=f'Cannot create image directory: {e}',
                        severity='error'
                    ))

        # Validate STATE_FILE directory exists
        state_file = os.getenv('STATE_FILE')
        if state_file:
            state_dir = os.path.dirname(state_file)
            if state_dir and not os.path.exists(state_dir):
                try:
                    os.makedirs(state_dir, exist_ok=True)
                    logger.info(f"Created state directory: {state_dir}")
                except Exception as e:
                    errors.append(ConfigValidationError(
                        field='STATE_FILE',
                        error=f'Cannot create state directory: {e}',
                        severity='error'
                    ))

        # Check if at least one generation backend is configured
        has_runpod = os.getenv('RUNPOD_API_KEY') and os.getenv('RUNPOD_ENDPOINT_ID')
        has_comfyui = os.getenv('COMFYUI_API_URL')

        if not (has_runpod or has_comfyui):
            errors.append(ConfigValidationError(
                field='GENERATION_BACKEND',
                error='No generation backend configured (RunPod or ComfyUI)',
                severity='error'
            ))

        # Check if at least one publishing platform is configured
        has_printify = os.getenv('PRINTIFY_API_KEY') and os.getenv('PRINTIFY_SHOP_ID')

        if not has_printify:
            errors.append(ConfigValidationError(
                field='PUBLISHING_PLATFORM',
                error='No publishing platform configured (Printify)',
                severity='warning'
            ))

        # Determine if configuration is valid (no errors, warnings are OK)
        has_errors = any(e.severity == 'error' for e in errors)
        is_valid = not has_errors

        return is_valid, errors

    def print_validation_report(self):
        """Print validation report to console"""
        is_valid, errors = self.validate()

        print("\n" + "="*70)
        print("Configuration Validation Report")
        print("="*70)

        if is_valid:
            print("✓ Configuration is valid")
        else:
            print("✗ Configuration has errors")

        if errors:
            print("\nIssues found:")
            for error in errors:
                symbol = "⚠" if error.severity == 'warning' else "✗"
                print(f"  {symbol} [{error.severity.upper()}] {error.field}: {error.error}")

        print("="*70 + "\n")

        return is_valid

    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            'image_dir': os.getenv('IMAGE_DIR'),
            'state_file': os.getenv('STATE_FILE'),
            'printify_enabled': bool(os.getenv('PRINTIFY_API_KEY') and os.getenv('PRINTIFY_SHOP_ID')),
            'runpod_enabled': bool(os.getenv('RUNPOD_API_KEY') and os.getenv('RUNPOD_ENDPOINT_ID')),
            'comfyui_enabled': bool(os.getenv('COMFYUI_API_URL')),
            'logging_level': os.getenv('LOG_LEVEL', 'INFO')
        }


# Global validator
config_validator = ConfigValidator()

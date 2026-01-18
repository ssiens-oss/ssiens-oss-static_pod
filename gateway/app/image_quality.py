"""
Image quality validation and auto-optimization
"""
import logging
from PIL import Image
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ImageQualityValidator:
    """
    Validate and optimize images for POD requirements.

    Checks:
    - Resolution (minimum/recommended)
    - File size
    - Format
    - Color mode
    - DPI
    """

    # POD requirements
    MIN_RESOLUTION = (2400, 2400)
    RECOMMENDED_RESOLUTION = (4500, 5400)
    MAX_FILE_SIZE_MB = 50
    SUPPORTED_FORMATS = ['PNG', 'JPEG', 'JPG']
    RECOMMENDED_DPI = 300

    def validate(self, image_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate image quality.

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (is_valid, validation_report)
        """
        report = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }

        try:
            # Check file exists
            if not image_path.exists():
                report['valid'] = False
                report['errors'].append('Image file not found')
                return False, report

            # Check file size
            file_size_mb = image_path.stat().st_size / (1024 * 1024)
            report['info']['file_size_mb'] = round(file_size_mb, 2)

            if file_size_mb > self.MAX_FILE_SIZE_MB:
                report['valid'] = False
                report['errors'].append(
                    f'File size ({file_size_mb:.1f}MB) exceeds maximum ({self.MAX_FILE_SIZE_MB}MB)'
                )

            # Open image
            with Image.open(image_path) as img:
                # Check format
                report['info']['format'] = img.format

                if img.format not in self.SUPPORTED_FORMATS:
                    report['valid'] = False
                    report['errors'].append(
                        f'Unsupported format: {img.format}. Use {", ".join(self.SUPPORTED_FORMATS)}'
                    )

                # Check resolution
                width, height = img.size
                report['info']['resolution'] = {'width': width, 'height': height}

                if width < self.MIN_RESOLUTION[0] or height < self.MIN_RESOLUTION[1]:
                    report['valid'] = False
                    report['errors'].append(
                        f'Resolution ({width}x{height}) below minimum '
                        f'({self.MIN_RESOLUTION[0]}x{self.MIN_RESOLUTION[1]})'
                    )

                if width < self.RECOMMENDED_RESOLUTION[0] or height < self.RECOMMENDED_RESOLUTION[1]:
                    report['warnings'].append(
                        f'Resolution ({width}x{height}) below recommended '
                        f'({self.RECOMMENDED_RESOLUTION[0]}x{self.RECOMMENDED_RESOLUTION[1]})'
                    )

                # Check color mode
                report['info']['color_mode'] = img.mode

                if img.mode not in ['RGB', 'RGBA']:
                    report['warnings'].append(
                        f'Color mode is {img.mode}, recommended: RGB or RGBA'
                    )

                # Check DPI
                dpi = img.info.get('dpi', (72, 72))
                if isinstance(dpi, tuple):
                    dpi_value = dpi[0]
                else:
                    dpi_value = dpi

                report['info']['dpi'] = dpi_value

                if dpi_value < self.RECOMMENDED_DPI:
                    report['warnings'].append(
                        f'DPI ({dpi_value}) below recommended ({self.RECOMMENDED_DPI})'
                    )

                # Calculate print size at 300 DPI
                print_width_inches = width / 300
                print_height_inches = height / 300
                report['info']['print_size_inches'] = {
                    'width': round(print_width_inches, 1),
                    'height': round(print_height_inches, 1)
                }

        except Exception as e:
            logger.error(f"Error validating image {image_path}: {e}")
            report['valid'] = False
            report['errors'].append(f'Validation error: {str(e)}')

        return report['valid'], report

    def optimize(
        self,
        image_path: Path,
        output_path: Path = None,
        target_resolution: Tuple[int, int] = None,
        quality: int = 95
    ) -> Optional[Path]:
        """
        Optimize image for POD.

        Args:
            image_path: Source image path
            output_path: Output path (uses source if None)
            target_resolution: Target resolution (uses recommended if None)
            quality: JPEG quality (1-100)

        Returns:
            Path to optimized image, or None if failed
        """
        try:
            if output_path is None:
                output_path = image_path

            if target_resolution is None:
                target_resolution = self.RECOMMENDED_RESOLUTION

            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode not in ['RGB', 'RGBA']:
                    img = img.convert('RGBA' if img.mode == 'LA' or 'transparency' in img.info else 'RGB')

                # Resize if needed
                if img.size != target_resolution:
                    img = img.resize(target_resolution, Image.Resampling.LANCZOS)

                # Save with DPI metadata
                img.save(
                    output_path,
                    dpi=(self.RECOMMENDED_DPI, self.RECOMMENDED_DPI),
                    quality=quality,
                    optimize=True
                )

                logger.info(f"Optimized image: {image_path} -> {output_path}")
                return output_path

        except Exception as e:
            logger.error(f"Error optimizing image {image_path}: {e}")
            return None


# Global validator instance
image_validator = ImageQualityValidator()

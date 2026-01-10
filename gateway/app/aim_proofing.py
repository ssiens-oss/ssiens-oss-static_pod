"""
AIM (Automated Image Manipulation) Proofing Engine
Automatically validates and scores images for POD suitability
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ImageQualityScore:
    """Image quality assessment results"""
    resolution_score: float  # 0-100
    filesize_score: float    # 0-100
    format_score: float      # 0-100
    aspect_ratio_score: float  # 0-100
    corruption_score: float  # 0-100
    overall_score: float     # 0-100
    issues: List[str]
    recommendations: List[str]
    metadata: Dict


@dataclass
class ProofingResult:
    """Complete proofing analysis result"""
    image_id: str
    filename: str
    quality_score: ImageQualityScore
    ai_analysis: Optional[Dict] = None
    decision: str = "manual_review"  # auto_approve, auto_reject, manual_review
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class AIMProofingEngine:
    """
    Automated Image Manipulation Proofing Engine
    Validates images for Print-on-Demand suitability
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize AIM Proofing Engine

        Args:
            config: Configuration dictionary with validation rules
        """
        self.config = config or self._default_config()

    def _default_config(self) -> Dict:
        """Default validation configuration"""
        return {
            "quality_checks": {
                "min_resolution": {"width": 2400, "height": 2400},
                "max_resolution": {"width": 8000, "height": 8000},
                "min_dpi": 150,
                "max_filesize_mb": 50,
                "allowed_formats": ["PNG", "JPEG", "JPG"],
                "min_aspect_ratio": 0.5,  # width/height
                "max_aspect_ratio": 2.0
            },
            "scoring": {
                "resolution_weight": 0.3,
                "filesize_weight": 0.1,
                "format_weight": 0.2,
                "aspect_ratio_weight": 0.2,
                "corruption_weight": 0.2
            },
            "auto_approval": {
                "enabled": True,
                "min_score": 85.0,
                "require_ai_analysis": False
            },
            "auto_rejection": {
                "enabled": True,
                "max_score": 40.0
            }
        }

    def analyze_image(self, image_path: str) -> ProofingResult:
        """
        Perform complete image analysis

        Args:
            image_path: Path to image file

        Returns:
            ProofingResult with quality scores and recommendations
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Generate unique ID
        image_id = self._generate_image_id(image_path)

        # Perform quality checks
        quality_score = self._check_image_quality(image_path)

        # Determine decision
        decision = self._make_decision(quality_score)

        return ProofingResult(
            image_id=image_id,
            filename=image_path.name,
            quality_score=quality_score,
            decision=decision
        )

    def _generate_image_id(self, image_path: Path) -> str:
        """Generate unique ID for image"""
        # Use filename stem or hash
        return image_path.stem

    def _check_image_quality(self, image_path: Path) -> ImageQualityScore:
        """
        Perform automated quality checks

        Args:
            image_path: Path to image file

        Returns:
            ImageQualityScore with detailed assessment
        """
        issues = []
        recommendations = []
        scores = {}

        try:
            # Open image
            img = Image.open(image_path)
            width, height = img.size
            format_type = img.format

            # File size
            file_size_mb = image_path.stat().st_size / (1024 * 1024)

            # 1. Resolution Check
            resolution_score = self._check_resolution(width, height, issues, recommendations)
            scores['resolution'] = resolution_score

            # 2. File Size Check
            filesize_score = self._check_filesize(file_size_mb, issues, recommendations)
            scores['filesize'] = filesize_score

            # 3. Format Check
            format_score = self._check_format(format_type, issues, recommendations)
            scores['format'] = format_score

            # 4. Aspect Ratio Check
            aspect_ratio_score = self._check_aspect_ratio(width, height, issues, recommendations)
            scores['aspect_ratio'] = aspect_ratio_score

            # 5. Corruption Check
            corruption_score = self._check_corruption(img, issues, recommendations)
            scores['corruption'] = corruption_score

            # Calculate overall score
            weights = self.config['scoring']
            overall_score = (
                scores['resolution'] * weights['resolution_weight'] +
                scores['filesize'] * weights['filesize_weight'] +
                scores['format'] * weights['format_weight'] +
                scores['aspect_ratio'] * weights['aspect_ratio_weight'] +
                scores['corruption'] * weights['corruption_weight']
            )

            # Metadata
            metadata = {
                "width": width,
                "height": height,
                "format": format_type,
                "file_size_mb": round(file_size_mb, 2),
                "color_mode": img.mode,
                "has_transparency": img.mode in ('RGBA', 'LA', 'P')
            }

            return ImageQualityScore(
                resolution_score=round(resolution_score, 2),
                filesize_score=round(filesize_score, 2),
                format_score=round(format_score, 2),
                aspect_ratio_score=round(aspect_ratio_score, 2),
                corruption_score=round(corruption_score, 2),
                overall_score=round(overall_score, 2),
                issues=issues,
                recommendations=recommendations,
                metadata=metadata
            )

        except Exception as e:
            # Image is corrupted or invalid
            return ImageQualityScore(
                resolution_score=0,
                filesize_score=0,
                format_score=0,
                aspect_ratio_score=0,
                corruption_score=0,
                overall_score=0,
                issues=[f"Failed to analyze image: {str(e)}"],
                recommendations=["Check if image file is corrupted"],
                metadata={}
            )

    def _check_resolution(self, width: int, height: int, issues: List, recommendations: List) -> float:
        """Check image resolution"""
        min_res = self.config['quality_checks']['min_resolution']
        max_res = self.config['quality_checks']['max_resolution']

        score = 100.0

        if width < min_res['width'] or height < min_res['height']:
            score = max(0, 100 - ((min_res['width'] - width) / min_res['width'] * 100))
            issues.append(f"Low resolution: {width}x{height} (minimum: {min_res['width']}x{min_res['height']})")
            recommendations.append("Increase image resolution for better print quality")

        if width > max_res['width'] or height > max_res['height']:
            score = 80.0
            issues.append(f"Very high resolution: {width}x{height} (may cause upload issues)")
            recommendations.append("Consider reducing resolution to improve upload speed")

        return score

    def _check_filesize(self, file_size_mb: float, issues: List, recommendations: List) -> float:
        """Check file size"""
        max_size = self.config['quality_checks']['max_filesize_mb']

        score = 100.0

        if file_size_mb > max_size:
            score = max(0, 100 - ((file_size_mb - max_size) / max_size * 100))
            issues.append(f"Large file size: {file_size_mb:.1f}MB (maximum: {max_size}MB)")
            recommendations.append("Compress image or reduce resolution")
        elif file_size_mb < 0.1:
            score = 70.0
            issues.append(f"Very small file size: {file_size_mb:.2f}MB (may indicate low quality)")
            recommendations.append("Verify image quality")

        return score

    def _check_format(self, format_type: str, issues: List, recommendations: List) -> float:
        """Check image format"""
        allowed = self.config['quality_checks']['allowed_formats']

        if format_type in allowed:
            return 100.0 if format_type == "PNG" else 90.0
        else:
            issues.append(f"Unsupported format: {format_type} (allowed: {', '.join(allowed)})")
            recommendations.append("Convert image to PNG format")
            return 50.0

    def _check_aspect_ratio(self, width: int, height: int, issues: List, recommendations: List) -> float:
        """Check aspect ratio"""
        min_ratio = self.config['quality_checks']['min_aspect_ratio']
        max_ratio = self.config['quality_checks']['max_aspect_ratio']

        ratio = width / height

        if min_ratio <= ratio <= max_ratio:
            return 100.0
        else:
            issues.append(f"Unusual aspect ratio: {ratio:.2f} (recommended: {min_ratio}-{max_ratio})")
            recommendations.append("Use more standard aspect ratio for better product fit")
            return 70.0

    def _check_corruption(self, img: Image.Image, issues: List, recommendations: List) -> float:
        """Check for image corruption"""
        try:
            # Try to verify image
            img.verify()
            # Reopen after verify (verify closes the file)
            img = Image.open(img.filename)
            # Try to load pixel data
            img.load()
            return 100.0
        except Exception as e:
            issues.append(f"Image may be corrupted: {str(e)}")
            recommendations.append("Re-generate or repair image")
            return 0.0

    def _make_decision(self, quality_score: ImageQualityScore) -> str:
        """
        Make auto-approval decision based on quality score

        Args:
            quality_score: Image quality assessment

        Returns:
            Decision string: auto_approve, auto_reject, or manual_review
        """
        overall = quality_score.overall_score

        # Auto-rejection
        if self.config['auto_rejection']['enabled']:
            if overall <= self.config['auto_rejection']['max_score']:
                return "auto_reject"

        # Auto-approval
        if self.config['auto_approval']['enabled']:
            if overall >= self.config['auto_approval']['min_score']:
                return "auto_approve"

        # Default to manual review
        return "manual_review"

    def batch_analyze(self, directory: str, pattern: str = "*.png") -> List[ProofingResult]:
        """
        Analyze all images in a directory

        Args:
            directory: Directory path to scan
            pattern: Glob pattern for image files

        Returns:
            List of ProofingResult objects
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        results = []
        for image_file in dir_path.glob(pattern):
            try:
                result = self.analyze_image(str(image_file))
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {image_file}: {e}")

        return results

    def generate_report(self, results: List[ProofingResult]) -> Dict:
        """
        Generate summary report from batch analysis

        Args:
            results: List of ProofingResult objects

        Returns:
            Dictionary with statistics and summaries
        """
        total = len(results)
        auto_approved = len([r for r in results if r.decision == "auto_approve"])
        auto_rejected = len([r for r in results if r.decision == "auto_reject"])
        manual_review = len([r for r in results if r.decision == "manual_review"])

        avg_score = sum(r.quality_score.overall_score for r in results) / total if total > 0 else 0

        return {
            "total_images": total,
            "auto_approved": auto_approved,
            "auto_rejected": auto_rejected,
            "manual_review": manual_review,
            "average_quality_score": round(avg_score, 2),
            "approval_rate": round((auto_approved / total * 100) if total > 0 else 0, 2),
            "results": [
                {
                    "filename": r.filename,
                    "decision": r.decision,
                    "score": r.quality_score.overall_score,
                    "issues": r.quality_score.issues
                }
                for r in results
            ]
        }


def load_config(config_path: Optional[str] = None) -> Dict:
    """
    Load AIM configuration from file

    Args:
        config_path: Path to JSON config file

    Returns:
        Configuration dictionary
    """
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return None

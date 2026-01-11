"""POD-specific risk assessment."""

from typing import Tuple, List, Dict, Any
from antigravity.models import PODOffer
from pathlib import Path


def assess_pod_risk(
    design_path: str,
    offer: PODOffer,
    check_copyright: bool = True,
    check_pricing: bool = True,
    check_content: bool = True,
) -> Tuple[bool, List[str]]:
    """
    Assess risk for a POD product launch.

    Args:
        design_path: Path to design file
        offer: POD offer to assess
        check_copyright: Check for copyright issues
        check_pricing: Check pricing strategy
        check_content: Check content appropriateness

    Returns:
        (is_safe, list_of_warnings)
    """
    warnings = []
    is_safe = True

    # Check if design file exists
    if not Path(design_path).exists():
        warnings.append(f"Design file not found: {design_path}")
        is_safe = False

    # Check for test/debug artifacts
    if "test" in design_path.lower() or "debug" in design_path.lower():
        warnings.append("Design path contains test/debug indicators")
        is_safe = False

    # Pricing risk assessment
    if check_pricing:
        pricing_warnings = _assess_pricing_risk(offer)
        warnings.extend(pricing_warnings)
        if pricing_warnings:
            # Pricing warnings are not blockers, just cautions
            pass

    # Content risk assessment
    if check_content:
        content_warnings = _assess_content_risk(offer)
        warnings.extend(content_warnings)
        if any("BLOCK" in w.upper() for w in content_warnings):
            is_safe = False

    # Copyright risk (basic checks)
    if check_copyright:
        copyright_warnings = _assess_copyright_risk(offer)
        warnings.extend(copyright_warnings)
        if copyright_warnings:
            # Copyright warnings should block
            is_safe = False

    return is_safe, warnings


def _assess_pricing_risk(offer: PODOffer) -> List[str]:
    """Assess pricing strategy risks."""
    warnings = []

    # Check for unrealistic pricing
    if offer.price < 10:
        warnings.append(f"Price too low ({offer.price}) - may indicate error or unsustainable margins")

    if offer.price > 100:
        warnings.append(f"Price very high ({offer.price}) - may limit market")

    # Check for pricing psychology
    if not (offer.price % 1 == 0.99 or offer.price % 1 == 0.95 or offer.price % 1 == 0):
        warnings.append(f"Price {offer.price} doesn't follow psychological pricing patterns (.99, .95, or whole numbers)")

    return warnings


def _assess_content_risk(offer: PODOffer) -> List[str]:
    """Assess content appropriateness risks."""
    warnings = []

    # Check for potentially problematic content
    blocked_terms = [
        "hate", "offensive", "explicit", "nsfw",
        "copyright", "trademark", "stolen",
    ]

    content = f"{offer.headline} {offer.description}".lower()

    for term in blocked_terms:
        if term in content:
            warnings.append(f"BLOCK: Potentially problematic term detected: '{term}'")

    # Check for excessive length
    if len(offer.headline) > 100:
        warnings.append(f"Headline too long ({len(offer.headline)} chars) - may be truncated on platforms")

    if len(offer.description) > 500:
        warnings.append(f"Description very long ({len(offer.description)} chars) - consider shortening")

    return warnings


def _assess_copyright_risk(offer: PODOffer) -> List[str]:
    """Assess copyright and trademark risks."""
    warnings = []

    # Check for common trademark terms
    trademark_terms = [
        "nike", "adidas", "supreme", "gucci", "louis vuitton",
        "coca cola", "disney", "marvel", "pokemon",
        "star wars", "harry potter",
    ]

    content = f"{offer.headline} {offer.description}".lower()

    for term in trademark_terms:
        if term in content:
            warnings.append(f"Potential trademark issue: '{term}' detected")

    # Check tags for trademark issues
    for tag in offer.tags:
        if tag.lower() in trademark_terms:
            warnings.append(f"Potential trademark in tags: '{tag}'")

    return warnings


def calculate_risk_score(
    design_path: str,
    offer: PODOffer,
) -> Dict[str, Any]:
    """
    Calculate overall risk score for POD launch.

    Args:
        design_path: Path to design file
        offer: POD offer

    Returns:
        Risk assessment dict with score and factors
    """
    is_safe, warnings = assess_pod_risk(design_path, offer)

    # Calculate risk score (0-100, lower is better)
    base_score = 0 if is_safe else 50

    # Add points for each warning
    warning_points = len(warnings) * 10

    # Reduce points for good practices
    good_practices = 0
    if 19.99 <= offer.price <= 59.99:
        good_practices += 5  # Reasonable price range

    if len(offer.tags) >= 3:
        good_practices += 5  # Good tagging

    total_score = max(0, min(100, base_score + warning_points - good_practices))

    # Determine risk level
    if total_score <= 20:
        risk_level = "low"
    elif total_score <= 50:
        risk_level = "medium"
    else:
        risk_level = "high"

    return {
        "score": total_score,
        "level": risk_level,
        "is_safe": is_safe,
        "warnings": warnings,
        "warning_count": len(warnings),
        "blocking_warnings": [w for w in warnings if "BLOCK" in w.upper()],
    }

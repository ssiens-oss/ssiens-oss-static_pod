"""Confidence-weighted voting and consensus building."""

from collections import defaultdict
from antigravity.models import ModelResponse
from typing import List, Tuple


def weighted_consensus(responses: List[ModelResponse]) -> Tuple[str, float]:
    """
    Calculate weighted consensus from model responses.

    Returns:
        (consensus_content, total_confidence)
    """
    if not responses:
        return "", 0.0

    # Group responses by content and sum confidence weights
    buckets = defaultdict(float)
    for r in responses:
        # Normalize content for comparison (strip whitespace, lowercase)
        normalized = r.content.strip().lower()
        buckets[normalized] += r.confidence

    # Find the content with highest total confidence
    if not buckets:
        return responses[0].content, responses[0].confidence

    best_content, best_score = max(buckets.items(), key=lambda x: x[1])

    # Return original case version
    for r in responses:
        if r.content.strip().lower() == best_content:
            return r.content, best_score

    return best_content, best_score


def majority_vote(responses: List[ModelResponse], threshold: float = 0.5) -> Tuple[bool, str]:
    """
    Determine if there's a clear majority decision.

    Returns:
        (has_majority, winning_content)
    """
    if not responses:
        return False, ""

    # Count responses by normalized content
    content_counts = defaultdict(int)
    for r in responses:
        normalized = r.content.strip().lower()
        content_counts[normalized] += 1

    total = len(responses)
    max_count = max(content_counts.values())

    has_majority = (max_count / total) >= threshold

    # Get the winning content
    for content, count in content_counts.items():
        if count == max_count:
            # Find original case version
            for r in responses:
                if r.content.strip().lower() == content:
                    return has_majority, r.content

    return has_majority, ""

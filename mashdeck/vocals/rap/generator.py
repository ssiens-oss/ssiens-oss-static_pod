"""
Rap Lyric and Flow Generator
Bar-aware rap generation with syllable timing
"""

import random
from typing import List, Dict


# Rap phrase banks by energy level
RAP_PHRASES = {
    "low": [
        "Moving through the night, keep it smooth",
        "Vibe check, we in the groove",
        "Low key but the flow's still tight",
        "Minimal flex, maximum sight",
        "Cool and collected, never stressed"
    ],
    "medium": [
        "Running through the night, no sleep",
        "Neon lights when I speak",
        "Heartbeat sync with the bass",
        "Fast life, no time to waste",
        "Pressure rising, feel the heat",
        "On my grind, can't be beat",
        "City lights, endless streets",
        "Moving forward, no defeat"
    ],
    "high": [
        "Fire burning, can't stop now",
        "Top level, taking the crown",
        "Energy maximum, feel the sound",
        "Break the ceiling, shake the ground",
        "Unstoppable force, here we go",
        "Peak performance, steal the show",
        "No limits, watch me grow",
        "Explosive moment, let it flow"
    ]
}

# Flow patterns (syllable patterns per bar)
FLOW_PATTERNS = {
    "simple": [8, 8],  # 8 syllables per half-bar
    "medium": [10, 10, 8, 8],  # Varied pattern
    "complex": [12, 8, 10, 6]  # Complex syncopation
}


def generate_rap(
    bars: int,
    bpm: int,
    energy: float = 0.5,
    theme: str = "general"
) -> str:
    """
    Generate rap lyrics for specified bars

    Args:
        bars: Number of bars (4/4 time)
        bpm: Beats per minute
        energy: Energy level 0.0-1.0
        theme: Thematic content

    Returns:
        Rap lyrics (newline-separated)
    """
    # Determine energy tier
    if energy > 0.7:
        energy_tier = "high"
    elif energy > 0.4:
        energy_tier = "medium"
    else:
        energy_tier = "low"

    # Generate lines (approximately 2 lines per bar for rap)
    lines_needed = bars * 2
    phrases = RAP_PHRASES[energy_tier]

    lines = []
    for _ in range(lines_needed):
        lines.append(random.choice(phrases))

    return "\n".join(lines)


def generate_freestyle(
    topics: List[str],
    bars: int = 4,
    style: str = "aggressive"
) -> str:
    """
    Generate freestyle rap from topics (for live mode)

    Args:
        topics: List of topics/keywords from chat
        bars: Number of bars
        style: Freestyle style (aggressive, smooth, hype)

    Returns:
        Freestyle rap lyrics
    """
    if not topics:
        topics = ["energy", "vibe", "music"]

    # Build lines incorporating topics
    templates = [
        "{topic} on my mind, feel the beat align",
        "Running with the {topic}, can't define",
        "{topic} energy, crossing every line",
        "Living for the {topic}, everything's fine",
        "Chase the {topic}, never decline"
    ]

    lines = []
    for _ in range(bars * 2):
        topic = random.choice(topics)
        template = random.choice(templates)
        lines.append(template.format(topic=topic))

    return "\n".join(lines)


def analyze_syllable_count(text: str) -> int:
    """
    Approximate syllable count (simple heuristic)

    Args:
        text: Text to analyze

    Returns:
        Estimated syllable count
    """
    # Simple approximation: count vowel groups
    vowels = "aeiouAEIOU"
    count = 0
    prev_was_vowel = False

    for char in text:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel

    return max(1, count)  # At least 1 syllable


def fit_to_flow(lyrics: str, flow_pattern: List[int]) -> str:
    """
    Adjust lyrics to fit flow pattern

    Args:
        lyrics: Input lyrics
        flow_pattern: Syllable count pattern

    Returns:
        Adjusted lyrics
    """
    # For now, return as-is
    # TODO: Implement intelligent syllable fitting
    return lyrics

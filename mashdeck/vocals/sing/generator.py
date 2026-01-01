"""
Sung Melody and Hook Generator
Key-aware melody generation with scale constraints
"""

import random
from typing import List, Dict, Tuple


# Musical scales (semitone intervals from root)
SCALES = {
    "minor": [0, 2, 3, 5, 7, 8, 10],      # Natural minor
    "major": [0, 2, 4, 5, 7, 9, 11],       # Major
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],  # Harmonic minor
    "pentatonic": [0, 2, 4, 7, 9]          # Pentatonic (versatile)
}

# Hook phrase banks
HOOK_PHRASES = {
    "energetic": [
        "We don't slow down",
        "Feel it in the sound",
        "Higher every round",
        "Lost but never found",
        "Take me to the sky",
        "Never say goodbye",
        "Living for tonight",
        "Burning bright with light"
    ],
    "chill": [
        "Floating through the air",
        "Nothing we can't bear",
        "Drifting without care",
        "Moments that we share",
        "Dreams within our reach",
        "Waves upon the beach",
        "Stars are all we need",
        "Follow where they lead"
    ],
    "dark": [
        "Shadows in the night",
        "Fading from the light",
        "Nothing left to fight",
        "Silence takes its bite",
        "Lost within the void",
        "Everything destroyed",
        "Echoes in my mind",
        "Leaving all behind"
    ]
}


def generate_hook(bars: int, mood: str = "energetic") -> str:
    """
    Generate sung hook lyrics

    Args:
        bars: Number of bars
        mood: Hook mood (energetic, chill, dark)

    Returns:
        Hook lyrics
    """
    if mood not in HOOK_PHRASES:
        mood = "energetic"

    phrases = HOOK_PHRASES[mood]
    lines_needed = bars // 2  # Hooks typically have fewer, longer lines

    # Select and combine phrases
    selected = random.sample(phrases, min(len(phrases), lines_needed))

    return " / ".join(selected)


def generate_melody(
    key: str = "F minor",
    bars: int = 8,
    contour: str = "ascending"
) -> List[int]:
    """
    Generate melody as MIDI note offsets

    Args:
        key: Musical key (e.g., "F minor", "C major")
        bars: Number of bars
        contour: Melody shape (ascending, descending, wave, random)

    Returns:
        List of semitone offsets from root note
    """
    # Parse key
    root, mode = key.split()
    mode = mode.lower()

    # Get scale
    if "minor" in mode:
        scale = SCALES["minor"]
    elif "major" in mode:
        scale = SCALES["major"]
    else:
        scale = SCALES["pentatonic"]

    # Generate melody based on contour
    num_notes = bars * 4  # Quarter notes

    if contour == "ascending":
        melody = _ascending_melody(scale, num_notes)
    elif contour == "descending":
        melody = _descending_melody(scale, num_notes)
    elif contour == "wave":
        melody = _wave_melody(scale, num_notes)
    else:  # random
        melody = _random_melody(scale, num_notes)

    return melody


def _ascending_melody(scale: List[int], length: int) -> List[int]:
    """Generate ascending melody"""
    melody = []
    for i in range(length):
        # Gradually move up the scale
        idx = (i // 2) % len(scale)
        octave = (i // (2 * len(scale))) * 12
        melody.append(scale[idx] + octave)
    return melody


def _descending_melody(scale: List[int], length: int) -> List[int]:
    """Generate descending melody"""
    melody = _ascending_melody(scale, length)
    return melody[::-1]


def _wave_melody(scale: List[int], length: int) -> List[int]:
    """Generate wave-like melody"""
    melody = []
    direction = 1
    pos = 0

    for _ in range(length):
        octave = (pos // len(scale)) * 12
        melody.append(scale[pos % len(scale)] + octave)

        pos += direction

        # Change direction at extremes
        if pos >= len(scale) * 2:
            direction = -1
        elif pos < 0:
            direction = 1

    return melody


def _random_melody(scale: List[int], length: int) -> List[int]:
    """Generate random melody within scale"""
    return [random.choice(scale) for _ in range(length)]


def melody_to_midi(
    melody: List[int],
    root_note: int = 60,  # Middle C
    duration_per_note: int = 480  # Quarter note in ticks
) -> List[Dict]:
    """
    Convert melody to MIDI note events

    Args:
        melody: List of semitone offsets
        root_note: MIDI root note number
        duration_per_note: Duration in MIDI ticks

    Returns:
        List of MIDI note events
    """
    events = []

    for i, offset in enumerate(melody):
        note = root_note + offset

        events.append({
            "type": "note_on",
            "note": note,
            "velocity": 80,
            "time": i * duration_per_note
        })

        events.append({
            "type": "note_off",
            "note": note,
            "velocity": 0,
            "time": (i + 1) * duration_per_note
        })

    return events

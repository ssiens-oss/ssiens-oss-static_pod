"""
Song structure and arrangement system

Automatically arranges songs with intro, verse, chorus, bridge, outro
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class SectionType(str, Enum):
    """Song section types"""
    INTRO = "intro"
    VERSE = "verse"
    PRE_CHORUS = "pre_chorus"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    BREAKDOWN = "breakdown"
    BUILD = "build"
    DROP = "drop"
    OUTRO = "outro"


@dataclass
class SongSection:
    """A section of a song"""
    type: SectionType
    duration: int  # seconds
    vibe_modifiers: Dict[str, float]  # Modifications to base vibe
    intensity: float  # 0.0 - 1.0
    description: str


class SongStructure:
    """Defines the arrangement of a song"""

    def __init__(self, style: str = "standard"):
        self.style = style
        self.sections: List[SongSection] = []
        self.total_duration = 0

    def add_section(self, section: SongSection):
        """Add a section to the structure"""
        self.sections.append(section)
        self.total_duration += section.duration

    def to_timeline(self) -> List[Dict]:
        """Convert to timeline with timestamps"""
        timeline = []
        current_time = 0

        for section in self.sections:
            timeline.append({
                "type": section.type,
                "start": current_time,
                "end": current_time + section.duration,
                "duration": section.duration,
                "vibe_modifiers": section.vibe_modifiers,
                "intensity": section.intensity,
                "description": section.description
            })
            current_time += section.duration

        return timeline


# Pre-defined song structures
SONG_STRUCTURES = {
    "standard": [
        SongSection(SectionType.INTRO, 8, {"energy": -0.2}, 0.3, "Gentle intro"),
        SongSection(SectionType.VERSE, 16, {}, 0.5, "First verse"),
        SongSection(SectionType.CHORUS, 16, {"energy": 0.2}, 0.8, "Chorus 1"),
        SongSection(SectionType.VERSE, 16, {}, 0.5, "Second verse"),
        SongSection(SectionType.CHORUS, 16, {"energy": 0.2}, 0.8, "Chorus 2"),
        SongSection(SectionType.BRIDGE, 12, {"dark": 0.2, "dreamy": 0.3}, 0.6, "Bridge"),
        SongSection(SectionType.CHORUS, 16, {"energy": 0.3}, 0.9, "Final chorus"),
        SongSection(SectionType.OUTRO, 12, {"energy": -0.3}, 0.3, "Outro fade"),
    ],

    "edm_banger": [
        SongSection(SectionType.INTRO, 8, {"energy": -0.1}, 0.4, "Intro"),
        SongSection(SectionType.BUILD, 8, {"energy": 0.1}, 0.6, "Build tension"),
        SongSection(SectionType.DROP, 16, {"energy": 0.4, "aggressive": 0.3}, 1.0, "First drop"),
        SongSection(SectionType.BREAKDOWN, 12, {"energy": -0.2}, 0.4, "Breakdown"),
        SongSection(SectionType.BUILD, 8, {"energy": 0.2}, 0.7, "Build 2"),
        SongSection(SectionType.DROP, 16, {"energy": 0.4, "aggressive": 0.3}, 1.0, "Second drop"),
        SongSection(SectionType.OUTRO, 8, {"energy": -0.3}, 0.3, "Outro"),
    ],

    "lofi_chill": [
        SongSection(SectionType.INTRO, 12, {"dreamy": 0.2}, 0.3, "Dreamy intro"),
        SongSection(SectionType.VERSE, 24, {}, 0.4, "Main groove"),
        SongSection(SectionType.BRIDGE, 16, {"dark": 0.1}, 0.5, "Variation"),
        SongSection(SectionType.VERSE, 24, {}, 0.4, "Return to groove"),
        SongSection(SectionType.OUTRO, 16, {"energy": -0.1, "dreamy": 0.3}, 0.3, "Fade out"),
    ],

    "cinematic_epic": [
        SongSection(SectionType.INTRO, 16, {"dark": 0.2}, 0.2, "Mysterious opening"),
        SongSection(SectionType.BUILD, 12, {"energy": 0.2}, 0.5, "Rising action"),
        SongSection(SectionType.CHORUS, 20, {"energy": 0.4, "aggressive": 0.2}, 0.9, "Epic climax"),
        SongSection(SectionType.BREAKDOWN, 12, {"energy": -0.2, "dreamy": 0.3}, 0.4, "Emotional moment"),
        SongSection(SectionType.BUILD, 12, {"energy": 0.3}, 0.7, "Final rise"),
        SongSection(SectionType.CHORUS, 20, {"energy": 0.5, "aggressive": 0.3}, 1.0, "Ultimate climax"),
        SongSection(SectionType.OUTRO, 16, {"energy": -0.2}, 0.5, "Heroic resolution"),
    ],

    "trap_anthem": [
        SongSection(SectionType.INTRO, 4, {"energy": -0.2}, 0.3, "Minimal intro"),
        SongSection(SectionType.VERSE, 16, {}, 0.6, "Verse 1"),
        SongSection(SectionType.PRE_CHORUS, 8, {"energy": 0.1}, 0.7, "Pre-drop"),
        SongSection(SectionType.DROP, 16, {"energy": 0.3, "aggressive": 0.4}, 1.0, "Drop 1"),
        SongSection(SectionType.VERSE, 16, {"energy": -0.1}, 0.5, "Verse 2"),
        SongSection(SectionType.PRE_CHORUS, 8, {"energy": 0.2}, 0.8, "Pre-drop 2"),
        SongSection(SectionType.DROP, 16, {"energy": 0.4, "aggressive": 0.4}, 1.0, "Drop 2"),
        SongSection(SectionType.OUTRO, 8, {"energy": -0.3}, 0.3, "Outro"),
    ],

    "ambient_journey": [
        SongSection(SectionType.INTRO, 20, {"dreamy": 0.3}, 0.2, "Ethereal opening"),
        SongSection(SectionType.BUILD, 24, {"energy": 0.1, "dreamy": 0.2}, 0.4, "Gradual evolution"),
        SongSection(SectionType.CHORUS, 32, {"energy": 0.2, "dreamy": 0.3}, 0.6, "Peak atmosphere"),
        SongSection(SectionType.BREAKDOWN, 24, {"dark": 0.2, "dreamy": 0.4}, 0.4, "Introspective moment"),
        SongSection(SectionType.OUTRO, 32, {"energy": -0.2, "dreamy": 0.4}, 0.3, "Peaceful resolution"),
    ],
}


def create_song_structure(
    style: str = "standard",
    target_duration: Optional[int] = None
) -> SongStructure:
    """
    Create a song structure

    Args:
        style: Structure style (standard, edm_banger, lofi_chill, etc.)
        target_duration: Optional target duration to scale to

    Returns:
        SongStructure object
    """
    structure = SongStructure(style=style)

    if style not in SONG_STRUCTURES:
        style = "standard"

    sections = SONG_STRUCTURES[style].copy()

    # Add sections
    for section in sections:
        structure.add_section(section)

    # Scale to target duration if specified
    if target_duration and target_duration != structure.total_duration:
        scale_factor = target_duration / structure.total_duration

        for section in structure.sections:
            section.duration = int(section.duration * scale_factor)

        structure.total_duration = target_duration

    return structure


def generate_dynamic_structure(
    base_vibe: Dict[str, float],
    duration: int,
    complexity: str = "medium"
) -> SongStructure:
    """
    Generate a dynamic structure based on vibe and desired complexity

    Args:
        base_vibe: Base vibe characteristics
        duration: Total song duration
        complexity: simple, medium, complex

    Returns:
        SongStructure tailored to the vibe
    """
    structure = SongStructure(style="dynamic")

    # Determine structure based on energy and duration
    energy = base_vibe.get("energy", 0.5)
    aggressive = base_vibe.get("aggressive", 0.3)
    dreamy = base_vibe.get("dreamy", 0.5)

    if energy > 0.7 and aggressive > 0.5:
        # High energy, aggressive → EDM/Trap structure
        base_sections = SONG_STRUCTURES["edm_banger"]
    elif energy < 0.4 and dreamy > 0.6:
        # Low energy, dreamy → Ambient structure
        base_sections = SONG_STRUCTURES["ambient_journey"]
    elif energy < 0.5:
        # Chill vibe → Lo-fi structure
        base_sections = SONG_STRUCTURES["lofi_chill"]
    else:
        # Default → Standard structure
        base_sections = SONG_STRUCTURES["standard"]

    # Scale to target duration
    total_base_duration = sum(s.duration for s in base_sections)
    scale_factor = duration / total_base_duration

    for section in base_sections:
        scaled_section = SongSection(
            type=section.type,
            duration=int(section.duration * scale_factor),
            vibe_modifiers=section.vibe_modifiers.copy(),
            intensity=section.intensity,
            description=section.description
        )
        structure.add_section(scaled_section)

    return structure


def get_structure_names() -> List[str]:
    """Get list of available structure names"""
    return list(SONG_STRUCTURES.keys())

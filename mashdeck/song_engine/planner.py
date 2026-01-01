"""
Song Planner - AI-driven song structure generation
Automatically plans intro, verse, chorus, bridge, outro with energy mapping
"""

import random
import json
from typing import Dict, List, Optional, Tuple

# Musical keys for coherent song generation
KEYS = ["C minor", "D minor", "E minor", "F minor", "G minor",
        "A minor", "C major", "D major", "G major", "A major"]

# Pre-defined song structures by style
# Each tuple: (section_name, bars, energy_level)
DEFAULT_STRUCTURES = {
    "edm": [
        ("intro", 16, 0.3),
        ("verse", 32, 0.5),
        ("chorus", 32, 0.8),
        ("verse", 32, 0.6),
        ("chorus", 32, 0.9),
        ("bridge", 16, 0.4),
        ("final_chorus", 32, 1.0),
        ("outro", 16, 0.2)
    ],
    "lofi": [
        ("intro", 16, 0.2),
        ("main", 64, 0.4),
        ("variation", 64, 0.5),
        ("outro", 16, 0.2)
    ],
    "trap": [
        ("intro", 8, 0.3),
        ("verse", 16, 0.6),
        ("pre_drop", 8, 0.7),
        ("drop", 16, 1.0),
        ("verse", 16, 0.5),
        ("pre_drop", 8, 0.8),
        ("drop", 16, 1.0),
        ("outro", 8, 0.3)
    ],
    "hiphop": [
        ("intro", 8, 0.3),
        ("verse", 16, 0.5),
        ("hook", 8, 0.7),
        ("verse", 16, 0.6),
        ("hook", 8, 0.8),
        ("bridge", 8, 0.4),
        ("hook", 8, 0.9),
        ("outro", 8, 0.3)
    ],
    "ambient": [
        ("intro", 24, 0.2),
        ("build", 32, 0.4),
        ("peak", 48, 0.6),
        ("descent", 32, 0.4),
        ("outro", 24, 0.2)
    ],
    "rock": [
        ("intro", 16, 0.4),
        ("verse", 24, 0.5),
        ("chorus", 24, 0.8),
        ("verse", 24, 0.6),
        ("chorus", 24, 0.9),
        ("solo", 16, 0.7),
        ("final_chorus", 24, 1.0),
        ("outro", 12, 0.3)
    ]
}


def plan_song(
    style: str = "edm",
    bpm: Optional[int] = None,
    key: Optional[str] = None,
    title: Optional[str] = None
) -> Dict:
    """
    Plan a complete song structure

    Args:
        style: Music style (edm, lofi, trap, hiphop, ambient, rock)
        bpm: BPM (auto-selected if None)
        key: Musical key (auto-selected if None)
        title: Song title (auto-generated if None)

    Returns:
        Complete song plan with structure, BPM, key, and sections
    """
    # Auto-select BPM based on style if not specified
    if bpm is None:
        bpm_ranges = {
            "edm": (120, 135),
            "lofi": (70, 90),
            "trap": (135, 155),
            "hiphop": (85, 110),
            "ambient": (60, 80),
            "rock": (110, 140)
        }
        min_bpm, max_bpm = bpm_ranges.get(style, (120, 130))
        bpm = random.randint(min_bpm, max_bpm)

    # Auto-select key if not specified
    if key is None:
        key = random.choice(KEYS)

    # Auto-generate title if not specified
    if title is None:
        adjectives = ["Neon", "Digital", "Midnight", "Electric", "Cosmic",
                     "Shadow", "Crystal", "Urban", "Future", "Sonic"]
        nouns = ["Dreams", "Waves", "Lights", "Pulse", "Journey",
                "Motion", "Echo", "Vibe", "Flow", "Zone"]
        title = f"{random.choice(adjectives)} {random.choice(nouns)}"

    # Get structure for style
    structure = []
    if style not in DEFAULT_STRUCTURES:
        style = "edm"  # Default fallback

    for section, bars, energy in DEFAULT_STRUCTURES[style]:
        structure.append({
            "section": section,
            "bars": bars,
            "energy": energy
        })

    return {
        "title": title,
        "style": style,
        "bpm": bpm,
        "key": key,
        "structure": structure
    }


def plan_vocals(song_plan: Dict) -> List[Dict]:
    """
    Plan where vocals should appear in the song

    Args:
        song_plan: Song plan from plan_song()

    Returns:
        List of vocal placements with type, timing, and energy
    """
    vocal_map = []

    for section in song_plan["structure"]:
        name = section["section"]

        # Hooks on choruses and drops
        if "chorus" in name or "hook" in name or "drop" in name:
            vocal_map.append({
                "section": name,
                "type": "hook",
                "bars": min(8, section["bars"]),
                "energy": section["energy"]
            })

        # Rap on verses (for hip-hop/trap)
        if "verse" in name and song_plan["style"] in ["hiphop", "trap"]:
            vocal_map.append({
                "section": name,
                "type": "rap",
                "bars": section["bars"],
                "energy": section["energy"]
            })

        # Ad-libs on bridges
        if "bridge" in name:
            vocal_map.append({
                "section": name,
                "type": "adlib",
                "bars": 4,
                "energy": section["energy"]
            })

    return vocal_map


def export_song_plan(plan: Dict, output_path: str):
    """Export song plan to JSON file"""
    with open(output_path, 'w') as f:
        json.dump(plan, f, indent=2)


def load_song_plan(input_path: str) -> Dict:
    """Load song plan from JSON file"""
    with open(input_path, 'r') as f:
        return json.load(f)

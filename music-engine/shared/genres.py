"""
Comprehensive genre and sub-genre definitions for music generation
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Genre:
    """Genre definition with characteristics"""
    name: str
    sub_genres: List[str]
    default_bpm_range: tuple
    default_key_preferences: List[str]
    vibe_profile: Dict[str, float]
    instrument_profile: Dict[str, str]
    description: str


# Comprehensive genre database
GENRES = {
    # Electronic
    "synthwave": Genre(
        name="Synthwave",
        sub_genres=["retrowave", "outrun", "darksynth", "dreamwave", "chillwave"],
        default_bpm_range=(100, 130),
        default_key_preferences=["C minor", "D minor", "A minor", "E minor"],
        vibe_profile={"energy": 0.6, "dark": 0.5, "dreamy": 0.7, "aggressive": 0.3},
        instrument_profile={"bass": "analog_mono", "lead": "supersaw", "pad": "warm_pad", "drums": "808"},
        description="80s-inspired electronic music with nostalgic vibes"
    ),

    "techno": Genre(
        name="Techno",
        sub_genres=["detroit_techno", "minimal_techno", "acid_techno", "industrial_techno", "melodic_techno"],
        default_bpm_range=(120, 150),
        default_key_preferences=["A minor", "F minor", "G minor"],
        vibe_profile={"energy": 0.8, "dark": 0.6, "dreamy": 0.2, "aggressive": 0.7},
        instrument_profile={"bass": "fm_bass", "lead": "acid", "pad": "dark_pad", "drums": "909"},
        description="Repetitive, hypnotic electronic dance music"
    ),

    "house": Genre(
        name="House",
        sub_genres=["deep_house", "tech_house", "progressive_house", "tropical_house", "future_house"],
        default_bpm_range=(120, 130),
        default_key_preferences=["C major", "G major", "D major", "A major"],
        vibe_profile={"energy": 0.7, "dark": 0.3, "dreamy": 0.5, "aggressive": 0.4},
        instrument_profile={"bass": "sub_bass", "lead": "pluck", "pad": "string_pad", "drums": "808"},
        description="Four-on-the-floor dance music with soulful elements"
    ),

    "dubstep": Genre(
        name="Dubstep",
        sub_genres=["brostep", "melodic_dubstep", "riddim", "drumstep", "future_bass"],
        default_bpm_range=(140, 150),
        default_key_preferences=["E minor", "B minor", "F# minor"],
        vibe_profile={"energy": 0.9, "dark": 0.7, "dreamy": 0.3, "aggressive": 0.9},
        instrument_profile={"bass": "reese", "lead": "supersaw", "pad": "dark_pad", "drums": "industrial"},
        description="Heavy bass music with wobbles and drops"
    ),

    "trance": Genre(
        name="Trance",
        sub_genres=["progressive_trance", "uplifting_trance", "psytrance", "vocal_trance", "tech_trance"],
        default_bpm_range=(130, 140),
        default_key_preferences=["C minor", "A minor", "D minor"],
        vibe_profile={"energy": 0.8, "dark": 0.4, "dreamy": 0.8, "aggressive": 0.5},
        instrument_profile={"bass": "analog_mono", "lead": "supersaw", "pad": "granular_pad", "drums": "909"},
        description="Euphoric electronic music with buildups and breakdowns"
    ),

    "drum_and_bass": Genre(
        name="Drum and Bass",
        sub_genres=["liquid_dnb", "neurofunk", "jump_up", "jungle", "darkstep"],
        default_bpm_range=(160, 180),
        default_key_preferences=["A minor", "D minor", "E minor"],
        vibe_profile={"energy": 0.9, "dark": 0.6, "dreamy": 0.4, "aggressive": 0.7},
        instrument_profile={"bass": "reese", "lead": "fm_bell", "pad": "dark_pad", "drums": "industrial"},
        description="Fast breakbeats with heavy basslines"
    ),

    # Chill/Ambient
    "lofi": Genre(
        name="Lo-Fi Hip Hop",
        sub_genres=["lofi_beats", "chillhop", "jazzhop", "study_beats", "chill_lofi"],
        default_bpm_range=(70, 90),
        default_key_preferences=["C major", "F major", "G major", "A minor"],
        vibe_profile={"energy": 0.3, "dark": 0.2, "dreamy": 0.7, "aggressive": 0.1},
        instrument_profile={"bass": "sub_bass", "lead": "pluck", "pad": "warm_pad", "drums": "acoustic"},
        description="Relaxed hip hop beats with nostalgic samples"
    ),

    "ambient": Genre(
        name="Ambient",
        sub_genres=["dark_ambient", "space_ambient", "drone", "atmospheric", "cinematic_ambient"],
        default_bpm_range=(60, 80),
        default_key_preferences=["C minor", "D minor", "A minor"],
        vibe_profile={"energy": 0.2, "dark": 0.5, "dreamy": 0.9, "aggressive": 0.1},
        instrument_profile={"bass": "sub_bass", "lead": "fm_bell", "pad": "granular_pad", "drums": "808"},
        description="Atmospheric soundscapes and textures"
    ),

    "chillwave": Genre(
        name="Chillwave",
        sub_genres=["vaporwave", "future_funk", "mallsoft", "hardvapour"],
        default_bpm_range=(80, 110),
        default_key_preferences=["C major", "F major", "A minor"],
        vibe_profile={"energy": 0.4, "dark": 0.3, "dreamy": 0.8, "aggressive": 0.2},
        instrument_profile={"bass": "analog_mono", "lead": "pluck", "pad": "warm_pad", "drums": "808"},
        description="Dreamy, nostalgic electronic music"
    ),

    # Hip Hop/Trap
    "trap": Genre(
        name="Trap",
        sub_genres=["hard_trap", "melodic_trap", "dark_trap", "future_trap", "latin_trap"],
        default_bpm_range=(130, 170),
        default_key_preferences=["C minor", "E minor", "G minor"],
        vibe_profile={"energy": 0.8, "dark": 0.7, "dreamy": 0.3, "aggressive": 0.8},
        instrument_profile={"bass": "sub_bass", "lead": "pluck", "pad": "dark_pad", "drums": "808"},
        description="Heavy bass and hi-hats with aggressive energy"
    ),

    "boom_bap": Genre(
        name="Boom Bap",
        sub_genres=["golden_age", "underground_hip_hop", "jazz_rap", "east_coast"],
        default_bpm_range=(80, 100),
        default_key_preferences=["A minor", "D minor", "C minor"],
        vibe_profile={"energy": 0.6, "dark": 0.5, "dreamy": 0.3, "aggressive": 0.6},
        instrument_profile={"bass": "sub_bass", "lead": "pluck", "pad": "string_pad", "drums": "acoustic"},
        description="Classic hip hop with hard-hitting drums"
    ),

    # Indie/Alternative
    "indie_electronic": Genre(
        name="Indie Electronic",
        sub_genres=["electropop", "indietronica", "dream_pop", "synth_pop"],
        default_bpm_range=(110, 130),
        default_key_preferences=["C major", "G major", "A minor", "E minor"],
        vibe_profile={"energy": 0.6, "dark": 0.3, "dreamy": 0.6, "aggressive": 0.3},
        instrument_profile={"bass": "analog_mono", "lead": "pluck", "pad": "string_pad", "drums": "808"},
        description="Electronic music with indie sensibilities"
    ),

    # Experimental
    "experimental": Genre(
        name="Experimental",
        sub_genres=["glitch", "idm", "noise", "avant_garde", "abstract"],
        default_bpm_range=(80, 140),
        default_key_preferences=["C minor", "F# minor", "A minor"],
        vibe_profile={"energy": 0.5, "dark": 0.6, "dreamy": 0.5, "aggressive": 0.5},
        instrument_profile={"bass": "fm_bass", "lead": "acid", "pad": "granular_pad", "drums": "industrial"},
        description="Unconventional, boundary-pushing electronic music"
    ),

    # World/Ethnic
    "world_fusion": Genre(
        name="World Fusion",
        sub_genres=["ethnic_electronica", "tribal_house", "oriental_bass", "afro_house"],
        default_bpm_range=(100, 125),
        default_key_preferences=["D minor", "E minor", "A minor"],
        vibe_profile={"energy": 0.7, "dark": 0.4, "dreamy": 0.6, "aggressive": 0.4},
        instrument_profile={"bass": "sub_bass", "lead": "fm_bell", "pad": "string_pad", "drums": "acoustic"},
        description="Electronic music with world music influences"
    ),

    # Cinematic
    "cinematic": Genre(
        name="Cinematic",
        sub_genres=["epic", "trailer_music", "orchestral_hybrid", "dark_cinematic", "uplifting_cinematic"],
        default_bpm_range=(70, 130),
        default_key_preferences=["C minor", "D minor", "A minor", "E minor"],
        vibe_profile={"energy": 0.7, "dark": 0.5, "dreamy": 0.6, "aggressive": 0.5},
        instrument_profile={"bass": "sub_bass", "lead": "supersaw", "pad": "granular_pad", "drums": "industrial"},
        description="Dramatic, film-score inspired music"
    ),
}


def get_genre_names() -> List[str]:
    """Get list of all genre names"""
    return list(GENRES.keys())


def get_sub_genres(genre: str) -> List[str]:
    """Get sub-genres for a specific genre"""
    if genre in GENRES:
        return GENRES[genre].sub_genres
    return []


def get_genre_profile(genre: str, sub_genre: str = None) -> Dict:
    """
    Get complete profile for a genre/sub-genre combination

    Returns a ready-to-use music spec profile
    """
    if genre not in GENRES:
        return {}

    g = GENRES[genre]

    # Base profile from genre
    profile = {
        "bpm": (g.default_bpm_range[0] + g.default_bpm_range[1]) // 2,
        "key": g.default_key_preferences[0],
        "vibe": g.vibe_profile.copy(),
        "instruments": g.instrument_profile.copy(),
        "genre_mix": {genre: 1.0}
    }

    # Modify based on sub-genre
    if sub_genre:
        profile = apply_sub_genre_modifiers(profile, genre, sub_genre)

    return profile


def apply_sub_genre_modifiers(profile: Dict, genre: str, sub_genre: str) -> Dict:
    """Apply sub-genre specific modifications to profile"""

    # Sub-genre modifiers
    modifiers = {
        # Synthwave sub-genres
        "darksynth": {"vibe": {"dark": 0.8, "aggressive": 0.6}, "bpm_offset": +10},
        "dreamwave": {"vibe": {"dreamy": 0.9, "energy": 0.4}, "bpm_offset": -10},
        "outrun": {"vibe": {"energy": 0.8, "aggressive": 0.5}, "bpm_offset": +5},

        # Techno sub-genres
        "acid_techno": {"instruments": {"lead": "acid"}, "vibe": {"aggressive": 0.8}},
        "minimal_techno": {"vibe": {"energy": 0.6, "dreamy": 0.3}, "bpm_offset": -10},
        "industrial_techno": {"instruments": {"drums": "industrial"}, "vibe": {"dark": 0.8, "aggressive": 0.9}},

        # Dubstep sub-genres
        "melodic_dubstep": {"vibe": {"dreamy": 0.7, "aggressive": 0.5}, "bpm_offset": -5},
        "riddim": {"vibe": {"aggressive": 1.0, "dark": 0.8}, "instruments": {"bass": "reese"}},

        # Lo-fi sub-genres
        "jazzhop": {"vibe": {"dreamy": 0.8}, "instruments": {"pad": "string_pad"}},
        "study_beats": {"vibe": {"energy": 0.2, "dreamy": 0.8}, "bpm_offset": -10},
    }

    if sub_genre in modifiers:
        mod = modifiers[sub_genre]

        # Apply vibe modifications
        if "vibe" in mod:
            for key, value in mod["vibe"].items():
                profile["vibe"][key] = value

        # Apply instrument changes
        if "instruments" in mod:
            profile["instruments"].update(mod["instruments"])

        # Apply BPM offset
        if "bpm_offset" in mod:
            profile["bpm"] += mod["bpm_offset"]

    return profile


def get_random_genre_mix(num_genres: int = 2) -> Dict[str, float]:
    """Generate a random genre mix"""
    import random

    genres = random.sample(list(GENRES.keys()), min(num_genres, len(GENRES)))

    # Generate random weights
    weights = [random.random() for _ in genres]
    total = sum(weights)

    # Normalize
    return {g: w/total for g, w in zip(genres, weights)}

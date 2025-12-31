"""
Automatic Song Generator

Generates complete songs automatically with AI-driven creativity
"""

import random
from typing import Dict, List, Optional
from .genres import GENRES, get_genre_profile, get_random_genre_mix
from .song_structure import create_song_structure, generate_dynamic_structure, get_structure_names
from .lyrics_generator import generate_lyrics_with_claude, generate_placeholder_lyrics


class AutoSongGenerator:
    """Automatically generates complete song specifications"""

    def __init__(self):
        self.genre_list = list(GENRES.keys())
        self.moods = [
            "energetic", "chill", "dark", "dreamy", "melancholic",
            "uplifting", "aggressive", "peaceful", "mysterious", "euphoric",
            "nostalgic", "futuristic", "epic", "intimate", "chaotic"
        ]
        self.themes = [
            "love", "heartbreak", "freedom", "adventure", "nostalgia",
            "rebellion", "hope", "loneliness", "celebration", "journey",
            "dreams", "night", "city", "nature", "technology",
            "memories", "future", "escape", "belonging", "change"
        ]

    def generate_random_song(
        self,
        duration: Optional[int] = None,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
        include_lyrics: bool = False
    ) -> Dict:
        """
        Generate a completely random song

        Returns a full MusicSpec ready for generation
        """
        # Pick genre
        if not genre:
            genre = random.choice(self.genre_list)

        # Get genre profile
        genre_data = GENRES[genre]
        profile = get_genre_profile(genre)

        # Pick sub-genre (30% chance)
        sub_genre = None
        if random.random() < 0.3 and genre_data.sub_genres:
            sub_genre = random.choice(genre_data.sub_genres)

        # Duration
        if not duration:
            duration = random.randint(90, 180)  # 1.5 to 3 minutes

        # Mood
        if not mood:
            mood = random.choice(self.moods)

        # Theme
        theme = random.choice(self.themes)

        # Create song structure
        structure_style = random.choice(get_structure_names())
        song_structure = create_song_structure(structure_style, duration)

        # Randomize vibe a bit
        vibe = profile["vibe"].copy()
        for key in vibe:
            vibe[key] = max(0.0, min(1.0, vibe[key] + random.uniform(-0.2, 0.2)))

        # Genre mix (sometimes blend genres)
        if random.random() < 0.4:
            # Add a second genre
            genre_mix = get_random_genre_mix(2)
        else:
            genre_mix = {genre: 1.0}

        # Build MusicSpec
        spec = {
            "bpm": profile["bpm"] + random.randint(-10, 10),
            "key": random.choice(genre_data.default_key_preferences),
            "duration": duration,
            "vibe": vibe,
            "genre_mix": genre_mix,
            "instruments": profile["instruments"].copy(),
            "stems": random.choice([True, False]),
            "seed": random.randint(1, 999999),

            # Extended fields
            "genre": genre,
            "sub_genre": sub_genre,
            "mood": mood,
            "theme": theme,
            "structure": {
                "style": structure_style,
                "sections": [
                    {
                        "type": s.type,
                        "duration": s.duration,
                        "vibe_modifiers": s.vibe_modifiers,
                        "intensity": s.intensity
                    }
                    for s in song_structure.sections
                ]
            },
            "title": self._generate_title(genre, mood, theme)
        }

        return spec

    def generate_genre_collection(
        self,
        genre: str,
        count: int = 5,
        variation: str = "medium"
    ) -> List[Dict]:
        """
        Generate a collection of songs in the same genre

        Args:
            genre: Genre to focus on
            count: Number of songs to generate
            variation: low, medium, high (how different songs should be)

        Returns:
            List of MusicSpecs
        """
        songs = []

        for i in range(count):
            # Vary parameters based on variation level
            if variation == "low":
                duration_range = (120, 150)
                vibe_variation = 0.1
            elif variation == "high":
                duration_range = (60, 240)
                vibe_variation = 0.3
            else:  # medium
                duration_range = (90, 180)
                vibe_variation = 0.2

            duration = random.randint(*duration_range)

            song = self.generate_random_song(
                duration=duration,
                genre=genre,
                include_lyrics=False
            )

            # Apply variation
            for key in song["vibe"]:
                song["vibe"][key] = max(0.0, min(1.0,
                    song["vibe"][key] + random.uniform(-vibe_variation, vibe_variation)
                ))

            songs.append(song)

        return songs

    def generate_mood_playlist(
        self,
        mood: str,
        count: int = 8,
        duration_per_song: int = 120
    ) -> List[Dict]:
        """
        Generate a playlist of songs matching a specific mood

        Perfect for creating workout playlists, study music, etc.
        """
        # Map mood to vibe characteristics
        mood_profiles = {
            "energetic": {"energy": 0.9, "aggressive": 0.6},
            "chill": {"energy": 0.3, "dreamy": 0.7},
            "dark": {"dark": 0.8, "aggressive": 0.5},
            "dreamy": {"dreamy": 0.9, "energy": 0.3},
            "uplifting": {"energy": 0.7, "dark": 0.2, "dreamy": 0.5},
            "aggressive": {"aggressive": 0.9, "energy": 0.8, "dark": 0.6},
            "peaceful": {"energy": 0.2, "dreamy": 0.7, "aggressive": 0.1},
        }

        target_vibe = mood_profiles.get(mood, {"energy": 0.5})

        songs = []

        for i in range(count):
            song = self.generate_random_song(
                duration=duration_per_song,
                mood=mood
            )

            # Override vibe to match mood
            for key, value in target_vibe.items():
                song["vibe"][key] = value + random.uniform(-0.1, 0.1)

            # Normalize vibe values
            for key in song["vibe"]:
                song["vibe"][key] = max(0.0, min(1.0, song["vibe"][key]))

            songs.append(song)

        return songs

    def generate_evolution_series(
        self,
        base_spec: Dict,
        steps: int = 5
    ) -> List[Dict]:
        """
        Generate a series of songs that evolve from the base

        Each song progressively changes from the original
        Useful for creating dynamic playlists or showing progression
        """
        series = [base_spec.copy()]

        for i in range(1, steps):
            progress = i / steps

            evolved = base_spec.copy()
            evolved["vibe"] = base_spec["vibe"].copy()

            # Gradually increase energy and decrease dreaminess
            evolved["vibe"]["energy"] = min(1.0, base_spec["vibe"]["energy"] + progress * 0.4)
            evolved["vibe"]["dreamy"] = max(0.0, base_spec["vibe"]["dreamy"] - progress * 0.3)
            evolved["vibe"]["aggressive"] = min(1.0, base_spec["vibe"]["aggressive"] + progress * 0.3)

            # Speed up BPM
            evolved["bpm"] = int(base_spec["bpm"] + progress * 20)

            # New seed for variation
            evolved["seed"] = base_spec.get("seed", 12345) + i

            # Update title
            evolved["title"] = f"{base_spec.get('title', 'Evolution')} - Step {i+1}"

            series.append(evolved)

        return series

    def generate_smart_preset(self, preset_name: str) -> Dict:
        """
        Generate a song from a smart preset

        Presets:
        - "morning_motivation"
        - "deep_focus"
        - "workout_energy"
        - "sleep_ambient"
        - "party_vibes"
        - "gaming_intensity"
        - "meditation"
        - "creative_flow"
        """
        presets = {
            "morning_motivation": {
                "genre": "indie_electronic",
                "mood": "uplifting",
                "theme": "hope",
                "duration": 180,
                "vibe": {"energy": 0.7, "dark": 0.2, "dreamy": 0.5, "aggressive": 0.3},
                "bpm": 115
            },
            "deep_focus": {
                "genre": "lofi",
                "mood": "peaceful",
                "theme": "concentration",
                "duration": 240,
                "vibe": {"energy": 0.3, "dark": 0.2, "dreamy": 0.7, "aggressive": 0.1},
                "bpm": 75
            },
            "workout_energy": {
                "genre": "trap",
                "mood": "energetic",
                "theme": "power",
                "duration": 150,
                "vibe": {"energy": 0.95, "dark": 0.5, "dreamy": 0.2, "aggressive": 0.8},
                "bpm": 150
            },
            "sleep_ambient": {
                "genre": "ambient",
                "mood": "peaceful",
                "theme": "dreams",
                "duration": 300,
                "vibe": {"energy": 0.1, "dark": 0.3, "dreamy": 0.95, "aggressive": 0.05},
                "bpm": 60
            },
            "party_vibes": {
                "genre": "house",
                "mood": "euphoric",
                "theme": "celebration",
                "duration": 180,
                "vibe": {"energy": 0.9, "dark": 0.3, "dreamy": 0.5, "aggressive": 0.4},
                "bpm": 128
            },
            "gaming_intensity": {
                "genre": "dubstep",
                "mood": "aggressive",
                "theme": "battle",
                "duration": 200,
                "vibe": {"energy": 0.9, "dark": 0.7, "dreamy": 0.3, "aggressive": 0.9},
                "bpm": 145
            },
            "meditation": {
                "genre": "ambient",
                "mood": "peaceful",
                "theme": "mindfulness",
                "duration": 600,
                "vibe": {"energy": 0.15, "dark": 0.2, "dreamy": 0.9, "aggressive": 0.05},
                "bpm": 55
            },
            "creative_flow": {
                "genre": "chillwave",
                "mood": "dreamy",
                "theme": "inspiration",
                "duration": 240,
                "vibe": {"energy": 0.5, "dark": 0.3, "dreamy": 0.8, "aggressive": 0.2},
                "bpm": 90
            }
        }

        if preset_name not in presets:
            preset_name = "creative_flow"

        preset = presets[preset_name]

        # Create full spec from preset
        spec = self.generate_random_song(
            duration=preset["duration"],
            genre=preset["genre"],
            mood=preset["mood"]
        )

        # Override with preset values
        spec.update({
            "vibe": preset["vibe"],
            "bpm": preset["bpm"],
            "theme": preset["theme"],
            "title": f"{preset_name.replace('_', ' ').title()} Mix"
        })

        return spec

    def _generate_title(self, genre: str, mood: str, theme: str) -> str:
        """Generate a creative title for the song"""
        prefixes = ["Eternal", "Neon", "Midnight", "Digital", "Lost", "Future", "Dark", "Golden", "Crystal", "Electric"]
        suffixes = ["Dreams", "Nights", "Waves", "Echoes", "Memories", "Vibes", "Journey", "Paradise", "Sky", "Heart"]

        # 50% chance of using theme in title
        if random.random() < 0.5:
            return f"{random.choice(prefixes)} {theme.title()}"
        else:
            return f"{random.choice(prefixes)} {random.choice(suffixes)}"


# Global instance
auto_generator = AutoSongGenerator()


def generate_automatic_song(**kwargs) -> Dict:
    """
    Quick function to generate an automatic song

    Usage:
        song = generate_automatic_song(genre="synthwave", mood="dark")
        song = generate_automatic_song(duration=180)
        song = generate_automatic_song()  # Completely random
    """
    return auto_generator.generate_random_song(**kwargs)


def generate_playlist(mood: str, count: int = 8) -> List[Dict]:
    """Generate a mood-based playlist"""
    return auto_generator.generate_mood_playlist(mood, count)


def get_smart_preset(preset_name: str) -> Dict:
    """Get a smart preset configuration"""
    return auto_generator.generate_smart_preset(preset_name)

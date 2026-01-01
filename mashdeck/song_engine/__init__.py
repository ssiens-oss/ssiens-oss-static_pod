"""
MashDeck Song Engine - Full-length AI song generation with structure
"""

from .planner import plan_song, plan_vocals
from .generator import generate_section, bars_to_seconds
from .arranger import arrange, crossfade
from .master import master
from .pipeline import generate_full_song

__all__ = [
    'plan_song',
    'plan_vocals',
    'generate_section',
    'bars_to_seconds',
    'arrange',
    'crossfade',
    'master',
    'generate_full_song'
]

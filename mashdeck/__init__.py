"""
MashDeck - AI-Powered Music Production System

Complete music generation with vocals, live features, and auto-release
"""

__version__ = "1.0.0"

from .song_engine import generate_full_song
from .vocals import generate_vocals, add_vocals_to_song
from .live import LiveFreestyleEngine, BattleEngine
from .release import AutoReleaser
from .marketplace import MarketplaceStore, PayoutEngine

__all__ = [
    'generate_full_song',
    'generate_vocals',
    'add_vocals_to_song',
    'LiveFreestyleEngine',
    'BattleEngine',
    'AutoReleaser',
    'MarketplaceStore',
    'PayoutEngine'
]

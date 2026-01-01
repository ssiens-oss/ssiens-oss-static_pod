"""
MashDeck Vocal AI System
Complete vocal generation with rap, singing, harmonies, and multilingual support
"""

from .roles.planner import assign_roles
from .rap.generator import generate_rap
from .sing.generator import generate_hook, generate_melody
from .harmony.engine import generate_harmonies, enhance_vocals
from .synthesis import rap_synthesize, sing_synthesize, synthesize
from .pipeline import generate_vocals, add_vocals_to_song

__all__ = [
    'assign_roles',
    'generate_rap',
    'generate_hook',
    'generate_melody',
    'generate_harmonies',
    'enhance_vocals',
    'rap_synthesize',
    'sing_synthesize',
    'synthesize',
    'generate_vocals',
    'add_vocals_to_song'
]

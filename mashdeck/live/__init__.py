"""
MashDeck Live Features
Real-time chat-reactive music, freestyle rap, and AI battle system
"""

from .chat.ingest import ChatIngestor, extract_topics
from .freestyle import LiveFreestyleEngine
from .battle.engine import BattleEngine, BattleScorer

__all__ = [
    'ChatIngestor',
    'extract_topics',
    'LiveFreestyleEngine',
    'BattleEngine',
    'BattleScorer'
]

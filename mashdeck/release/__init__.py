"""
Auto-Release System
Automatic distribution to Spotify, TikTok, YouTube Music, etc.
"""

from .spotify import SpotifyReleaser
from .tiktok import TikTokSoundPublisher
from .youtube import YouTubeMusicPublisher
from .pipeline import AutoReleaser

__all__ = [
    'SpotifyReleaser',
    'TikTokSoundPublisher',
    'YouTubeMusicPublisher',
    'AutoReleaser'
]

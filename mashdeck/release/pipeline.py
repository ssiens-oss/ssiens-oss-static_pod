"""
Auto-Release Pipeline
Orchestrates multi-platform release
"""

import os
from typing import Dict, List

from .spotify import SpotifyReleaser
from .tiktok import TikTokSoundPublisher
from .youtube import YouTubeMusicPublisher


class AutoReleaser:
    """
    Automated multi-platform release system
    """

    def __init__(self):
        self.spotify = SpotifyReleaser()
        self.tiktok = TikTokSoundPublisher()
        self.youtube = YouTubeMusicPublisher()

    def release_everywhere(
        self,
        audio_path: str,
        metadata: Dict,
        platforms: List[str] = None
    ) -> Dict:
        """
        Release to all platforms

        Args:
            audio_path: Path to final mixed song
            metadata: Track metadata
            platforms: List of platforms (default: all)

        Returns:
            Dict with release IDs for each platform
        """
        if platforms is None:
            platforms = ["spotify", "tiktok", "youtube"]

        print("\n" + "=" * 60)
        print("🚀 AUTO-RELEASE PIPELINE")
        print("=" * 60)

        results = {}

        # Spotify/Streaming
        if "spotify" in platforms:
            try:
                result = self.spotify.release_track(audio_path, metadata)
                results["spotify"] = result
            except Exception as e:
                print(f"Spotify release error: {e}")
                results["spotify"] = {"status": "error", "error": str(e)}

        # TikTok
        if "tiktok" in platforms:
            try:
                # Create 30s clip from best part (chorus)
                clip_path = audio_path.replace(".wav", "_tiktok_clip.wav")

                # TODO: Intelligently find best 30s section
                self.tiktok.create_hook_clip(
                    audio_path,
                    clip_path,
                    start_time=60,  # Assume chorus at 60s
                    duration=30
                )

                result = self.tiktok.upload_sound(
                    clip_path,
                    title=metadata.get("title", "MashDeck Track"),
                    tags=["#mashdeck", "#aimusic", "#edm"]
                )

                results["tiktok"] = result

            except Exception as e:
                print(f"TikTok upload error: {e}")
                results["tiktok"] = {"status": "error", "error": str(e)}

        # YouTube
        if "youtube" in platforms:
            try:
                result = self.youtube.upload_track(audio_path, metadata)
                results["youtube"] = result
            except Exception as e:
                print(f"YouTube upload error: {e}")
                results["youtube"] = {"status": "error", "error": str(e)}

        print("\n" + "=" * 60)
        print("✓ RELEASE PIPELINE COMPLETE")
        print("=" * 60)

        for platform, result in results.items():
            status = result.get("status", "unknown")
            print(f"  {platform.upper()}: {status}")

        print("=" * 60)

        return results

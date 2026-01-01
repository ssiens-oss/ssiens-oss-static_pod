"""
Spotify Release Integration
Automated distribution via distributor API
"""

import os
import json
from typing import Dict, Optional


class SpotifyReleaser:
    """
    Spotify release manager

    Uses distributor API (like DistroKid, TuneCore, etc.)
    """

    def __init__(self, api_key: Optional[str] = None, distributor: str = "distrokid"):
        self.api_key = api_key or os.getenv("DISTRIBUTOR_API_KEY")
        self.distributor = distributor

    def release_track(
        self,
        audio_path: str,
        metadata: Dict,
        release_type: str = "single"
    ) -> Dict:
        """
        Release track to Spotify

        Args:
            audio_path: Path to audio file (WAV/FLAC)
            metadata: Track metadata
            release_type: "single" or "album"

        Returns:
            Release info dict
        """
        print(f"\n📀 Releasing to Spotify via {self.distributor}...")

        # Validate audio
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Prepare release data
        release_data = {
            "title": metadata.get("title", "Untitled"),
            "artist": metadata.get("artist", "MashDeck AI"),
            "album": metadata.get("album", metadata.get("title")),
            "genre": metadata.get("genre", "Electronic"),
            "release_date": metadata.get("release_date", "today"),
            "audio_file": audio_path,
            "artwork": metadata.get("artwork"),
            "isrc": metadata.get("isrc"),  # Optional ISRC code
            "upc": metadata.get("upc"),    # Optional UPC code
            "release_type": release_type
        }

        # TODO: Actual API integration
        # For now, save release data locally
        release_id = self._save_release_data(release_data)

        print(f"✓ Release prepared: {release_id}")
        print(f"  Title: {release_data['title']}")
        print(f"  Artist: {release_data['artist']}")
        print(f"  Status: Pending distribution")

        return {
            "release_id": release_id,
            "status": "pending",
            "distributor": self.distributor,
            "platforms": ["spotify", "apple_music", "amazon_music"],
            "release_data": release_data
        }

    def _save_release_data(self, data: Dict) -> str:
        """Save release data locally"""
        import time

        release_id = f"release_{int(time.time())}"
        output_dir = "releases"
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, f"{release_id}.json")

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        return release_id

    def check_status(self, release_id: str) -> str:
        """Check release status"""
        # TODO: Implement status checking
        return "pending"

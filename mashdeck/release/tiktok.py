"""
TikTok Sound Publisher
Upload sounds to TikTok sound library
"""

import os
import json
from typing import Dict, Optional


class TikTokSoundPublisher:
    """Publish sounds to TikTok"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TIKTOK_API_KEY")

    def upload_sound(
        self,
        audio_path: str,
        title: str,
        tags: list = None,
        description: str = ""
    ) -> Dict:
        """
        Upload sound to TikTok

        Args:
            audio_path: Path to audio (preferably 15-60s clip)
            title: Sound title
            tags: List of hashtags
            description: Sound description

        Returns:
            Upload result
        """
        print(f"\n🎵 Uploading sound to TikTok...")

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio not found: {audio_path}")

        # Prepare sound data
        sound_data = {
            "title": title,
            "audio_file": audio_path,
            "tags": tags or ["#mashdeck", "#aimusic"],
            "description": description
        }

        # TODO: Actual TikTok API integration
        # For now, save upload data
        upload_id = self._save_upload_data(sound_data)

        print(f"✓ Sound upload prepared: {upload_id}")
        print(f"  Title: {title}")
        print(f"  Tags: {', '.join(sound_data['tags'])}")

        return {
            "upload_id": upload_id,
            "status": "pending",
            "platform": "tiktok",
            "sound_data": sound_data
        }

    def create_hook_clip(
        self,
        full_audio: str,
        out_path: str,
        start_time: float = 0,
        duration: float = 30.0
    ) -> str:
        """
        Extract hook/best part for TikTok (30s optimal)

        Args:
            full_audio: Full song path
            out_path: Output clip path
            start_time: Start time in seconds
            duration: Clip duration

        Returns:
            Path to clip
        """
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_wav(full_audio)

            # Extract clip
            start_ms = int(start_time * 1000)
            end_ms = int((start_time + duration) * 1000)

            clip = audio[start_ms:end_ms]

            # Fade in/out for smoothness
            clip = clip.fade_in(500).fade_out(1000)

            clip.export(out_path, format="wav")

            print(f"✓ Created TikTok clip: {out_path}")

            return out_path

        except Exception as e:
            print(f"Error creating clip: {e}")
            return ""

    def _save_upload_data(self, data: Dict) -> str:
        """Save upload data locally"""
        import time

        upload_id = f"tiktok_{int(time.time())}"
        output_dir = "tiktok_uploads"
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, f"{upload_id}.json")

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        return upload_id

"""
Live Freestyle Rap Engine
Generates freestyle rap in real-time based on chat input
"""

import os
import sys
import time
from typing import List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vocals.rap.generator import generate_freestyle
from vocals.synthesis import rap_synthesize
from .chat.ingest import extract_topics, ChatIngestor


class LiveFreestyleEngine:
    """
    Real-time freestyle rap generator

    Reacts to chat topics and generates bars on the fly
    """

    def __init__(self, output_dir: str = "live_output"):
        self.output_dir = output_dir
        self.chat_ingestor = ChatIngestor()
        self.last_freestyle_time = 0
        self.freestyle_cooldown = 30.0  # seconds between freestyles

        os.makedirs(output_dir, exist_ok=True)

    def can_generate(self) -> bool:
        """Check if enough time has passed for new freestyle"""
        return (time.time() - self.last_freestyle_time) >= self.freestyle_cooldown

    def generate_from_chat(
        self,
        bars: int = 4,
        style: str = "aggressive"
    ) -> Optional[str]:
        """
        Generate freestyle from recent chat

        Args:
            bars: Number of bars to generate
            style: Rap style

        Returns:
            Path to generated audio, or None if cooldown active
        """
        if not self.can_generate():
            return None

        # Get recent messages
        recent = self.chat_ingestor.get_recent_messages(50)

        if not recent:
            topics = ["energy", "vibe", "music"]
        else:
            topics = extract_topics(recent)

        print(f"\n🎤 Live Freestyle - Topics: {', '.join(topics)}")

        # Generate lyrics
        lyrics = generate_freestyle(topics, bars, style)
        print(f"Lyrics:\n{lyrics}\n")

        # Synthesize
        timestamp = int(time.time())
        output_path = os.path.join(
            self.output_dir,
            f"freestyle_{timestamp}.wav"
        )

        rap_synthesize(lyrics, output_path, style=style)

        self.last_freestyle_time = time.time()

        return output_path

    def add_chat_message(self, username: str, message: str):
        """Add a chat message to the ingestor"""
        self.chat_ingestor.add_message(username, message, time.time())

    def trigger_freestyle(
        self,
        bars: int = 4,
        style: str = "aggressive",
        force: bool = False
    ) -> Optional[str]:
        """
        Trigger a freestyle (bypasses cooldown if forced)

        Args:
            bars: Number of bars
            style: Style
            force: Force generation ignoring cooldown

        Returns:
            Path to generated audio
        """
        if force:
            self.last_freestyle_time = 0

        return self.generate_from_chat(bars, style)

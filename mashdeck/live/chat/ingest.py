"""
Chat Ingestion System
Connects to YouTube/TikTok chat and extracts topics for live generation
"""

from typing import List, Dict
from collections import Counter
import re


class ChatIngestor:
    """Ingests and analyzes chat messages"""

    def __init__(self):
        self.messages = []
        self.topic_history = []

    def add_message(self, username: str, message: str, timestamp: float = None):
        """Add a chat message"""
        self.messages.append({
            "username": username,
            "message": message,
            "timestamp": timestamp or 0
        })

    def get_recent_messages(self, count: int = 50) -> List[Dict]:
        """Get recent messages"""
        return self.messages[-count:]

    def clear_history(self):
        """Clear message history"""
        self.messages = []
        self.topic_history = []


def extract_topics(chat_msgs: List[Dict], top_n: int = 5) -> List[str]:
    """
    Extract trending topics from chat messages

    Args:
        chat_msgs: List of chat message dicts
        top_n: Number of top topics to return

    Returns:
        List of top topic keywords
    """
    # Collect all words
    word_counts = Counter()

    for msg in chat_msgs:
        text = msg.get("message", "")

        # Clean and split
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter out common words
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        words = [w for w in words if w not in stopwords and len(w) > 2]

        word_counts.update(words)

    # Get top topics
    top_topics = [word for word, count in word_counts.most_common(top_n)]

    return top_topics if top_topics else ["energy", "vibe", "music"]


def calculate_chat_rate(
    chat_msgs: List[Dict],
    window_seconds: float = 10.0
) -> float:
    """
    Calculate messages per second

    Args:
        chat_msgs: Chat messages with timestamps
        window_seconds: Time window to analyze

    Returns:
        Messages per second
    """
    if not chat_msgs:
        return 0.0

    # Get current time
    latest_time = max(msg.get("timestamp", 0) for msg in chat_msgs)
    start_time = latest_time - window_seconds

    # Count messages in window
    count = sum(1 for msg in chat_msgs
                if msg.get("timestamp", 0) >= start_time)

    return count / window_seconds


def detect_hype_spike(
    current_rate: float,
    baseline_rate: float,
    threshold_multiplier: float = 2.0
) -> bool:
    """
    Detect if chat is spiking (hype moment)

    Args:
        current_rate: Current message rate
        baseline_rate: Normal baseline rate
        threshold_multiplier: Multiplier for spike detection

    Returns:
        True if spike detected
    """
    return current_rate > baseline_rate * threshold_multiplier


def extract_emoji_sentiment(chat_msgs: List[Dict]) -> Dict[str, int]:
    """
    Extract emoji sentiment from chat

    Args:
        chat_msgs: Chat messages

    Returns:
        Dict with emoji counts
    """
    emoji_counts = Counter()

    # Common emoji patterns
    positive_emojis = ['🔥', '💯', '🎵', '🎶', '💪', '👏', '🎉', '✨']
    negative_emojis = ['😴', '👎', '💤']

    for msg in chat_msgs:
        text = msg.get("message", "")

        for emoji in positive_emojis + negative_emojis:
            emoji_counts[emoji] += text.count(emoji)

    return dict(emoji_counts)

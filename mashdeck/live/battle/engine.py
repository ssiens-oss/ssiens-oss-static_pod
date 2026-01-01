"""
AI Rapper Battle Engine
Chat vs Chat competitive rap battles with real-time scoring
"""

import os
import sys
import time
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from vocals.rap.generator import generate_freestyle
from vocals.synthesis import rap_synthesize
from live.chat.ingest import ChatIngestor, extract_topics, calculate_chat_rate


@dataclass
class BattleStats:
    """Statistics for one side of a battle"""
    msg_rate: float = 0.0
    unique_users: int = 0
    votes: int = 0
    keyword_entropy: float = 0.0
    total_score: float = 0.0


@dataclass
class BattleRound:
    """A single round of the battle"""
    round_num: int
    side_a_lyrics: str
    side_b_lyrics: str
    side_a_score: float
    side_b_score: float
    winner: str
    timestamp: float


class BattleScorer:
    """Scores battle performance"""

    @staticmethod
    def compute_score(stats: BattleStats) -> float:
        """
        Compute battle score from stats

        Args:
            stats: Battle statistics

        Returns:
            Total score (0-100)
        """
        # Weighted scoring
        score = (
            stats.msg_rate * 35.0 +           # 35% weight
            stats.unique_users * 25.0 +       # 25% weight
            stats.votes * 25.0 +              # 25% weight
            stats.keyword_entropy * 15.0      # 15% weight
        )

        return min(100.0, max(0.0, score))


class BattleEngine:
    """
    Main battle engine

    Manages two-sided rap battles with chat as fuel
    """

    def __init__(self, output_dir: str = "battles"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.chat_a = ChatIngestor()
        self.chat_b = ChatIngestor()

        self.rounds: List[BattleRound] = []
        self.current_round = 0
        self.battle_active = False

        self.stats_a = BattleStats()
        self.stats_b = BattleStats()

    def start_battle(self):
        """Start a new battle"""
        self.battle_active = True
        self.current_round = 0
        self.rounds = []
        self.stats_a = BattleStats()
        self.stats_b = BattleStats()

        print("\n" + "=" * 60)
        print("🎤 BATTLE STARTED 🎤")
        print("=" * 60)

    def end_battle(self) -> str:
        """
        End battle and declare winner

        Returns:
            Winner ("A" or "B")
        """
        self.battle_active = False

        # Calculate total scores
        total_a = sum(r.side_a_score for r in self.rounds)
        total_b = sum(r.side_b_score for r in self.rounds)

        winner = "A" if total_a > total_b else "B"

        print("\n" + "=" * 60)
        print("🏆 BATTLE COMPLETE 🏆")
        print("=" * 60)
        print(f"Side A Total: {total_a:.1f}")
        print(f"Side B Total: {total_b:.1f}")
        print(f"WINNER: SIDE {winner}")
        print("=" * 60)

        # Save battle log
        self._save_battle_log(winner, total_a, total_b)

        return winner

    def execute_round(
        self,
        bars: int = 4,
        duration: int = 30
    ) -> BattleRound:
        """
        Execute one round of the battle

        Args:
            bars: Bars per rapper
            duration: Round duration in seconds

        Returns:
            BattleRound result
        """
        self.current_round += 1

        print(f"\n--- ROUND {self.current_round} ---")

        # Update stats from chat
        self._update_stats()

        # Generate topics from each chat
        topics_a = extract_topics(self.chat_a.get_recent_messages(50))
        topics_b = extract_topics(self.chat_b.get_recent_messages(50))

        print(f"Side A Topics: {', '.join(topics_a)}")
        print(f"Side B Topics: {', '.join(topics_b)}")

        # Generate lyrics
        lyrics_a = generate_freestyle(topics_a, bars, style="aggressive")
        lyrics_b = generate_freestyle(topics_b, bars, style="aggressive")

        print(f"\nSide A:\n{lyrics_a}\n")
        print(f"Side B:\n{lyrics_b}\n")

        # Synthesize audio
        audio_a = self._synthesize_round_audio("A", self.current_round, lyrics_a)
        audio_b = self._synthesize_round_audio("B", self.current_round, lyrics_b)

        # Score round
        score_a = BattleScorer.compute_score(self.stats_a)
        score_b = BattleScorer.compute_score(self.stats_b)

        winner = "A" if score_a > score_b else "B"

        print(f"Score A: {score_a:.1f}")
        print(f"Score B: {score_b:.1f}")
        print(f"Round Winner: {winner}")

        # Create round record
        round_result = BattleRound(
            round_num=self.current_round,
            side_a_lyrics=lyrics_a,
            side_b_lyrics=lyrics_b,
            side_a_score=score_a,
            side_b_score=score_b,
            winner=winner,
            timestamp=time.time()
        )

        self.rounds.append(round_result)

        return round_result

    def add_message_a(self, username: str, message: str):
        """Add message to Side A chat"""
        self.chat_a.add_message(username, message, time.time())

    def add_message_b(self, username: str, message: str):
        """Add message to Side B chat"""
        self.chat_b.add_message(username, message, time.time())

    def add_vote_a(self):
        """Add vote for Side A"""
        self.stats_a.votes += 1

    def add_vote_b(self):
        """Add vote for Side B"""
        self.stats_b.votes += 1

    def _update_stats(self):
        """Update battle statistics from chat"""
        # Side A
        msgs_a = self.chat_a.get_recent_messages(100)
        self.stats_a.msg_rate = calculate_chat_rate(msgs_a, window_seconds=10)
        self.stats_a.unique_users = len(set(m.get("username") for m in msgs_a))

        topics_a = extract_topics(msgs_a, top_n=10)
        self.stats_a.keyword_entropy = len(set(topics_a)) / max(1, len(topics_a))

        # Side B
        msgs_b = self.chat_b.get_recent_messages(100)
        self.stats_b.msg_rate = calculate_chat_rate(msgs_b, window_seconds=10)
        self.stats_b.unique_users = len(set(m.get("username") for m in msgs_b))

        topics_b = extract_topics(msgs_b, top_n=10)
        self.stats_b.keyword_entropy = len(set(topics_b)) / max(1, len(topics_b))

    def _synthesize_round_audio(self, side: str, round_num: int, lyrics: str) -> str:
        """Synthesize audio for a round"""
        output_path = os.path.join(
            self.output_dir,
            f"round_{round_num}_side_{side}.wav"
        )

        rap_synthesize(lyrics, output_path)

        return output_path

    def _save_battle_log(self, winner: str, score_a: float, score_b: float):
        """Save battle results to JSON"""
        log_path = os.path.join(
            self.output_dir,
            f"battle_{int(time.time())}.json"
        )

        log_data = {
            "winner": winner,
            "total_score_a": score_a,
            "total_score_b": score_b,
            "rounds": [asdict(r) for r in self.rounds],
            "stats_a": asdict(self.stats_a),
            "stats_b": asdict(self.stats_b)
        }

        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        print(f"✓ Battle log saved: {log_path}")

"""
Game state representation for Wordle Arena.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class GameMode(Enum):
    """Game mode enumeration."""

    SINGLE = "single"  # solo practice
    VS_AI_TURN = "vs_ai_turn"  # turn‑based vs AI
    VS_AI_RACE = "vs_ai_race"  # race vs AI
    VS_HUMAN_TURN = "vs_human_turn"  # turn‑based two humans
    VS_HUMAN_RACE = "vs_human_race"  # race two humans

    def is_race(self) -> bool:
        """Return True if this mode is a race mode."""
        return self in (GameMode.VS_AI_RACE, GameMode.VS_HUMAN_RACE)

    def is_turn_based(self) -> bool:
        """Return True if this mode is turn‑based."""
        return self in (GameMode.VS_AI_TURN, GameMode.VS_HUMAN_TURN)

    def is_single(self) -> bool:
        """Return True if this mode is single player."""
        return self == GameMode.SINGLE


class PlayerType(Enum):
    """Player type."""

    HUMAN = "human"
    AI = "ai"


@dataclass
class GuessEntry:
    """Record of a single guess."""

    player_id: str  # "player1", "player2", "ai"
    guess: str
    feedback: List[int]  # 0/1/2
    timestamp: float = field(default_factory=time.time)


@dataclass
class GameState:
    """State of a Wordle game.

    Attributes:
        mode: Current game mode.
        target_word: The secret word (lowercase).
        target_length: Length of target word.
        first_letter: First letter of target word (if revealed).
        max_attempts: Maximum allowed guesses (length + 1).
        guesses: List of GuessEntry objects.
        current_player: Which player's turn (for turn‑based modes).
        player1_id: Identifier for player 1.
        player2_id: Identifier for player 2.
        player_types: Dict mapping player_id to PlayerType.
        hard_mode: Whether Hard Mode is active.
        time_limit: Time limit per turn in seconds (0 = unlimited).
        start_time: Timestamp when game started.
        turn_start_time: Timestamp when current turn started (for timer).
        winner: Player id of winner, None if no winner yet.
        game_over: Whether game has ended.
        config: Additional configuration dict.
    """

    mode: GameMode
    target_word: str
    target_length: int
    first_letter: str
    max_attempts: int
    guesses: List[GuessEntry] = field(default_factory=list)
    current_player: str = "player1"
    player1_id: str = "player1"
    player2_id: str = "player2"
    player_types: Dict[str, PlayerType] = field(
        default_factory=lambda: {"player1": PlayerType.HUMAN, "player2": PlayerType.AI}
    )
    hard_mode: bool = False
    time_limit: float = 0.0
    start_time: float = field(default_factory=time.time)
    turn_start_time: float = field(default_factory=time.time)
    winner: Optional[str] = None
    game_over: bool = False
    config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and set derived attributes."""
        if self.target_length != len(self.target_word):
            raise ValueError("Target length mismatch")
        if self.first_letter != self.target_word[0]:
            raise ValueError("First letter mismatch")

    @property
    def attempts_used(self) -> int:
        """Number of guesses made so far."""
        return len(self.guesses)

    @property
    def attempts_left(self) -> int:
        """Remaining guesses before max attempts."""
        return self.max_attempts - self.attempts_used

    def add_guess(self, player_id: str, guess: str, feedback: List[int]) -> None:
        """Record a new guess.

        Args:
            player_id: Which player made the guess.
            guess: The guessed word.
            feedback: Feedback list.
        """
        if self.game_over:
            raise RuntimeError("Cannot add guess after game over")
        self.guesses.append(GuessEntry(player_id, guess, feedback))
        # Check for win
        if all(f == 2 for f in feedback):
            self.winner = player_id
            self.game_over = True
        elif not self.mode.is_turn_based() and self.attempts_used >= self.max_attempts:
            self.game_over = True

    def get_player_guesses(self, player_id: str) -> List[GuessEntry]:
        """Return all guesses made by a specific player.

        Args:
            player_id: Player identifier.

        Returns:
            List of GuessEntry objects.
        """
        return [g for g in self.guesses if g.player_id == player_id]

    def get_last_feedback(self) -> Optional[List[int]]:
        """Get feedback of the most recent guess, if any."""
        if not self.guesses:
            return None
        return self.guesses[-1].feedback

    def switch_turn(self) -> None:
        """Switch current player in turn‑based modes."""
        if self.current_player == self.player1_id:
            self.current_player = self.player2_id
        else:
            self.current_player = self.player1_id
        self.turn_start_time = time.time()

    def is_turn_based(self) -> bool:
        """Whether the current mode is turn‑based."""
        return self.mode.is_turn_based()

    def is_race(self) -> bool:
        """Whether the current mode is race."""
        return self.mode.is_race()

    def is_single(self) -> bool:
        """Whether the current mode is single player."""
        return self.mode.is_single()

    def time_remaining(self) -> float:
        """Remaining time for current turn (if time limit > 0)."""
        if self.time_limit <= 0:
            return float("inf")
        elapsed = time.time() - self.turn_start_time
        remaining = self.time_limit - elapsed
        return max(0.0, remaining)

    def is_timed_out(self) -> bool:
        """Check if current turn has timed out."""
        return self.time_limit > 0 and self.time_remaining() <= 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize game state to dictionary (for replay)."""
        return {
            "mode": self.mode.value,
            "target_word": self.target_word,
            "target_length": self.target_length,
            "first_letter": self.first_letter,
            "max_attempts": self.max_attempts,
            "guesses": [
                {
                    "player": g.player_id,
                    "guess": g.guess,
                    "feedback": g.feedback,
                    "timestamp": g.timestamp,
                }
                for g in self.guesses
            ],
            "current_player": self.current_player,
            "hard_mode": self.hard_mode,
            "time_limit": self.time_limit,
            "winner": self.winner,
            "game_over": self.game_over,
            "start_time": self.start_time,
        }

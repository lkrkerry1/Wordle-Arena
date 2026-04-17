"""
Game controller orchestrates game flow, AI turns, timers, and race coordination.
"""

import random
import threading
import time
from typing import Callable, Optional, List, Tuple, Any
from .game_state import GameState, GameMode, PlayerType
from .feedback import get_feedback
from .ai_player import AIPlayer


class GameController:
    """Controls the game logic and UI updates.

    Attributes:
        game_state: Current game state.
        ai_player: AI player instance (if any).
        on_state_change: Callback when game state changes.
        on_timer_update: Callback for timer updates.
        on_game_over: Callback when game ends.
        timer_thread: Optional thread for periodic timer updates.
        ai_thread: Optional thread for AI guessing in race mode.
        stop_event: threading.Event to stop background threads.
    """

    def __init__(
        self,
        game_state: GameState,
        ai_player: Optional[AIPlayer] = None,
        on_state_change: Optional[Callable[[], None]] = None,
        on_timer_update: Optional[Callable[[float], None]] = None,
        on_game_over: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize controller.

        Args:
            game_state: Initial game state.
            ai_player: AI player instance (required for modes with AI).
            on_state_change: Called after any state change (e.g., new guess).
            on_timer_update: Called with remaining seconds each second.
            on_game_over: Called when game ends.
        """
        self.game_state = game_state
        self.ai_player = ai_player
        self.on_state_change = on_state_change or (lambda: None)
        self.on_timer_update = on_timer_update or (lambda _: None)
        self.on_game_over = on_game_over or (lambda: None)
        self.timer_thread: Optional[threading.Thread] = None
        self.ai_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self._lock = threading.RLock()

    def start(self) -> None:
        """Start the game (start timers, AI if needed)."""
        if self.game_state.is_turn_based() and self.game_state.time_limit > 0:
            self._start_timer_thread()
        if self.game_state.is_race() and self._is_ai_involved():
            self._start_ai_race_thread()

    def stop(self) -> None:
        """Stop all background threads."""
        self.stop_event.set()
        if self.ai_player:
            self.ai_player.stop()
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1.0)
        if self.ai_thread and self.ai_thread.is_alive():
            self.ai_thread.join(timeout=1.0)

    def _is_ai_involved(self) -> bool:
        """Check if AI is a participant in current mode."""
        mode = self.game_state.mode
        return mode in (GameMode.VS_AI_TURN, GameMode.VS_AI_RACE)

    def _start_timer_thread(self) -> None:
        """Start a thread that updates timer every second."""

        def timer_loop() -> None:
            while not self.stop_event.is_set() and not self.game_state.game_over:
                remaining = self.game_state.time_remaining()
                self.on_timer_update(remaining)
                if remaining <= 0:
                    self._handle_timeout()
                    break
                time.sleep(1)

        self.timer_thread = threading.Thread(target=timer_loop, daemon=True)
        self.timer_thread.start()

    def _start_ai_race_thread(self) -> None:
        """Start AI guessing loop for race mode."""
        if self.ai_player is None:
            return
        # Reset AI stop flag
        self.ai_player.reset_stop()
        # Define callback that will be called with each AI guess
        def ai_guess_callback(guess: str) -> None:
            # The AI does not know the answer; we need to compute feedback.
            # In race mode, AI guesses are submitted to the game state as if
            # they were a player's guess, but feedback is computed using the target.
            with self._lock:
                if self.game_state.game_over:
                    return
                feedback = get_feedback(guess, self.game_state.target_word)
                self.game_state.add_guess(self.game_state.player2_id, guess, feedback)
                self.on_state_change()
                # Check if AI just won
                if self.game_state.game_over:
                    self.on_game_over()

        # Run AI loop in a separate thread
        def ai_loop() -> None:
            self.ai_player.race_mode_guess_loop(
                length=self.game_state.target_length,
                first_letter=self.game_state.first_letter,
                hard_mode=self.game_state.hard_mode,
                callback=ai_guess_callback,
                stop_event=self.stop_event,
            )

        self.ai_thread = threading.Thread(target=ai_loop, daemon=True)
        self.ai_thread.start()

    def submit_guess(self, player_id: str, guess: str) -> bool:
        """Submit a guess for a human player.

        Args:
            player_id: Which player.
            guess: Guessed word (lowercase).

        Returns:
            True if guess was accepted, False otherwise.
        """
        with self._lock:
            if self.game_state.game_over:
                return False
            # Validate guess length and existence (should be done by UI)
            # Compute feedback
            feedback = get_feedback(guess, self.game_state.target_word)
            self.game_state.add_guess(player_id, guess, feedback)
            self.on_state_change()
            # If turn‑based, switch turn
            if self.game_state.is_turn_based():
                self.game_state.switch_turn()
                # If next player is AI, trigger AI turn
                if (
                    self._is_ai_involved()
                    and self.game_state.current_player == self.game_state.player2_id
                ):
                    self._trigger_ai_turn()
            # Check game over
            if self.game_state.game_over:
                self.on_game_over()
            return True

    def _trigger_ai_turn(self) -> None:
        """Make AI take a turn (turn‑based mode)."""
        if self.ai_player is None:
            return
        # Run AI decision in a separate thread to avoid blocking UI
        def ai_turn() -> None:
            # Simulate thinking delay
            time.sleep(random.uniform(0.5, 1.5))
            with self._lock:
                if self.game_state.game_over:
                    return
                guess = self.ai_player.make_guess(
                    length=self.game_state.target_length,
                    first_letter=self.game_state.first_letter,
                    hard_mode=self.game_state.hard_mode,
                    previous_feedback=[
                        (g.guess, g.feedback)
                        for g in self.game_state.get_player_guesses(
                            self.game_state.player2_id
                        )
                    ],
                )
                feedback = get_feedback(guess, self.game_state.target_word)
                self.game_state.add_guess(self.game_state.player2_id, guess, feedback)
                self.game_state.switch_turn()
                self.on_state_change()
                if self.game_state.game_over:
                    self.on_game_over()

        threading.Thread(target=ai_turn, daemon=True).start()

    def _handle_timeout(self) -> None:
        """Handle timeout of current turn."""
        with self._lock:
            if self.game_state.game_over:
                return
            # Current player loses
            self.game_state.winner = (
                self.game_state.player2_id
                if self.game_state.current_player == self.game_state.player1_id
                else self.game_state.player1_id
            )
            self.game_state.game_over = True
            self.on_state_change()
            self.on_game_over()

    def get_replay_data(self) -> List[Tuple[str, str, List[int]]]:
        """Get data suitable for replay display.

        Returns:
            List of (player_id, guess, feedback) for all guesses.
        """
        return [
            (g.player_id, g.guess, g.feedback)
            for g in self.game_state.guesses
        ]


# Helper function to create a game state from configuration
def create_game_state(
    mode: GameMode,
    target_word: str,
    hard_mode: bool = False,
    time_limit: float = 0,
    player1_type: PlayerType = PlayerType.HUMAN,
    player2_type: PlayerType = PlayerType.AI,
) -> GameState:
    """Create a GameState with appropriate defaults.

    Args:
        mode: Game mode.
        target_word: The secret word.
        hard_mode: Hard mode flag.
        time_limit: Time limit per turn (0 = unlimited).
        player1_type: Type of player 1.
        player2_type: Type of player 2.

    Returns:
        GameState instance.
    """
    length = len(target_word)
    first_letter = target_word[0]
    max_attempts = length + 1
    player_types = {"player1": player1_type, "player2": player2_type}
    return GameState(
        mode=mode,
        target_word=target_word,
        target_length=length,
        first_letter=first_letter,
        max_attempts=max_attempts,
        player_types=player_types,
        hard_mode=hard_mode,
        time_limit=time_limit,
    )
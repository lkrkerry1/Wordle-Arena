"""
AI player using maximum information entropy (cross‑entropy) strategy.
"""

import math
import random
import threading
import time
from typing import Dict, List, Optional, Tuple, Set
from functools import lru_cache

from .feedback import get_feedback_cached, feedback_to_pattern
from .word_bank import get_word_bank


class AIPlayer:
    """AI player that guesses words based on entropy.

    Attributes:
        temperature: float between 0.0 (pure greedy) and 1.0 (more random).
        min_delay: minimum delay between guesses in seconds (race mode).
        max_delay: maximum delay between guesses in seconds (race mode).
        word_bank: reference to the global word bank.
        candidate_cache: Dict[Tuple[int, ...], str] mapping candidate set signature to best guess.
    """

    def __init__(
        self,
        temperature: float = 0.0,
        min_delay: float = 0.5,
        max_delay: float = 2.0,
    ) -> None:
        """Initialize AI player.

        Args:
            temperature: randomness factor (0 = deterministic).
            min_delay: minimum thinking delay for race mode.
            max_delay: maximum thinking delay for race mode.
        """
        self.temperature = max(0.0, min(temperature, 1.0))
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.word_bank = get_word_bank()
        self.candidate_cache: Dict[Tuple[int, ...], str] = {}
        self._stop_thread = threading.Event()

    def stop(self) -> None:
        """Signal AI to stop any ongoing background guessing."""
        self._stop_thread.set()

    def reset_stop(self) -> None:
        """Reset stop flag (call before new game)."""
        self._stop_thread.clear()

    def get_candidates(
        self,
        length: int,
        first_letter: Optional[str] = None,
        hard_mode: bool = False,
        previous_feedback: List[Tuple[str, List[int]]] = None,
    ) -> List[str]:
        """Get candidate words that match current constraints.

        Args:
            length: Word length.
            first_letter: If provided, restrict to words starting with this letter.
            hard_mode: Whether Hard Mode is active.
            previous_feedback: For Hard Mode filtering.

        Returns:
            List of candidate words (lowercase).
        """
        if previous_feedback is None:
            previous_feedback = []
        candidates = self.word_bank.get_words_by_length(length)
        if first_letter is not None:
            candidates = [
                w for w in candidates if w.startswith(first_letter.lower())
            ]
        # Hard‑mode filtering (simplified)
        if hard_mode and previous_feedback:
            # TODO: implement proper hard‑mode filtering
            pass
        return candidates

    @staticmethod
    @lru_cache(maxsize=1024)
    def compute_entropy(guess: str, candidates: Tuple[str, ...]) -> float:
        """Compute information entropy of a guess against a candidate set.

        Args:
            guess: Guessing word.
            candidates: Tuple of candidate answer words (hashable for cache).

        Returns:
            Entropy in bits.
        """
        pattern_counts: Dict[int, int] = {}
        for ans in candidates:
            pattern = feedback_to_pattern(get_feedback_cached(guess, ans))
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        total = len(candidates)
        entropy = 0.0
        for cnt in pattern_counts.values():
            p = cnt / total
            entropy -= p * math.log2(p) if p > 0 else 0.0
        return entropy

    def best_guess(
        self,
        candidates: List[str],
        guess_pool: Optional[List[str]] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Select the best guess from candidates, possibly with randomness.

        Args:
            candidates: Current possible answers.
            guess_pool: Words allowed as guesses (defaults to candidates).
            temperature: Override instance temperature.

        Returns:
            Selected guess word.
        """
        if temperature is None:
            temperature = self.temperature
        if not candidates:
            raise ValueError("No candidates left")
        if len(candidates) == 1:
            return candidates[0]

        # Use cached result if available
        key = tuple(sorted(candidates))
        if key in self.candidate_cache:
            best = self.candidate_cache[key]
        else:
            # Evaluate entropy for each possible guess (guess_pool or candidates)
            pool = guess_pool if guess_pool is not None else candidates
            # If pool is large, sample at most 200 words for performance
            if len(pool) > 200:
                pool = random.sample(pool, 200)
            best_score = -float("inf")
            best = pool[0]
            for g in pool:
                entropy = self.compute_entropy(g, tuple(candidates))
                if entropy > best_score:
                    best_score = entropy
                    best = g
            self.candidate_cache[key] = best

        # Apply temperature‑based randomness
        if temperature > 0.0 and len(candidates) > 1:
            # With probability temperature, pick a random candidate
            if random.random() < temperature:
                return random.choice(candidates)
        return best

    def make_guess(
        self,
        length: int,
        first_letter: Optional[str] = None,
        hard_mode: bool = False,
        previous_feedback: List[Tuple[str, List[int]]] = None,
    ) -> str:
        """Make a guess given the current game state.

        Args:
            length: Word length.
            first_letter: Revealed first letter (if any).
            hard_mode: Whether Hard Mode is active.
            previous_feedback: List of (guess, feedback) for previous guesses.

        Returns:
            Guessed word.
        """
        candidates = self.get_candidates(
            length, first_letter, hard_mode, previous_feedback
        )
        # In practice we would also consider the whole word bank as guess pool.
        # For simplicity we use candidates as guess pool.
        return self.best_guess(candidates, guess_pool=candidates)

    def race_mode_guess_loop(
        self,
        length: int,
        first_letter: Optional[str],
        hard_mode: bool,
        callback,
        stop_event: threading.Event = None,
    ) -> None:
        """Run AI guessing in race mode with delays.

        This function is intended to be run in a separate thread.
        It repeatedly makes guesses, calls callback with each guess,
        and sleeps a random delay between guesses.

        Args:
            length: Word length.
            first_letter: Revealed first letter.
            hard_mode: Hard mode flag.
            callback: Function to call with each guess (signature: guess -> None).
            stop_event: Optional external stop event; if set, loop terminates.
        """
        if stop_event is None:
            stop_event = self._stop_thread
        previous_feedback: List[Tuple[str, List[int]]] = []
        max_attempts = length + 1
        for attempt in range(max_attempts):
            if stop_event.is_set():
                break
            guess = self.make_guess(
                length, first_letter, hard_mode, previous_feedback
            )
            callback(guess)
            # Simulate receiving feedback (in race mode AI doesn't know answer)
            # We cannot compute actual feedback because answer is hidden.
            # Instead, the game controller will provide feedback later.
            # For now we just store dummy feedback (all gray) as placeholder.
            dummy_feedback = [0] * length
            previous_feedback.append((guess, dummy_feedback))
            # Random delay
            delay = random.uniform(self.min_delay, self.max_delay)
            time.sleep(delay)
            if stop_event.is_set():
                break
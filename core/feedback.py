"""
Feedback calculation for Wordle (variable length) and pattern encoding.
"""

from functools import lru_cache
from typing import List, Tuple


def get_feedback(guess: str, answer: str) -> List[int]:
    """
    Compute standard Wordle feedback.

    For each position returns 0 (gray), 1 (yellow), or 2 (green).
    Handles duplicate letters correctly: green matches first, remaining letters used for yellow,
    each answer letter can be matched only once.

    Args:
        guess: Guessed word, must have same length as answer.
        answer: Target word.

    Returns:
        List of length L with values 0,1,2.
    """
    L = len(guess)
    if L != len(answer):
        raise ValueError("Guess and answer must have same length")
    result = [0] * L
    answer_chars = list(answer)
    # First pass: green
    for i in range(L):
        if guess[i] == answer[i]:
            result[i] = 2
            answer_chars[i] = None
    # Second pass: yellow
    for i in range(L):
        if result[i] == 0 and guess[i] in answer_chars:
            result[i] = 1
            answer_chars[answer_chars.index(guess[i])] = None
    return result


@lru_cache(maxsize=32768)
def feedback_to_pattern(feedback: Tuple[int, ...]) -> int:
    """
    Encode feedback tuple (0,1,2) into a single integer.

    Encoding: base‑3 number where each digit is feedback[i].
    This yields a unique integer for each possible feedback pattern.

    Args:
        feedback: Tuple of integers 0,1,2.

    Returns:
        Unique integer identifier.
    """
    pattern = 0
    for f in feedback:
        pattern = pattern * 3 + f
    return pattern


@lru_cache(maxsize=32768)
def get_feedback_cached(guess: str, answer: str) -> Tuple[int, ...]:
    """
    Cached version of get_feedback returning a tuple (hashable).

    Args:
        guess: Guessed word.
        answer: Target word.

    Returns:
        Tuple of feedback values.
    """
    return tuple(get_feedback(guess, answer))


def pattern_to_feedback(pattern: int, length: int) -> List[int]:
    """
    Decode integer pattern back to feedback list.

    Args:
        pattern: Base‑3 encoded pattern.
        length: Word length.

    Returns:
        List of feedback values.
    """
    feedback = []
    for _ in range(length):
        feedback.append(pattern % 3)
        pattern //= 3
    return feedback[::-1]


def is_hard_mode_compliant(
    guess: str, previous_feedback: List[Tuple[str, List[int]]]
) -> bool:
    """
    Check if a guess complies with Hard Mode constraints.

    Hard Mode rules:
    - Green letters must stay in the same position.
    - Yellow letters must appear in the guess at least as many times as
      the number of yellow occurrences revealed so far for that letter.
    - Gray letters (confirmed absent) must not appear (optional but recommended).

    Args:
        guess: Candidate guess.
        previous_feedback: List of (previous_guess, feedback) for all prior guesses.

    Returns:
        True if guess satisfies all constraints.
    """
    # For simplicity, we implement basic checks.
    # In a full implementation you would track constraints per letter.
    # This is a placeholder.
    # TODO: implement proper hard‑mode checking.
    return True


def feedback_to_colors(feedback: List[int]) -> List[str]:
    """
    Map feedback values to color names.

    Returns:
        List of color names "gray", "yellow", "green".
    """
    color_map = {0: "gray", 1: "yellow", 2: "green"}
    return [color_map[f] for f in feedback]

"""
Utility helper functions.
"""

import random
import string
from typing import List, Optional


def random_word(length: int, word_list: List[str]) -> Optional[str]:
    """Pick a random word of given length from word list.

    Args:
        length: Desired length.
        word_list: List of candidate words.

    Returns:
        Random word or None if no word matches.
    """
    candidates = [w for w in word_list if len(w) == length]
    if not candidates:
        return None
    return random.choice(candidates)


def validate_word(word: str, word_set: set) -> bool:
    """Check if word is valid (lowercase, alphabetic, in set).

    Args:
        word: Word to validate.
        word_set: Set of allowed words.

    Returns:
        True if valid.
    """
    return word.isalpha() and word.lower() == word and word in word_set


def color_hex(name: str) -> str:
    """Return hex color for named color.

    Args:
        name: "green", "yellow", "gray".

    Returns:
        Hex string.
    """
    colors = {
        "green": "#6aaa64",
        "yellow": "#c9b458",
        "gray": "#787c7e",
    }
    return colors.get(name, "#ffffff")


def format_time(seconds: float) -> str:
    """Format seconds into MM:SS.

    Args:
        seconds: Time in seconds.

    Returns:
        Formatted string.
    """
    if seconds < 0:
        return "00:00"
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"
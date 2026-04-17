"""
Word bank management: loading word lists, indexing by length and first letter.
"""

import os
import random
from typing import Dict, List, Optional, Set


class WordBank:
    """Word bank for Wordle game.

    Attributes:
        word_sets: Dict[int, List[str]] mapping length to list of words.
        first_letter_index: Dict[int, Dict[str, List[str]]] mapping length then first letter to list.
        word_sets_set: Dict[int, Set[str]] for fast membership test.
    """

    def __init__(self, data_dir: str = "data") -> None:
        """Initialize word bank with data directory.

        Args:
            data_dir: Path to directory containing word list files.
        """
        self.data_dir = data_dir
        self.word_sets: Dict[int, List[str]] = {}
        self.first_letter_index: Dict[int, Dict[str, List[str]]] = {}
        self.word_sets_set: Dict[int, Set[str]] = {}
        self.load_all()

    def load_all(self) -> None:
        """Load all word list files from data directory.

        Expected files: words_gaokao.txt, words_cet4.txt, words_full.txt.
        The active word list is determined by config; by default load all and merge.
        """
        # For simplicity, we load the first found file (or all).
        # In practice, the game will allow switching between banks.
        # We'll implement merging all words from all files.
        all_words: List[str] = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".txt"):
                path = os.path.join(self.data_dir, filename)
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        word = line.strip().lower()
                        if word.isalpha():
                            all_words.append(word)

        self._build_index(all_words)

    def _build_index(self, words: List[str]) -> None:
        """Build length and first‑letter index from a word list.

        Args:
            words: List of lowercase alphabetic words.
        """
        self.word_sets.clear()
        self.first_letter_index.clear()
        self.word_sets_set.clear()

        for word in words:
            L = len(word)
            if L < 1:
                continue
            # Add to length list
            if L not in self.word_sets:
                self.word_sets[L] = []
                self.first_letter_index[L] = {}
                self.word_sets_set[L] = set()
            self.word_sets[L].append(word)
            self.word_sets_set[L].add(word)
            # Index by first letter
            fl = word[0]
            if fl not in self.first_letter_index[L]:
                self.first_letter_index[L][fl] = []
            self.first_letter_index[L][fl].append(word)

    def get_words_by_length(self, length: int) -> List[str]:
        """Return all words of given length.

        Args:
            length: Desired word length.

        Returns:
            List of words (lowercase). Empty list if length not present.
        """
        return self.word_sets.get(length, [])

    def get_words_by_length_and_first_letter(
        self, length: int, first_letter: str
    ) -> List[str]:
        """Return words of given length that start with the specified letter.

        Args:
            length: Word length.
            first_letter: First letter (lowercase).

        Returns:
            List of matching words.
        """
        idx = self.first_letter_index.get(length)
        if idx is None:
            return []
        return idx.get(first_letter, [])

    def contains(self, word: str) -> bool:
        """Check if a word exists in the bank for its length.

        Args:
            word: Word to check (case-insensitive).

        Returns:
            True if word exists.
        """
        L = len(word)
        if L not in self.word_sets_set:
            return False
        return word.lower() in self.word_sets_set[L]

    def random_word(self, length: int, first_letter: Optional[str] = None) -> str:
        """Pick a random word of given length (optionally with first letter).

        Args:
            length: Desired length.
            first_letter: If provided, restrict to words starting with this letter.

        Returns:
            A random word.

        Raises:
            ValueError: If no word matches the criteria.
        """
        candidates: List[str]
        if first_letter is None:
            candidates = self.get_words_by_length(length)
        else:
            candidates = self.get_words_by_length_and_first_letter(
                length, first_letter.lower()
            )
        if not candidates:
            raise ValueError(
                f"No word of length {length} with first letter {first_letter}"
            )
        return random.choice(candidates)

    def get_available_lengths(self) -> List[int]:
        """Return sorted list of lengths present in the bank.

        Returns:
            List of lengths, e.g., [4,5,6,7,8].
        """
        return sorted(self.word_sets.keys())


# Singleton instance
_word_bank: Optional[WordBank] = None


def get_word_bank(data_dir: str = "data") -> WordBank:
    """Get the global word bank instance (singleton).

    Args:
        data_dir: Directory containing word lists.

    Returns:
        WordBank instance.
    """
    global _word_bank
    if _word_bank is None:
        _word_bank = WordBank(data_dir)
    return _word_bank

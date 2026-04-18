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

    def __init__(self, data_dir: str = "data", bank_name: Optional[str] = None) -> None:
        """Initialize word bank with data directory and optional bank name.

        Args:
            data_dir: Path to directory containing word list files.
            bank_name: If provided, load only this specific file (e.g., "words_gaokao.txt").
                If None, load all .txt files in the directory (default).
        """
        self.data_dir = data_dir
        self.bank_name = bank_name
        self.word_sets: Dict[int, List[str]] = {}
        self.first_letter_index: Dict[int, Dict[str, List[str]]] = {}
        self.word_sets_set: Dict[int, Set[str]] = {}
        self.load_all()

    def load_all(self) -> None:
        """Load word list files from data directory according to bank_name.

        If self.bank_name is None, load all .txt files in the directory.
        Otherwise, load only the specified file.
        """
        all_words: List[str] = []
        if self.bank_name is None:
            # Load all .txt files
            for filename in os.listdir(self.data_dir):
                if filename.endswith(".txt"):
                    path = os.path.join(self.data_dir, filename)
                    self._load_file(path, all_words)
        else:
            # Load only the specified bank file
            path = os.path.join(self.data_dir, self.bank_name)
            if os.path.exists(path):
                self._load_file(path, all_words)
            else:
                # Fallback to loading all files if the specified file doesn't exist
                import warnings

                warnings.warn(
                    f"Word bank file {self.bank_name} not found, loading all files."
                )
                for filename in os.listdir(self.data_dir):
                    if filename.endswith(".txt"):
                        path = os.path.join(self.data_dir, filename)
                        self._load_file(path, all_words)

        self._build_index(all_words)

    def _load_file(self, path: str, word_list: List[str]) -> None:
        """Load words from a single file into word_list."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip().lower()
                    if word.isalpha():
                        word_list.append(word)
        except Exception as e:
            import warnings

            warnings.warn(f"Failed to load word bank file {path}: {e}")

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
_current_bank_name: Optional[str] = None


def get_word_bank(data_dir: str = "data", bank_name: Optional[str] = None) -> WordBank:
    """Get the global word bank instance (singleton).

    Args:
        data_dir: Directory containing word lists.
        bank_name: If provided, ensure the word bank is loaded from this specific file.
            If None, use the previously loaded bank (or default to all files).

    Returns:
        WordBank instance.
    """
    global _word_bank, _current_bank_name
    if _word_bank is None or bank_name != _current_bank_name:
        _word_bank = WordBank(data_dir, bank_name)
        _current_bank_name = bank_name
    return _word_bank


def reload_word_bank(bank_name: Optional[str] = None, data_dir: str = "data") -> WordBank:
    """Force‑reload the global word bank with a new bank name.

    Args:
        bank_name: If provided, load only this file; otherwise load all files.
        data_dir: Directory containing word lists.

    Returns:
        Fresh WordBank instance.
    """
    global _word_bank, _current_bank_name
    _word_bank = WordBank(data_dir, bank_name)
    _current_bank_name = bank_name
    return _word_bank

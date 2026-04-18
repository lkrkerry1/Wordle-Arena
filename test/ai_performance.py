#!/usr/bin/env python3
"""
Simulate AI guessing performance over a set of target words.
"""

import sys

sys.path.insert(0, ".")

from core.ai_player import AIPlayer
from core.feedback import get_feedback
import random
import time


def simulate_one_target(ai: AIPlayer, target: str, max_guesses=20) -> int:
    """Return number of guesses taken to guess target."""
    length = len(target)
    previous_feedback = []
    guesses = []
    for attempt in range(max_guesses):
        guess = ai.make_guess(
            length,
            first_letter=None,
            hard_mode=False,
            previous_feedback=previous_feedback,
        )
        guesses.append(guess)
        if guess == target:
            return attempt + 1  # guessed on this attempt
        feedback = get_feedback(guess, target)
        previous_feedback.append((guess, feedback))
    return max_guesses  # failed


def main():
    ai = AIPlayer(temperature=0.0)
    # Get all 5-letter words from word bank
    words = ai.word_bank.get_words_by_length(5)
    print(f"Total 5-letter words: {len(words)}")
    # Sample up to 200 words for speed
    sample_size = min(200, len(words))
    targets = random.sample(words, sample_size)
    print(f"Testing on {sample_size} random targets...")

    start = time.time()
    guess_counts = []
    for i, target in enumerate(targets):
        if i % 20 == 0:
            print(f"  processed {i}/{sample_size}")
        n = simulate_one_target(ai, target)
        guess_counts.append(n)
    elapsed = time.time() - start

    # Statistics
    avg = sum(guess_counts) / len(guess_counts)
    max_guesses = max(guess_counts)
    min_guesses = min(guess_counts)
    # Distribution
    dist = {}
    for cnt in guess_counts:
        dist[cnt] = dist.get(cnt, 0) + 1

    print(f"\nResults (sample size {sample_size}):")
    print(f"Average guesses: {avg:.2f}")
    print(f"Min guesses: {min_guesses}")
    print(f"Max guesses: {max_guesses}")
    print("Distribution:")
    for cnt in sorted(dist.keys()):
        print(f"  {cnt}: {dist[cnt]} ({dist[cnt] / sample_size * 100:.1f}%)")

    # Check if any target not solved within 6 guesses (typical Wordle limit)
    failures = [cnt for cnt in guess_counts if cnt > 6]
    if failures:
        print(f"\nWarning: {len(failures)} targets required more than 6 guesses.")
    else:
        print("\nAll targets solved within 6 guesses.")

    print(f"\nTotal time: {elapsed:.2f}s")


if __name__ == "__main__":
    main()

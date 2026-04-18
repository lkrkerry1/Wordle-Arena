#!/usr/bin/env python3
"""
Quick test to verify AI updates guesses based on feedback.
"""

import sys

sys.path.insert(0, ".")

from core.ai_player import AIPlayer
from core.feedback import get_feedback


def main():
    ai = AIPlayer(temperature=0.0)  # deterministic
    length = 5
    # Get initial candidates
    candidates = ai.get_candidates(length)
    print(f"Initial candidates: {len(candidates)}")
    if len(candidates) < 10:
        print("Warning: too few candidates")

    # Pick a target word (must be in word bank)
    target = "brand"  # ensure it's in bank
    # Verify target is in candidates
    if target not in candidates:
        # find another target
        target = candidates[0]
        print(f"Target not in candidates, using {target}")

    # First guess: use AI's best guess with no feedback
    guess1 = ai.make_guess(length, previous_feedback=[])
    print(f"First guess (no feedback): {guess1}")

    # Compute feedback
    fb1 = get_feedback(guess1, target)
    print(f"Feedback: {fb1}")

    # Second guess: provide previous feedback
    guess2 = ai.make_guess(length, previous_feedback=[(guess1, fb1)])
    print(f"Second guess (with feedback): {guess2}")

    # If feedback is not all gray, candidates should shrink
    candidates2 = ai.get_candidates(length, previous_feedback=[(guess1, fb1)])
    print(f"Candidates after feedback: {len(candidates2)}")

    # Ensure guess2 is different from guess1 (unless forced)
    if guess2 == guess1:
        print("WARNING: AI guessed the same word again!")
        # maybe because candidate set unchanged? check
        if len(candidates2) == len(candidates):
            print("Candidates unchanged, filtering may not work.")
        else:
            print("Candidates changed but AI still picked same word.")
    else:
        print("SUCCESS: AI changed guess based on feedback.")

    # Additional check: if feedback is all gray, guess2 should not contain any gray letters
    # (optional)

    # Test race feedback memory
    ai.race_feedback.clear()
    ai.race_feedback.append((guess1, fb1))
    guess3 = ai.make_guess(length, previous_feedback=ai.race_feedback)
    print(f"Guess using race_feedback: {guess3}")

    # Ensure race_feedback is being used
    if guess3 == guess2:
        print("race_feedback works correctly.")
    else:
        print("race_feedback discrepancy.")


if __name__ == "__main__":
    main()

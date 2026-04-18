#!/usr/bin/env python3
"""
Test that AI ignores first letter on first guess.
"""

import sys

sys.path.insert(0, ".")

from core.ai_player import AIPlayer


def main():
    ai = AIPlayer(temperature=0.0)
    length = 5
    first_letter = "b"  # pretend first letter is revealed
    # First guess with no previous feedback
    guess1 = ai.make_guess(length, first_letter=first_letter, previous_feedback=[])
    print(f"First guess with first_letter='{first_letter}': {guess1}")
    # Check if guess starts with first_letter
    if guess1.startswith(first_letter):
        print("WARNING: AI used first letter hint on first guess (should ignore).")
    else:
        print("SUCCESS: AI ignored first letter hint on first guess.")

    # Second guess with dummy feedback (to simulate after first guess)
    # Provide a dummy feedback (all gray) to indicate that a guess has been made
    dummy_feedback = [0] * length
    guess2 = ai.make_guess(
        length, first_letter=first_letter, previous_feedback=[(guess1, dummy_feedback)]
    )
    print(f"Second guess with first_letter='{first_letter}': {guess2}")
    if guess2.startswith(first_letter):
        print("Second guess uses first letter (as expected).")
    else:
        print(
            "Second guess does not use first letter (maybe candidate set lacks words with that letter)."
        )

    # Additional test: ensure candidate filtering works with first_letter after first guess
    candidates = ai.get_candidates(
        length, first_letter=first_letter, previous_feedback=[(guess1, dummy_feedback)]
    )
    print(
        f"Candidates after first guess with first_letter='{first_letter}': {len(candidates)}"
    )
    if candidates:
        print("Example candidate:", candidates[0])


if __name__ == "__main__":
    main()

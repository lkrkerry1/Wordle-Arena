#!/usr/bin/env python3
"""
Wordle Arena - Main entry point.

A Wordle‑like game with variable word length, five game modes,
AI opponent, and race modes.

Run this script to start the game.
"""

import sys
import os

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    """Launch the GUI application."""
    try:
        from gui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all required modules are present.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
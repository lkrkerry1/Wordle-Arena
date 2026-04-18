#!/usr/bin/env python3
"""
Wordle Arena - Main entry point.

A Wordle‑like game with variable word length, five game modes,
AI opponent, and race modes.

Run this script to start the game.
"""

import os
import sys
import logging
import logging.handlers

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "wordle.log")

# Create handlers
file_handler = logging.FileHandler(log_file, encoding="utf-8")
console_handler = logging.StreamHandler(sys.stderr)

# Set formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Configure root logger
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])


def main() -> None:
    """Launch the GUI application."""
    try:
        from gui.main_window import main as gui_main

        gui_main()
    except ImportError as e:
        logging.error(f"Import error: {e}")
        logging.error("Please ensure all required modules are present.")
        sys.exit(1)
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

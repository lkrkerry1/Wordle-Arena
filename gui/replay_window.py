"""
Replay window showing both players' full guess history after a race game.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Tuple


class ReplayWindow:
    """Modal window displaying complete guess history for both players."""

    def __init__(
        self,
        parent: tk.Widget,
        replay_data: List[Tuple[str, str, List[int]]],
    ) -> None:
        """Initialize replay window.

        Args:
            parent: Parent widget.
            replay_data: List of (player_id, guess, feedback).
        """
        self.parent = parent
        self.replay_data = replay_data
        self.window = tk.Toplevel(parent)
        self.window.title("对局复盘")
        self.window.geometry("900x600")
        self.window.transient(parent)
        self.window.grab_set()

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create UI elements."""
        # Title
        tk.Label(
            self.window,
            text="对局复盘 - 双方完整猜测过程",
            font=("Arial", 18, "bold"),
            pady=10,
        ).pack()

        # Split into two columns
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Determine unique players
        players = set(p for p, _, _ in self.replay_data)
        player_list = sorted(players)
        if len(player_list) != 2:
            # Fallback: player1 left, player2 right
            player_list = ["player1", "player2"]

        # Left column
        left_frame = tk.Frame(main_frame, relief="groove", borderwidth=2)
        left_frame.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(
            left_frame,
            text=player_list[0].upper(),
            font=("Arial", 14, "bold"),
            pady=5,
        ).pack()
        self._create_player_table(left_frame, player_list[0])

        # Right column
        right_frame = tk.Frame(main_frame, relief="groove", borderwidth=2)
        right_frame.pack(side="right", fill="both", expand=True, padx=5)
        tk.Label(
            right_frame,
            text=player_list[1].upper(),
            font=("Arial", 14, "bold"),
            pady=5,
        ).pack()
        self._create_player_table(right_frame, player_list[1])

        # Close button
        tk.Button(
            self.window,
            text="关闭",
            font=("Arial", 12),
            command=self.window.destroy,
            width=15,
        ).pack(pady=20)

    def _create_player_table(self, parent: tk.Widget, player_id: str) -> None:
        """Create a table of guesses for a specific player."""
        # Filter data for this player
        player_data = [(g, f) for p, g, f in self.replay_data if p == player_id]
        if not player_data:
            tk.Label(parent, text="无猜测记录").pack(pady=20)
            return

        # Create canvas with scrollbar
        canvas = tk.Canvas(parent, bg="white")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Header
        header = tk.Frame(scrollable_frame, bg="#e0e0e0")
        header.pack(fill="x", pady=(0, 5))
        tk.Label(header, text="猜测", width=10, anchor="w", bg="#e0e0e0").pack(
            side="left", padx=10
        )
        tk.Label(header, text="反馈", width=20, anchor="w", bg="#e0e0e0").pack(
            side="left", padx=10
        )

        # Each guess
        colors = {0: "#787c7e", 1: "#c9b458", 2: "#6aaa64"}
        for idx, (guess, feedback) in enumerate(player_data):
            row = tk.Frame(scrollable_frame, bg="white")
            row.pack(fill="x", pady=2)

            # Guess number
            tk.Label(row, text=f"{idx + 1}", width=3, anchor="w", bg="white").pack(
                side="left", padx=5
            )
            # Guess word
            tk.Label(
                row,
                text=guess.upper(),
                width=10,
                anchor="w",
                font=("Arial", 12, "bold"),
            ).pack(side="left", padx=5)
            # Feedback squares
            fb_frame = tk.Frame(row, bg="white")
            fb_frame.pack(side="left", padx=5)
            for f in feedback:
                color = colors.get(f, "white")
                square = tk.Label(
                    fb_frame,
                    text="",
                    width=2,
                    height=1,
                    relief="solid",
                    borderwidth=1,
                    bg=color,
                )
                square.pack(side="left", padx=1)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

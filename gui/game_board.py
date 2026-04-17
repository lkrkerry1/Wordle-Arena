"""
Single‑player game board (variable‑length grid, input, virtual keyboard).
"""

import tkinter as tk
from typing import List, Dict

from core.game_state import GameState
from core.game_controller import GameController
from core.feedback import feedback_to_colors


class GameBoard(tk.Frame):
    """Game board for non‑race modes (single, turn‑based)."""

    def __init__(
        self,
        master: tk.Widget,
        game_state: GameState,
        controller: GameController,
    ) -> None:
        """Initialize game board.

        Args:
            master: Parent widget.
            game_state: Current game state.
            controller: Game controller.
        """
        super().__init__(master, bg="#f0f0f0")
        self.game_state = game_state
        self.controller = controller
        self.length = game_state.target_length
        self.max_attempts = game_state.max_attempts
        self.cell_size = 50
        self.padding = 5
        self.colors = {"green": "#6aaa64", "yellow": "#c9b458", "gray": "#787c7e"}

        self._setup_grid()
        self._setup_input()
        self._setup_keyboard()
        self.update_display()

    def _setup_grid(self) -> None:
        """Create the grid of guess cells."""
        grid_frame = tk.Frame(self, bg="#f0f0f0")
        grid_frame.pack(side="top", pady=20)

        # Create cells: rows = max_attempts, cols = length
        self.cells: List[List[tk.Label]] = []
        for r in range(self.max_attempts):
            row_cells = []
            for c in range(self.length):
                cell = tk.Label(
                    grid_frame,
                    width=2,
                    height=1,
                    relief="ridge",
                    borderwidth=2,
                    bg="white",
                    fg="black",
                    font=("Arial", 20, "bold"),
                    text="",
                )
                cell.grid(row=r, column=c, padx=self.padding, pady=self.padding)
                row_cells.append(cell)
            self.cells.append(row_cells)

        # Info label
        self.info_label = tk.Label(
            self,
            text=f"单词长度: {self.length}",
            font=("Arial", 12),
            bg="#f0f0f0",
        )
        self.info_label.pack(pady=5)

    def _setup_input(self) -> None:
        """Setup guess input area."""
        input_frame = tk.Frame(self, bg="#f0f0f0")
        input_frame.pack(side="top", pady=10)

        tk.Label(input_frame, text="输入猜测:", font=("Arial", 12), bg="#f0f0f0").pack(
            side="left", padx=5
        )
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            input_frame,
            textvariable=self.entry_var,
            font=("Arial", 14),
            width=self.length,
            justify="center",
        )
        self.entry.pack(side="left", padx=5)
        self.entry.bind("<Return>", lambda e: self.submit_guess())

        self.submit_btn = tk.Button(
            input_frame,
            text="提交",
            font=("Arial", 12),
            command=self.submit_guess,
            state="normal" if not self.game_state.game_over else "disabled",
        )
        self.submit_btn.pack(side="left", padx=5)

        self.message_label = tk.Label(
            self, text="", font=("Arial", 10), bg="#f0f0f0", fg="red"
        )
        self.message_label.pack(pady=5)

    def _setup_keyboard(self) -> None:
        """Setup virtual keyboard with color hints."""
        keyboard_frame = tk.Frame(self, bg="#f0f0f0")
        keyboard_frame.pack(side="top", pady=20)

        rows = [
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM",
        ]
        self.key_buttons: Dict[str, tk.Button] = {}
        for i, row in enumerate(rows):
            row_frame = tk.Frame(keyboard_frame, bg="#f0f0f0")
            row_frame.pack(pady=2)
            for ch in row:
                btn = tk.Button(
                    row_frame,
                    text=ch,
                    width=3,
                    height=2,
                    font=("Arial", 10, "bold"),
                    command=lambda c=ch: self.on_key_press(c),
                )
                btn.pack(side="left", padx=1)
                self.key_buttons[ch] = btn

        # Backspace and Enter
        control_frame = tk.Frame(keyboard_frame, bg="#f0f0f0")
        control_frame.pack(pady=5)
        tk.Button(
            control_frame,
            text="删除",
            width=6,
            height=2,
            font=("Arial", 10),
            command=self.on_backspace,
        ).pack(side="left", padx=2)
        tk.Button(
            control_frame,
            text="清空",
            width=6,
            height=2,
            font=("Arial", 10),
            command=lambda: self.entry_var.set(""),
        ).pack(side="left", padx=2)
        tk.Button(
            control_frame,
            text="提交",
            width=6,
            height=2,
            font=("Arial", 10),
            command=self.submit_guess,
        ).pack(side="left", padx=2)

    def on_key_press(self, char: str) -> None:
        """Handle virtual keyboard key press."""
        if self.game_state.game_over:
            return
        current = self.entry_var.get()
        if len(current) < self.length:
            self.entry_var.set(current + char.lower())

    def on_backspace(self) -> None:
        """Remove last character."""
        current = self.entry_var.get()
        if current:
            self.entry_var.set(current[:-1])

    def submit_guess(self) -> None:
        """Submit the current guess."""
        if self.game_state.game_over:
            return
        guess = self.entry_var.get().strip().lower()
        if len(guess) != self.length:
            self.message_label.config(text=f"单词长度必须为 {self.length}")
            return
        # TODO: check word existence via word bank
        # For now assume valid
        success = self.controller.submit_guess(self.game_state.current_player, guess)
        if success:
            self.entry_var.set("")
            self.message_label.config(text="")
        else:
            self.message_label.config(text="猜测无效或游戏已结束")

    def update_display(self) -> None:
        """Update grid and keyboard colors based on game state."""
        # Fill grid cells
        for r in range(self.max_attempts):
            for c in range(self.length):
                cell = self.cells[r][c]
                cell.config(text="", bg="white")
        # Place guesses
        for i, guess_entry in enumerate(self.game_state.guesses):
            r = i
            guess = guess_entry.guess.upper()
            feedback = guess_entry.feedback
            colors = feedback_to_colors(feedback)
            for c in range(self.length):
                cell = self.cells[r][c]
                cell.config(text=guess[c] if c < len(guess) else "")
                cell.config(bg=self.colors.get(colors[c], "white"))
                cell.config(fg="white" if colors[c] != "gray" else "black")

        # Update keyboard colors
        # Determine best feedback per letter across all guesses
        letter_status: Dict[str, str] = {}  # "gray", "yellow", "green"
        for guess_entry in self.game_state.guesses:
            guess = guess_entry.guess.upper()
            feedback = guess_entry.feedback
            for idx, ch in enumerate(guess):
                f = feedback[idx]
                if f == 2:
                    letter_status[ch] = "green"
                elif f == 1:
                    if letter_status.get(ch) != "green":
                        letter_status[ch] = "yellow"
                else:
                    if ch not in letter_status:
                        letter_status[ch] = "gray"
        for ch, status in letter_status.items():
            btn = self.key_buttons.get(ch)
            if btn:
                btn.config(bg=self.colors.get(status, "#d3d3d3"))

        # Update input and button state
        if self.game_state.game_over:
            self.submit_btn.config(state="disabled")
            self.entry.config(state="disabled")
            self.message_label.config(text="游戏结束")
        else:
            self.submit_btn.config(state="normal")
            self.entry.config(state="normal")

        # Update info label
        if self.game_state.is_turn_based():
            self.info_label.config(
                text=f"单词长度: {self.length} | 当前回合: {self.game_state.current_player}"
            )
        else:
            self.info_label.config(
                text=f"单词长度: {self.length} | 剩余尝试: {self.game_state.attempts_left}"
            )

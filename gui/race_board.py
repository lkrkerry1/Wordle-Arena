"""
Race‑mode dual board layout with opponent attempt counter.
"""

import tkinter as tk
from typing import Optional

from core.game_state import GameState, GameMode
from core.game_controller import GameController
from core.ai_player import AIPlayer


class RaceBoard(tk.Frame):
    """Race mode board (two sides, opponent attempts hidden)."""

    def __init__(
        self,
        master: tk.Widget,
        game_state: GameState,
        ai_player: Optional[AIPlayer],
        controller: GameController,
    ) -> None:
        """Initialize race board.

        Args:
            master: Parent widget.
            game_state: Current game state.
            ai_player: AI player instance (if any).
            controller: Game controller.
        """
        super().__init__(master, bg="#f0f0f0")
        self.game_state = game_state
        self.ai_player = ai_player
        self.controller = controller
        self.length = game_state.target_length
        self.max_attempts = game_state.max_attempts

        # Determine player sides
        self.player1_id = game_state.player1_id
        self.player2_id = game_state.player2_id

        self._setup_layout()

    def _setup_layout(self) -> None:
        """Setup left‑right split."""
        # Left frame: player 1 (human)
        left_frame = tk.Frame(self, bg="#f0f0f0", relief="groove", borderwidth=2)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            left_frame,
            text="玩家 1",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
        ).pack(pady=5)

        # Player 1's own game board (simplified)
        self.player1_board = self._create_mini_board(left_frame, self.player1_id)
        self.player1_board.pack(pady=10)

        # Right frame: opponent (player 2 or AI)
        right_frame = tk.Frame(self, bg="#f0f0f0", relief="groove", borderwidth=2)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        opponent_name = (
            "AI" if self.game_state.mode == GameMode.VS_AI_RACE else "玩家 2"
        )
        tk.Label(
            right_frame,
            text=opponent_name,
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
        ).pack(pady=5)

        # Opponent attempt counter (big text)
        self.opponent_attempts_label = tk.Label(
            right_frame,
            text="对手已猜 0 次",
            font=("Arial", 24, "bold"),
            fg="#2c3e50",
            bg="#f0f0f0",
        )
        self.opponent_attempts_label.pack(pady=30)

        # Hidden opponent board (not shown)
        self.opponent_hidden_frame = tk.Frame(right_frame, bg="#f0f0f0")
        self.opponent_hidden_frame.pack(pady=10)
        tk.Label(
            self.opponent_hidden_frame,
            text="猜测过程隐藏",
            font=("Arial", 12),
            fg="#7f8c8d",
            bg="#f0f0f0",
        ).pack()

        # Input for player 1 (since player 2 is AI or second human)
        input_frame = tk.Frame(left_frame, bg="#f0f0f0")
        input_frame.pack(pady=20)

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
        )
        self.submit_btn.pack(side="left", padx=5)

        self.message_label = tk.Label(
            left_frame, text="", font=("Arial", 10), bg="#f0f0f0", fg="red"
        )
        self.message_label.pack(pady=5)

        # Virtual keyboard for player 1 (optional, reuse from game_board)
        self._setup_keyboard(left_frame)

        # Status label
        self.status_label = tk.Label(
            self,
            text=f"单词长度: {self.length} | 最大尝试: {self.max_attempts}",
            font=("Arial", 12),
            bg="#f0f0f0",
        )
        self.status_label.pack(side="bottom", pady=10)

    def _create_mini_board(self, parent: tk.Widget, player_id: str) -> tk.Frame:
        """Create a mini board showing player's own guesses."""
        frame = tk.Frame(parent, bg="#f0f0f0")
        # Create a small grid
        cell_size = 30
        cells = []
        for r in range(self.max_attempts):
            row_cells = []
            for c in range(self.length):
                cell = tk.Label(
                    frame,
                    width=2,
                    height=1,
                    relief="ridge",
                    borderwidth=1,
                    bg="white",
                    fg="black",
                    font=("Arial", 12),
                    text="",
                )
                cell.grid(row=r, column=c, padx=1, pady=1)
                row_cells.append(cell)
            cells.append(row_cells)
        self.player_cells = cells
        return frame

    def _setup_keyboard(self, parent: tk.Widget) -> None:
        """Setup virtual keyboard for player 1."""
        keyboard_frame = tk.Frame(parent, bg="#f0f0f0")
        keyboard_frame.pack(pady=10)

        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for row in rows:
            row_frame = tk.Frame(keyboard_frame, bg="#f0f0f0")
            row_frame.pack(pady=1)
            for ch in row:
                btn = tk.Button(
                    row_frame,
                    text=ch,
                    width=2,
                    height=1,
                    font=("Arial", 9),
                    command=lambda c=ch: self.on_key_press(c),
                )
                btn.pack(side="left", padx=1)

        control_frame = tk.Frame(keyboard_frame, bg="#f0f0f0")
        control_frame.pack(pady=5)
        tk.Button(
            control_frame,
            text="删除",
            width=5,
            height=1,
            font=("Arial", 9),
            command=self.on_backspace,
        ).pack(side="left", padx=2)
        tk.Button(
            control_frame,
            text="清空",
            width=5,
            height=1,
            font=("Arial", 9),
            command=lambda: self.entry_var.set(""),
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
        """Submit guess for player 1."""
        if self.game_state.game_over:
            return
        guess = self.entry_var.get().strip().lower()
        if len(guess) != self.length:
            self.message_label.config(text=f"单词长度必须为 {self.length}")
            return
        success = self.controller.submit_guess(self.player1_id, guess)
        if success:
            self.entry_var.set("")
            self.message_label.config(text="")
        else:
            self.message_label.config(text="猜测无效或游戏已结束")

    def update_display(self) -> None:
        """Update both sides."""
        # Update player 1 mini board
        player1_guesses = [
            g for g in self.game_state.guesses if g.player_id == self.player1_id
        ]
        for r in range(self.max_attempts):
            for c in range(self.length):
                cell = self.player_cells[r][c]
                cell.config(text="", bg="white")
        for i, guess_entry in enumerate(player1_guesses):
            r = i
            guess = guess_entry.guess.upper()
            feedback = guess_entry.feedback
            for c in range(self.length):
                cell = self.player_cells[r][c]
                if c < len(guess):
                    cell.config(text=guess[c])
                # Color based on feedback
                color = "#787c7e"  # gray
                if feedback[c] == 2:
                    color = "#6aaa64"  # green
                elif feedback[c] == 1:
                    color = "#c9b458"  # yellow
                cell.config(bg=color, fg="white" if feedback[c] != 0 else "black")

        # Update opponent attempt counter
        opponent_guesses = [
            g for g in self.game_state.guesses if g.player_id == self.player2_id
        ]
        self.opponent_attempts_label.config(text=f"对手已猜 {len(opponent_guesses)} 次")

        # Update game status
        if self.game_state.game_over:
            self.submit_btn.config(state="disabled")
            self.entry.config(state="disabled")
            self.message_label.config(text="游戏结束")
            winner = self.game_state.winner
            if winner:
                self.status_label.config(text=f"游戏结束！胜者: {winner}")
            else:
                self.status_label.config(text="游戏结束！平局")
        else:
            self.submit_btn.config(state="normal")
            self.entry.config(state="normal")
            self.status_label.config(
                text=f"单词长度: {self.length} | 玩家1已猜: {len(player1_guesses)}"
            )

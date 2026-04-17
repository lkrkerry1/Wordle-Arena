"""
Dialogs for settings, results, etc.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from typing import Optional, Dict, Any


class SettingsDialog:
    """Settings dialog window."""

    def __init__(self, parent: tk.Widget, current_config: Dict[str, Any]) -> None:
        """Initialize dialog with current config.

        Args:
            parent: Parent widget.
            current_config: Current configuration dictionary.
        """
        self.parent = parent
        self.config = current_config.copy()
        self.result: Optional[Dict[str, Any]] = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("游戏设置")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Word bank selection
        tk.Label(main_frame, text="词库:", font=("Arial", 12)).grid(
            row=0, column=0, sticky="w", pady=10
        )
        self.bank_var = tk.StringVar(value=self.config.get("word_bank", "words_full.txt"))
        bank_combo = ttk.Combobox(
            main_frame,
            textvariable=self.bank_var,
            values=["words_gaokao.txt", "words_cet4.txt", "words_full.txt"],
            state="readonly",
            width=25,
        )
        bank_combo.grid(row=0, column=1, sticky="w", pady=10)

        # Word length selection
        tk.Label(main_frame, text="单词长度:", font=("Arial", 12)).grid(
            row=1, column=0, sticky="w", pady=10
        )
        self.length_var = tk.StringVar(value=self.config.get("word_length", "random"))
        length_combo = ttk.Combobox(
            main_frame,
            textvariable=self.length_var,
            values=["random", "4", "5", "6", "7", "8"],
            state="readonly",
            width=25,
        )
        length_combo.grid(row=1, column=1, sticky="w", pady=10)

        # Hard mode
        tk.Label(main_frame, text="难度模式:", font=("Arial", 12)).grid(
            row=2, column=0, sticky="w", pady=10
        )
        self.hard_var = tk.BooleanVar(value=self.config.get("hard_mode", False))
        hard_frame = tk.Frame(main_frame)
        hard_frame.grid(row=2, column=1, sticky="w", pady=10)
        tk.Radiobutton(
            hard_frame,
            text="普通",
            variable=self.hard_var,
            value=False,
        ).pack(side="left", padx=5)
        tk.Radiobutton(
            hard_frame,
            text="困难",
            variable=self.hard_var,
            value=True,
        ).pack(side="left", padx=5)

        # AI temperature
        tk.Label(main_frame, text="AI 随机性 (0=确定, 1=随机):", font=("Arial", 12)).grid(
            row=3, column=0, sticky="w", pady=10
        )
        self.temp_var = tk.DoubleVar(value=self.config.get("ai_temperature", 0.0))
        temp_scale = tk.Scale(
            main_frame,
            variable=self.temp_var,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient="horizontal",
            length=200,
        )
        temp_scale.grid(row=3, column=1, sticky="w", pady=10)

        # AI delay range
        tk.Label(main_frame, text="AI 思考延迟 (秒):", font=("Arial", 12)).grid(
            row=4, column=0, sticky="w", pady=10
        )
        delay_frame = tk.Frame(main_frame)
        delay_frame.grid(row=4, column=1, sticky="w", pady=10)
        tk.Label(delay_frame, text="最小:").pack(side="left")
        self.min_delay_var = tk.DoubleVar(value=self.config.get("ai_min_delay", 0.5))
        tk.Spinbox(
            delay_frame,
            from_=0.1,
            to=5.0,
            increment=0.1,
            textvariable=self.min_delay_var,
            width=5,
        ).pack(side="left", padx=5)
        tk.Label(delay_frame, text="最大:").pack(side="left", padx=(10, 0))
        self.max_delay_var = tk.DoubleVar(value=self.config.get("ai_max_delay", 2.0))
        tk.Spinbox(
            delay_frame,
            from_=0.1,
            to=10.0,
            increment=0.1,
            textvariable=self.max_delay_var,
            width=5,
        ).pack(side="left", padx=5)

        # Time limit per turn
        tk.Label(main_frame, text="每步限时 (秒, 0=不限):", font=("Arial", 12)).grid(
            row=5, column=0, sticky="w", pady=10
        )
        self.time_limit_var = tk.IntVar(value=self.config.get("time_limit", 60))
        tk.Spinbox(
            main_frame,
            from_=0,
            to=300,
            increment=5,
            textvariable=self.time_limit_var,
            width=10,
        ).grid(row=5, column=1, sticky="w", pady=10)

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=30)

        tk.Button(
            button_frame,
            text="确定",
            font=("Arial", 12),
            width=10,
            command=self.on_ok,
        ).pack(side="left", padx=20)
        tk.Button(
            button_frame,
            text="取消",
            font=("Arial", 12),
            width=10,
            command=self.on_cancel,
        ).pack(side="left", padx=20)

    def on_ok(self) -> None:
        """OK button handler."""
        # Validate
        min_delay = self.min_delay_var.get()
        max_delay = self.max_delay_var.get()
        if min_delay > max_delay:
            messagebox.showerror("错误", "最小延迟不能大于最大延迟")
            return
        self.result = {
            "word_bank": self.bank_var.get(),
            "word_length": self.length_var.get(),
            "hard_mode": self.hard_var.get(),
            "ai_temperature": self.temp_var.get(),
            "ai_min_delay": min_delay,
            "ai_max_delay": max_delay,
            "time_limit": self.time_limit_var.get(),
        }
        self.dialog.destroy()

    def on_cancel(self) -> None:
        """Cancel button handler."""
        self.result = None
        self.dialog.destroy()


class ResultDialog:
    """Simple result message dialog."""

    @staticmethod
    def show(parent: tk.Widget, title: str, message: str) -> None:
        """Show a result dialog.

        Args:
            parent: Parent widget.
            title: Dialog title.
            message: Message text.
        """
        messagebox.showinfo(title, message)

    @staticmethod
    def ask_new_game(parent: tk.Widget) -> bool:
        """Ask whether to start a new game.

        Args:
            parent: Parent widget.

        Returns:
            True if user chooses "是".
        """
        return messagebox.askyesno("新游戏", "是否开始新游戏？")
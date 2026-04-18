"""
Main window and menu for Wordle Arena.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional
import json
import os
import logging

from core.game_state import GameMode, GameState, PlayerType
from core.game_controller import GameController, create_game_state
from core.word_bank import get_word_bank
from core.ai_player import AIPlayer
from .dialogs import SettingsDialog
from .game_board import GameBoard
from .race_board import RaceBoard
from .replay_window import ReplayWindow


class MainWindow:
    """Main application window."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize main window.

        Args:
            root: Tkinter root window.
        """
        self.root = root
        self.root.title("Wordle Arena")
        self.root.geometry("1100x750")
        self.root.minsize(800, 600)
        self.root.configure(bg="#f0f0f0")

        # Load config
        self.config = self._load_config()
        # Initialize word bank with configured bank name
        self.word_bank = get_word_bank(bank_name=self.config.get("word_bank"))
        # Initialize AI player with config
        self.ai_player = AIPlayer(
            temperature=self.config.get("ai_temperature", 0.0),
            min_delay=self.config.get("ai_min_delay", 0.5),
            max_delay=self.config.get("ai_max_delay", 2.0),
        )
        # Ensure AI player uses the same word bank instance
        self.ai_player.word_bank = self.word_bank
        # Current game state and controller
        self.game_state: Optional[GameState] = None
        self.controller: Optional[GameController] = None
        # UI components
        self.menubar: Optional[tk.Menu] = None
        self.status_bar: Optional[tk.Label] = None
        self.game_frame: Optional[tk.Frame] = None
        self.current_board: Optional[GameBoard] = None
        self.race_board: Optional[RaceBoard] = None

        self._setup_menus()
        self._setup_ui()
        self._update_status()

    def _load_config(self) -> dict:
        """Load configuration from config.json, create default if missing."""
        config_path = "config.json"
        default_config = {
            "word_bank": "words_full.txt",
            "word_length": "random",
            "hard_mode": False,
            "ai_temperature": 0.0,
            "ai_min_delay": 0.5,
            "ai_max_delay": 2.0,
            "time_limit": 60,
        }
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for k, v in default_config.items():
                        if k not in loaded:
                            loaded[k] = v
                    return loaded
            except Exception:
                return default_config
        return default_config

    def _save_config(self) -> None:
        """Save current configuration to config.json."""
        logging.debug(f"Saving config: {self.config}")
        config_path = "config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)
        logging.debug("Config saved")

    def _setup_menus(self) -> None:
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="游戏", menu=game_menu)
        game_menu.add_command(
            label="单人练习", command=lambda: self.start_game(GameMode.SINGLE)
        )
        game_menu.add_separator()
        game_menu.add_command(
            label="人机回合对战", command=lambda: self.start_game(GameMode.VS_AI_TURN)
        )
        game_menu.add_command(
            label="人机竞速对战", command=lambda: self.start_game(GameMode.VS_AI_RACE)
        )
        game_menu.add_separator()
        game_menu.add_command(
            label="双人回合对战",
            command=lambda: self.start_game(GameMode.VS_HUMAN_TURN),
        )
        game_menu.add_command(
            label="双人竞速对战",
            command=lambda: self.start_game(GameMode.VS_HUMAN_RACE),
        )
        game_menu.add_separator()
        game_menu.add_command(label="回到主页", command=self.show_home)
        game_menu.add_separator()
        game_menu.add_command(label="退出", command=self.root.quit)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="游戏设置", command=self.open_settings)
        settings_menu.add_command(label="重置配置", command=self.reset_config)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="规则说明", command=self.show_rules)
        help_menu.add_command(label="关于", command=self.show_about)

    def _setup_ui(self) -> None:
        """Setup main UI frames."""
        # Top status bar
        self.status_bar = tk.Label(
            self.root,
            text="就绪",
            bg="#e0e0e0",
            fg="#333",
            font=("Arial", 10),
            anchor="w",
            relief="sunken",
            bd=1,
        )
        self.status_bar.pack(side="top", fill="x", padx=5, pady=2)

        # Central game area
        self.game_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.game_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Welcome label
        welcome = tk.Label(
            self.game_frame,
            text="Wordle Arena",
            font=("Arial", 24, "bold"),
            fg="#2c3e50",
            bg="#f0f0f0",
        )
        welcome.pack(pady=50)

        subtitle = tk.Label(
            self.game_frame,
            text="请从菜单选择游戏模式开始",
            font=("Arial", 14),
            fg="#7f8c8d",
            bg="#f0f0f0",
        )
        subtitle.pack(pady=10)

        # Mode buttons (optional)
        button_frame = tk.Frame(self.game_frame, bg="#f0f0f0")
        button_frame.pack(pady=20)
        modes = [
            ("单人练习", GameMode.SINGLE),
            ("人机回合", GameMode.VS_AI_TURN),
            ("人机竞速", GameMode.VS_AI_RACE),
            ("双人回合", GameMode.VS_HUMAN_TURN),
            ("双人竞速", GameMode.VS_HUMAN_RACE),
        ]
        for text, mode in modes:
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Arial", 11),
                width=15,
                command=lambda m=mode: self.start_game(m),
            )
            btn.pack(side="left", padx=5, pady=5)

    def _update_status(self, text: Optional[str] = None) -> None:
        """Update status bar text."""
        if self.status_bar is None:
            return
        if text is None:
            # Build status string from config
            length = self.config.get("word_length", "random")
            bank = self.config.get("word_bank", "words_full.txt")
            hard = "困难" if self.config.get("hard_mode") else "普通"
            time_limit = self.config.get("time_limit", 60)
            text = f"词库: {bank} | 长度: {length} | 难度: {hard} | 限时: {time_limit}s"
        self.status_bar.config(text=text)
        self.status_bar.update_idletasks()

    def open_settings(self) -> None:
        """Open settings dialog."""
        logging.debug("open_settings called")
        try:
            dialog = SettingsDialog(self.root, self.config)
            logging.debug("SettingsDialog created")
        except Exception as e:
            logging.error(f"Failed to create SettingsDialog: {e}")
            return
        # Wait for dialog to close
        dialog.dialog.wait_window()
        logging.debug("dialog closed")
        if dialog.result:
            # Debug log
            logging.debug(f"dialog.result = {dialog.result}")
            # Remember old word bank to detect changes
            old_bank = self.config.get("word_bank")
            # Update config
            for k, v in dialog.result.items():
                self.config[k] = v
            logging.debug(f"config after update = {self.config}")
            self._save_config()
            logging.debug("config saved")
            self._update_status()
            # Update AI player parameters
            self.ai_player.temperature = self.config.get("ai_temperature", 0.0)
            self.ai_player.min_delay = self.config.get("ai_min_delay", 0.5)
            self.ai_player.max_delay = self.config.get("ai_max_delay", 2.0)
            # Reload word bank if bank changed
            new_bank = self.config.get("word_bank")
            if new_bank != old_bank:
                self.word_bank = get_word_bank(bank_name=new_bank)
                self.ai_player.word_bank = self.word_bank
            # Auto‑restart current game if one is active
            if self.game_state is not None:
                current_mode = self.game_state.mode
                self.start_game(current_mode)
        else:
            logging.debug("dialog.result is None (cancelled or closed)")

    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        self.config = self._load_config()  # reload defaults
        self._save_config()
        logging.debug(f"config after save = {self.config}")
        self._update_status()
        # Reload word bank to reflect default bank
        self.word_bank = get_word_bank(bank_name=self.config.get("word_bank"))
        self.ai_player.word_bank = self.word_bank
        # Update AI player parameters
        self.ai_player.temperature = self.config.get("ai_temperature", 0.0)
        self.ai_player.min_delay = self.config.get("ai_min_delay", 0.5)
        self.ai_player.max_delay = self.config.get("ai_max_delay", 2.0)
        # Auto‑restart current game if one is active
        if self.game_state is not None:
            current_mode = self.game_state.mode
            self.start_game(current_mode)
        messagebox.showinfo("重置", "配置已恢复默认值")

    def show_rules(self) -> None:
        """Show game rules."""
        rules = """
Wordle Arena 规则

- 目标：猜出隐藏的单词。
- 每次猜测必须是合法单词，长度与目标相同。
- 反馈颜色：
  绿色：字母正确且位置正确。
  黄色：字母正确但位置错误。
  灰色：字母不在单词中。
- 最大猜测次数 = 单词长度 + 1。
- 困难模式：后续猜测必须遵守已揭示的线索。

游戏模式：
1. 单人练习：独自猜词。
2. 人机回合：与 AI 轮流猜测同一个单词。
3. 人机竞速：与 AI 同时猜测，互不可见。
4. 双人回合：两名玩家轮流猜测。
5. 双人竞速：两名玩家同时猜测。
        """
        messagebox.showinfo("游戏规则", rules)

    def show_about(self) -> None:
        """Show about dialog."""
        about = """
Wordle Arena
版本 1.0

基于 Python 和 Tkinter 开发。
支持单词长度 4‑8 字母。
提供五种对战模式，含 AI 对手。

作者：lkrkerry
        """
        messagebox.showinfo("关于", about)

    def start_game(self, mode: GameMode) -> None:
        """Start a new game with selected mode."""
        # Stop any ongoing game
        if self.controller:
            self.controller.stop()
        # Clear game frame
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        # Determine word length
        length_setting = self.config.get("word_length", "random")
        if length_setting == "random":
            import random

            available = self.word_bank.get_available_lengths()
            length = random.choice(available) if available else 5
        else:
            length = int(length_setting)
        # Debug log
        logging.debug(
            f"start_game: length_setting={length_setting}, chosen length={length}"
        )

        # Choose target word
        first_letter = None
        if mode == GameMode.SINGLE or mode == GameMode.VS_AI_TURN:
            # Reveal first letter in single and vs AI turn modes
            first_letter = "a"  # placeholder, should be random
        try:
            target = self.word_bank.random_word(length, first_letter)
        except ValueError:
            # Fallback to any word of that length
            candidates = self.word_bank.get_words_by_length(length)
            if not candidates:
                messagebox.showerror("错误", f"词库中没有长度为 {length} 的单词")
                return
            import random

            target = random.choice(candidates)

        # Create game state
        hard_mode = self.config.get("hard_mode", False)
        time_limit = self.config.get("time_limit", 60)
        player2_type = PlayerType.AI if "AI" in mode.name else PlayerType.HUMAN
        self.game_state = create_game_state(
            mode=mode,
            target_word=target,
            hard_mode=hard_mode,
            time_limit=time_limit,
            player2_type=player2_type,
        )

        # Create controller
        self.controller = GameController(
            game_state=self.game_state,
            ai_player=self.ai_player if player2_type == PlayerType.AI else None,
            on_state_change=self._on_state_change,
            on_timer_update=self._on_timer_update,
            on_game_over=self._on_game_over,
        )

        # Create appropriate board
        if mode.is_race():
            self.race_board = RaceBoard(
                self.game_frame,
                self.game_state,
                self.ai_player,
                self.controller,
                on_restart=lambda: self.start_game(mode),
            )
            self.race_board.pack(fill="both", expand=True)
            self.current_board = None
        else:
            self.current_board = GameBoard(
                self.game_frame,
                self.game_state,
                self.controller,
                on_restart=lambda: self.start_game(mode),
            )
            self.current_board.pack(fill="both", expand=True)
            self.race_board = None

        # Start game
        self.controller.start()
        self._update_status(f"游戏开始 - {mode.value} - 单词长度: {length}")

    def _on_state_change(self) -> None:
        """Callback when game state changes."""
        if self.current_board:
            self.current_board.update_display()
        if self.race_board:
            self.race_board.update_display()
        # Update status bar with turn info
        if self.game_state and self.game_state.is_turn_based():
            player = self.game_state.current_player
            self.status_bar.config(text=f"当前回合: {player}")

    def _on_timer_update(self, remaining: float) -> None:
        """Callback for timer updates."""
        if self.game_state and self.game_state.is_turn_based():
            self.status_bar.config(text=f"剩余时间: {remaining:.0f} 秒")

    def _on_game_over(self) -> None:
        """Callback when game ends."""
        winner = self.game_state.winner if self.game_state else None
        if winner:
            messagebox.showinfo("游戏结束", f"{winner} 获胜！")
        else:
            messagebox.showinfo("游戏结束", "平局！")
        # Show replay window for race modes
        if self.game_state and self.game_state.is_race():
            ReplayWindow(self.root, self.controller.get_replay_data())

    def show_home(self) -> None:
        """Return to home screen (clear game and show welcome)."""
        # Stop any ongoing game
        if self.controller:
            self.controller.stop()
            self.controller = None
        # Clear game frame
        if self.game_frame:
            for widget in self.game_frame.winfo_children():
                widget.destroy()
            # Recreate welcome screen
            welcome = tk.Label(
                self.game_frame,
                text="Wordle Arena",
                font=("Arial", 24, "bold"),
                fg="#2c3e50",
                bg="#f0f0f0",
            )
            welcome.pack(pady=50)
            subtitle = tk.Label(
                self.game_frame,
                text="请从菜单选择游戏模式开始",
                font=("Arial", 14),
                fg="#7f8c8d",
                bg="#f0f0f0",
            )
            subtitle.pack(pady=10)
            # Mode buttons (optional)
            button_frame = tk.Frame(self.game_frame, bg="#f0f0f0")
            button_frame.pack(pady=20)
            modes = [
                ("单人练习", GameMode.SINGLE),
                ("人机回合", GameMode.VS_AI_TURN),
                ("人机竞速", GameMode.VS_AI_RACE),
                ("双人回合", GameMode.VS_HUMAN_TURN),
                ("双人竞速", GameMode.VS_HUMAN_RACE),
            ]
            for text, mode in modes:
                btn = tk.Button(
                    button_frame,
                    text=text,
                    font=("Arial", 11),
                    width=15,
                    command=lambda m=mode: self.start_game(m),
                )
                btn.pack(side="left", padx=5, pady=5)
        # Reset game state
        self.game_state = None
        self.current_board = None
        self.race_board = None
        # Update status bar to show config
        self._update_status()


def main() -> None:
    """Entry point for the GUI application."""
    root = tk.Tk()
    app = MainWindow(root)
    root.protocol(
        "WM_DELETE_WINDOW",
        lambda: (app.controller.stop() if app.controller else None, root.quit()),
    )
    root.mainloop()


if __name__ == "__main__":
    main()

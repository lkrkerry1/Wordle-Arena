#!/usr/bin/env python3
"""
Wordle Arena - 服务端版本
在本地运行一个网页游戏服务器。
"""

import os
import sys
import json
import random
import uuid
import threading
import time
from typing import Dict, Optional, Any, List

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_from_directory
from core.game_state import GameState, GameMode, PlayerType
from core.game_controller import GameController
from core.ai_player import AIPlayer
from core.word_bank import WordBank
from core.feedback import get_feedback

# 初始化 Flask 应用
app = Flask(__name__, static_folder=None)

# 全局单词库（使用配置文件）
CONFIG_FILE = "config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    config = {}

WORD_BANK_NAME = config.get("word_bank", "words_gaokao.txt")
WORD_LENGTH = int(config.get("word_length", 5))
HARD_MODE = config.get("hard_mode", False)
AI_TEMPERATURE = config.get("ai_temperature", 0.6)
AI_MIN_DELAY = config.get("ai_min_delay", 2.0)
AI_MAX_DELAY = config.get("ai_max_delay", 4.0)


def get_word_bank_list() -> List[str]:
    """返回 data 目录下所有词库文件名（仅 .txt 文件）"""
    import os

    if not os.path.exists("data"):
        return []
    files = []
    for f in os.listdir("data"):
        if f.endswith(".txt") and os.path.isfile(os.path.join("data", f)):
            files.append(f)
    return files


# 初始化单词库
word_bank = WordBank(data_dir="data", bank_name=WORD_BANK_NAME)
# 全局完整词库，用于单词验证
full_word_bank = WordBank(data_dir="data", bank_name="words_full.txt")

# 游戏会话存储
sessions: Dict[str, Dict[str, Any]] = {}
session_lock = threading.Lock()


# 辅助函数
def create_game_session(
    mode: GameMode,
    length: int,
    first_letter: Optional[str] = None,
    hard_mode: bool = False,
    word_bank_name: Optional[str] = None,
    ai_temperature: float = AI_TEMPERATURE,
    ai_min_delay: float = AI_MIN_DELAY,
    ai_max_delay: float = AI_MAX_DELAY,
) -> str:
    """创建一个新游戏会话，返回 session_id"""
    # 使用指定词库创建单词库实例
    bank_name = word_bank_name or WORD_BANK_NAME
    game_word_bank = WordBank(data_dir="data", bank_name=bank_name)

    # 随机选择目标单词
    candidates = game_word_bank.get_words_by_length(length)
    if first_letter:
        candidates = [w for w in candidates if w.startswith(first_letter.lower())]
    if not candidates:
        raise ValueError(f"No word of length {length} with first letter {first_letter}")
    target_word = random.choice(candidates)

    # 根据模式决定最大尝试次数
    if mode.is_turn_based():
        max_attempts = 9999  # 轮流模式下无限制
    else:
        max_attempts = length + 1

    # 创建游戏状态
    game_state = GameState(
        mode=mode,
        target_word=target_word,
        target_length=length,
        first_letter=target_word[0],
        max_attempts=max_attempts,
        hard_mode=hard_mode,
        time_limit=0.0,  # 暂无时间限制
    )

    # 根据模式设置玩家类型
    if mode == GameMode.VS_AI_TURN:
        game_state.player_types["player2"] = PlayerType.AI
        ai_player = AIPlayer(
            temperature=ai_temperature,
            min_delay=ai_min_delay,
            max_delay=ai_max_delay,
        )
        ai_player.word_bank = game_word_bank
    else:
        ai_player = None

    # 创建游戏控制器
    controller = GameController(
        game_state=game_state,
        ai_player=ai_player,
        on_state_change=lambda: None,
        on_timer_update=lambda _: None,
        on_game_over=lambda: None,
    )
    controller.start()

    session_id = str(uuid.uuid4())
    with session_lock:
        sessions[session_id] = {
            "game_state": game_state,
            "controller": controller,
            "ai_player": ai_player,
            "word_bank": game_word_bank,  # 保存引用，避免被垃圾回收
            "created_at": time.time(),
        }
    return session_id


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """根据 session_id 获取会话，不存在则返回 None"""
    with session_lock:
        return sessions.get(session_id)


# 路由
@app.route("/")
def index():
    """提供前端页面"""
    return send_from_directory(".", "index.html")


@app.route("/api/game", methods=["POST"])
def create_game():
    """创建新游戏"""
    try:
        data = request.get_json()
        mode_str = data.get("mode", "single")
        length = int(data.get("length", WORD_LENGTH))
        first_letter = data.get("first_letter")
        hard_mode = bool(data.get("hard_mode", HARD_MODE))
        word_bank_name = data.get("word_bank")  # 可选，默认使用配置中的词库
        ai_temperature = float(data.get("ai_temperature", AI_TEMPERATURE))
        ai_min_delay = float(data.get("ai_min_delay", AI_MIN_DELAY))
        ai_max_delay = float(data.get("ai_max_delay", AI_MAX_DELAY))

        # 映射模式字符串到 GameMode
        mode_map = {
            "single": GameMode.SINGLE,
            "vs_ai_turn": GameMode.VS_AI_TURN,
            "vs_ai_race": GameMode.VS_AI_RACE,
            "vs_human_turn": GameMode.VS_HUMAN_TURN,
            "vs_human_race": GameMode.VS_HUMAN_RACE,
        }
        mode = mode_map.get(mode_str)
        if mode is None:
            return jsonify({"error": "Invalid game mode"}), 400

        session_id = create_game_session(
            mode=mode,
            length=length,
            first_letter=first_letter,
            hard_mode=hard_mode,
            word_bank_name=word_bank_name,
            ai_temperature=ai_temperature,
            ai_min_delay=ai_min_delay,
            ai_max_delay=ai_max_delay,
        )
        return jsonify({"session_id": session_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/game/<session_id>", methods=["GET"])
def get_game_state(session_id: str):
    """获取游戏状态"""
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Game session not found"}), 404

    game_state = session["game_state"]
    # 构建响应
    response = {
        "mode": game_state.mode.value,
        "target_length": game_state.target_length,
        "first_letter": game_state.first_letter,
        "max_attempts": game_state.max_attempts,
        "hard_mode": game_state.hard_mode,
        "guesses": [
            {
                "player_id": g.player_id,
                "guess": g.guess,
                "feedback": g.feedback,
                "timestamp": g.timestamp,
            }
            for g in game_state.guesses
        ],
        "current_player": game_state.current_player,
        "game_over": game_state.game_over,
        "winner": game_state.winner,
        "attempts_used": len(game_state.guesses),
        "attempts_left": game_state.max_attempts - len(game_state.guesses),
    }
    if game_state.game_over:
        response["target_word"] = game_state.target_word
    return jsonify(response), 200


@app.route("/api/game/<session_id>/guess", methods=["POST"])
def submit_guess(session_id: str):
    """提交猜测"""
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Game session not found"}), 404

    game_state = session["game_state"]
    controller = session["controller"]

    if game_state.game_over:
        return jsonify({"error": "Game is already over"}), 400

    data = request.get_json()
    guess = data.get("guess", "").strip().lower()
    if not guess.isalpha():
        return jsonify({"error": "Guess must be alphabetic"}), 400

    # 检查单词长度
    if len(guess) != game_state.target_length:
        return jsonify(
            {"error": f"Guess must be {game_state.target_length} letters long"}
        ), 400

    # 使用全局完整词库进行单词验证（无论玩家选择哪个词库）
    if guess not in full_word_bank.word_sets_set.get(game_state.target_length, set()):
        return jsonify({"error": "Word not in dictionary"}), 400

    # 检查是否已经猜测过该单词（任何玩家）
    if any(g.guess == guess for g in game_state.guesses):
        return jsonify({"error": "Word already guessed"}), 400

    # 计算反馈
    feedback = get_feedback(guess, game_state.target_word)

    # 添加到猜测记录
    from core.game_state import GuessEntry

    guess_entry = GuessEntry(
        player_id=game_state.current_player, guess=guess, feedback=feedback
    )
    game_state.guesses.append(guess_entry)

    # 检查游戏是否结束
    if guess == game_state.target_word:
        game_state.game_over = True
        game_state.winner = game_state.current_player
        controller.stop()
    elif len(game_state.guesses) >= game_state.max_attempts:
        game_state.game_over = True
        game_state.winner = None
        controller.stop()
    else:
        # 切换玩家（如果是双人模式）
        if game_state.mode.is_turn_based() and not game_state.mode.is_single():
            # 简单切换
            game_state.current_player = (
                "player2" if game_state.current_player == "player1" else "player1"
            )

    # 触发状态变更回调（暂无）

    response = {
        "feedback": feedback,
        "game_over": game_state.game_over,
        "winner": game_state.winner,
        "current_player": game_state.current_player,
    }
    if game_state.game_over:
        response["target_word"] = game_state.target_word
    return jsonify(response), 200


@app.route("/api/game/<session_id>/ai_turn", methods=["POST"])
def ai_turn(session_id: str):
    """请求AI进行猜测（用于VS_AI_TURN模式）"""
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Game session not found"}), 404

    game_state = session["game_state"]
    ai_player = session["ai_player"]

    if game_state.game_over:
        return jsonify({"error": "Game is already over"}), 400

    if game_state.mode != GameMode.VS_AI_TURN:
        return jsonify({"error": "AI turn only available in VS_AI_TURN mode"}), 400

    if game_state.current_player != "player2":  # AI应该是player2
        return jsonify({"error": "Not AI's turn"}), 400

    # 获取AI的猜测
    # 这里简化：直接使用AI玩家的get_best_guess方法（需要实现）
    # 暂时随机选择一个候选单词
    candidates = ai_player.get_candidates(
        length=game_state.target_length,
        first_letter=game_state.first_letter if game_state.hard_mode else None,
        hard_mode=game_state.hard_mode,
        previous_feedback=[(g.guess, g.feedback) for g in game_state.guesses],
    )
    # 排除已经猜测过的单词
    guessed_words = {g.guess for g in game_state.guesses}
    candidates = [c for c in candidates if c not in guessed_words]
    if not candidates:
        guess = "?" * game_state.target_length
    else:
        guess = random.choice(candidates)

    # 提交猜测
    data = {"guess": guess}
    # 重用submit_guess逻辑
    # 简化：直接调用内部函数
    feedback = get_feedback(guess, game_state.target_word)
    from core.game_state import GuessEntry

    guess_entry = GuessEntry(player_id="player2", guess=guess, feedback=feedback)
    game_state.guesses.append(guess_entry)

    if guess == game_state.target_word:
        game_state.game_over = True
        game_state.winner = "player2"
        session["controller"].stop()
    elif len(game_state.guesses) >= game_state.max_attempts:
        game_state.game_over = True
        game_state.winner = None
        session["controller"].stop()
    else:
        game_state.current_player = "player1"

    response = {
        "guess": guess,
        "feedback": feedback,
        "game_over": game_state.game_over,
        "winner": game_state.winner,
        "current_player": game_state.current_player,
    }
    if game_state.game_over:
        response["target_word"] = game_state.target_word
    return jsonify(response), 200


@app.route("/api/wordbanks", methods=["GET"])
def list_word_banks():
    """返回可用的词库列表"""
    banks = get_word_bank_list()
    return jsonify(banks), 200


if __name__ == "__main__":
    import time

    print("Starting Wordle Arena server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(host="0.0.0.0", port=5000, debug=True)

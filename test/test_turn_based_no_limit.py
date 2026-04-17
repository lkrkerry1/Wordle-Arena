#!/usr/bin/env python3
"""测试轮流模式（turn-based）无尝试次数限制"""

import sys

sys.path.insert(0, ".")

from core.game_controller import create_game_state
from core.game_state import GameMode


def test_turn_based_no_limit():
    # 创建一个 turn-based 模式的状态 (VS_AI_TURN)
    target_word = "apple"
    mode = GameMode.VS_AI_TURN
    state = create_game_state(mode=mode, target_word=target_word)
    print(f"初始 max_attempts: {state.max_attempts}")
    print(f"模式是 turn-based: {state.mode.is_turn_based()}")
    print(f"模式是 race: {state.mode.is_race()}")

    # 模拟多次错误猜测，超过 max_attempts
    for i in range(state.max_attempts + 5):
        guess = "wrong"
        feedback = [0, 0, 0, 0, 0]
        state.add_guess("player1", guess, feedback)
        print(
            f"猜测 {i + 1} 后, game_over={state.game_over}, attempts_used={state.attempts_used}, max_attempts={state.max_attempts}"
        )
        if state.game_over:
            print(f"游戏意外结束！winner={state.winner}")
            break
    # 预期游戏没有结束（因为 turn-based 模式已跳过限制）
    assert not state.game_over, (
        f"游戏不应在 {state.attempts_used} 次猜测后结束（turn-based 模式）"
    )
    print("✓ 游戏未因尝试次数用尽而结束")

    # 现在模拟猜中
    feedback = [2, 2, 2, 2, 2]
    state.add_guess("player1", target_word, feedback)
    assert state.game_over
    assert state.winner == "player1"
    print("✓ 猜中后游戏正确结束")

    print("所有测试通过")


if __name__ == "__main__":
    test_turn_based_no_limit()

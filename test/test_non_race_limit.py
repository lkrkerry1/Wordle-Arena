#!/usr/bin/env python3
"""测试非轮流模式仍有尝试次数限制"""

import sys

sys.path.insert(0, ".")

from core.game_controller import create_game_state
from core.game_state import GameMode


def test_single_mode_limit():
    # 创建一个单人模式状态
    target_word = "apple"
    mode = GameMode.SINGLE
    state = create_game_state(mode=mode, target_word=target_word)
    print(f"初始 max_attempts: {state.max_attempts}")
    print(f"模式是 race: {state.mode.is_race()}")

    # 模拟多次错误猜测，直到达到 max_attempts
    for i in range(state.max_attempts):
        guess = "wrong"
        feedback = [0, 0, 0, 0, 0]
        state.add_guess("player1", guess, feedback)
        print(f"猜测 {i + 1} 后, game_over={state.game_over}")
        if state.game_over:
            break
    # 预期游戏在 max_attempts 次猜测后结束
    assert state.game_over, f"游戏应在 {state.max_attempts} 次猜测后结束"
    assert state.winner is None, "不应有胜者"
    print("游戏在尝试次数用尽后正确结束")

    # 确保在游戏结束后不能再添加猜测
    try:
        state.add_guess("player1", "test", [0] * 5)
        assert False, "游戏结束后不应允许添加猜测"
    except RuntimeError as e:
        print(f"预期异常: {e}")

    print("所有测试通过")


if __name__ == "__main__":
    test_single_mode_limit()

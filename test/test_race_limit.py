#!/usr/bin/env python3
"""快速测试轮流模式下无尝试次数限制"""

import sys

sys.path.insert(0, ".")

from core.game_controller import create_game_state
from core.game_state import GameMode


def test_race_no_limit():
    # 创建一个 race 模式的状态 (VS_AI_RACE)
    target_word = "apple"
    mode = GameMode.VS_AI_RACE
    state = create_game_state(mode=mode, target_word=target_word)
    print(f"初始 max_attempts: {state.max_attempts}")
    print(f"模式是 race: {state.mode.is_race()}")

    # 模拟玩家1多次错误猜测，达到 max_attempts 次
    for i in range(state.max_attempts):
        guess = "wrong"
        feedback = [0, 0, 0, 0, 0]
        state.add_guess("player1", guess, feedback)
        print(f"猜测 {i + 1} 后, game_over={state.game_over}")
        if state.game_over:
            break
    # 预期游戏结束，因为玩家1用尽了尝试次数
    assert state.game_over, f"游戏应在 {state.max_attempts} 次猜测后结束"
    assert state.winner == "player2", f"赢家应为 player2，实际为 {state.winner}"
    print("✓ 玩家1尝试次数用尽，玩家2获胜")

    # 现在测试猜中场景（需要重置状态）
    state2 = create_game_state(mode=mode, target_word=target_word)
    feedback = [2, 2, 2, 2, 2]
    state2.add_guess("player1", target_word, feedback)
    assert state2.game_over
    assert state2.winner == "player1"
    print("✓ 猜中后游戏正确结束")

    print("所有测试通过")


if __name__ == "__main__":
    test_race_no_limit()

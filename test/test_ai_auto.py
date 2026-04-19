#!/usr/bin/env python3
"""
快速测试 AI 自动猜测功能。
启动服务器（如果未运行），创建一个 VS_AI_TURN 游戏，提交一个猜测，
然后轮询游戏状态，观察 AI 是否自动猜测。
"""

import sys
import time

import requests

BASE_URL = "http://localhost:5000"


def test_ai_auto():
    # 1. 创建游戏
    data = {
        "mode": "vs_ai_turn",
        "length": 5,
        "first_letter": None,
        "hard_mode": False,
        "word_bank": "words_gaokao.txt",
        "ai_temperature": 0.6,
        "ai_min_delay": 2.0,
        "ai_max_delay": 4.0,
    }
    resp = requests.post(f"{BASE_URL}/api/game", json=data)
    assert resp.status_code == 201, f"创建游戏失败: {resp.text}"
    session_id = resp.json()["session_id"]
    print(f"游戏已创建，session_id: {session_id}")

    # 2. 获取初始状态
    resp = requests.get(f"{BASE_URL}/api/game/{session_id}")
    assert resp.status_code == 200
    state = resp.json()
    print(f"初始状态: 模式={state['mode']}, 当前玩家={state['current_player']}")

    # 3. 玩家提交一个猜测（确保不是正确答案）
    guess = "apple"  # 假设这个词在词库中
    resp = requests.post(
        f"{BASE_URL}/api/game/{session_id}/guess", json={"guess": guess}
    )
    if resp.status_code != 200:
        # 如果单词不在词库中，尝试另一个词
        guess = "about"
        resp = requests.post(
            f"{BASE_URL}/api/game/{session_id}/guess", json={"guess": guess}
        )
    assert resp.status_code == 200, f"提交猜测失败: {resp.text}"
    result = resp.json()
    print(f"玩家猜测后: {result}")

    # 4. 等待一小段时间，让前端自动触发 AI 回合（如果前端正在运行）
    # 但我们可以直接调用 AI 回合端点，看看是否允许（应该允许，因为轮到 AI 了）
    # 不过，我们想测试的是自动触发，但这里我们只是验证游戏状态是否切换。
    # 我们轮询几次，观察当前玩家是否变为 player1（AI 猜测后）。
    max_polls = 10
    for i in range(max_polls):
        time.sleep(1)
        resp = requests.get(f"{BASE_URL}/api/game/{session_id}")
        state = resp.json()
        print(
            f"轮询 {i}: 当前玩家={state['current_player']}, 游戏结束={state['game_over']}"
        )
        if state["current_player"] == "player1":
            print("AI 已猜测并切换回玩家1，自动猜测可能已发生。")
            # 检查猜测列表是否增加
            if len(state["guesses"]) > 1:
                print(f"AI 猜测: {state['guesses'][-1]}")
                break
        if state["game_over"]:
            print("游戏意外结束。")
            break
    else:
        print("警告：在轮询期间未检测到 AI 猜测。")

    # 5. 清理（无）
    print("测试完成。")


if __name__ == "__main__":
    try:
        test_ai_auto()
    except Exception as e:
        print(f"测试失败: {e}")
        sys.exit(1)

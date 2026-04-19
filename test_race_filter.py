#!/usr/bin/env python3
"""
测试竞速模式玩家过滤功能。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json

from server import app


def test_player_filter():
    with app.test_client() as client:
        # 创建竞速游戏
        resp = client.post(
            "/api/game",
            data=json.dumps(
                {
                    "mode": "vs_ai_race",
                    "length": 5,
                    "hard_mode": False,
                    "word_bank": "words_gaokao.txt",
                    "ai_temperature": 0.6,
                    "ai_min_delay": 0.5,
                    "ai_max_delay": 1.0,
                }
            ),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        session_id = data["session_id"]
        print(f"Session: {session_id}")

        # 获取玩家1视角
        resp = client.get(f"/api/game/{session_id}?player=player1")
        assert resp.status_code == 200
        state = json.loads(resp.data)
        print(f"Player1 guesses: {len(state['guesses'])}")
        print(f"Opponent attempts: {state.get('opponent_attempts')}")
        assert "opponent_attempts" in state
        assert state["opponent_attempts"] == 0  # 初始应为0

        # 提交一个玩家1的猜测
        resp = client.post(
            f"/api/game/{session_id}/guess",
            data=json.dumps({"guess": "apple", "player_id": "player1"}),
            content_type="application/json",
        )
        # 可能失败（单词不在词库中），忽略

        # 再次获取玩家1视角
        resp = client.get(f"/api/game/{session_id}?player=player1")
        state = json.loads(resp.data)
        print(f"Player1 guesses after: {len(state['guesses'])}")
        print(f"Opponent attempts after: {state.get('opponent_attempts')}")
        # 对手尝试次数应仍为0（AI可能尚未猜测）

        # 获取完整状态（无玩家参数）
        resp = client.get(f"/api/game/{session_id}")
        state = json.loads(resp.data)
        print(f"Total guesses: {len(state['guesses'])}")

        print("测试通过")


if __name__ == "__main__":
    test_player_filter()

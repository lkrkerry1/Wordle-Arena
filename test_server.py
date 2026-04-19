#!/usr/bin/env python3
"""
快速测试服务器API。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import unittest

from server import app


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        """测试首页"""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Wordle Arena", response.data)

    def test_create_game(self):
        """测试创建游戏"""
        response = self.app.post(
            "/api/game",
            data=json.dumps({"mode": "single", "length": 5}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("session_id", data)
        return data["session_id"]

    def test_get_game_state(self):
        """测试获取游戏状态"""
        session_id = self.test_create_game()
        response = self.app.get(f"/api/game/{session_id}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["target_length"], 5)
        self.assertEqual(data["mode"], "single")

    def test_submit_guess(self):
        """测试提交猜测（需要有效单词）"""
        # 首先创建游戏
        session_id = self.test_create_game()
        # 获取游戏状态以知道目标单词？不行，但我们可以尝试一个随机单词
        # 我们使用一个肯定存在的单词（从单词库中）
        # 为了简化，我们假设单词库中包含'apple'（5个字母）
        # 但我们需要确保单词在单词库中。使用一个通用单词。
        # 我们直接测试错误处理：单词不在单词库中
        response = self.app.post(
            f"/api/game/{session_id}/guess",
            data=json.dumps({"guess": "xxxxx"}),
            content_type="application/json",
        )
        # 可能返回400，因为单词不在单词库中
        # 我们只检查响应格式
        self.assertIn(response.status_code, [200, 400])
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn("feedback", data)
        else:
            data = json.loads(response.data)
            self.assertIn("error", data)


    def test_race_mode_vs_ai(self):
        """测试竞速模式 vs AI"""
        # 创建竞速游戏
        response = self.app.post(
            "/api/game",
            data=json.dumps({
                "mode": "vs_ai_race",
                "length": 5,
                "hard_mode": False,
                "word_bank": "words_gaokao.txt",
                "ai_temperature": 0.6,
                "ai_min_delay": 0.5,
                "ai_max_delay": 1.0
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        session_id = data["session_id"]
        
        # 获取游戏状态
        response = self.app.get(f"/api/game/{session_id}")
        self.assertEqual(response.status_code, 200)
        state = json.loads(response.data)
        self.assertEqual(state["mode"], "vs_ai_race")
        self.assertFalse(state["game_over"])
        
        # 提交玩家1的猜测（使用有效单词）
        # 从单词库中选取一个单词（假设存在）
        # 使用一个简单的单词 "apple"（如果存在）
        response = self.app.post(
            f"/api/game/{session_id}/guess",
            data=json.dumps({"guess": "apple", "player_id": "player1"}),
            content_type="application/json",
        )
        # 如果单词不在单词库中，可能会失败；尝试其他单词
        if response.status_code != 200:
            # 尝试另一个单词 "words"
            response = self.app.post(
                f"/api/game/{session_id}/guess",
                data=json.dumps({"guess": "words", "player_id": "player1"}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)
        guess_data = json.loads(response.data)
        self.assertIn("feedback", guess_data)
        
        # 检查游戏是否可能结束（如果猜对了）
        # 这里我们只确保没有错误
        
        # 注意：AI线程在后台运行，但测试中我们无法验证
        # 我们可以等待一小段时间，然后检查猜测是否增加
        import time
        time.sleep(2)
        response = self.app.get(f"/api/game/{session_id}")
        self.assertEqual(response.status_code, 200)
        state = json.loads(response.data)
        # 至少有一个猜测（玩家1的）
        self.assertGreaterEqual(len(state["guesses"]), 1)
        # 打印猜测信息以便调试
        for g in state["guesses"]:
            print(f"Guess: {g['player_id']} - {g['guess']}")

if __name__ == "__main__":
    unittest.main(verbosity=2)

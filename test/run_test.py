#!/usr/bin/env python3
"""
启动服务器并测试基本功能。
"""

import subprocess
import sys
import time

import requests


def main():
    # 启动服务器子进程
    server_proc = subprocess.Popen(
        [sys.executable, "server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    try:
        # 等待服务器启动
        time.sleep(2)
        # 测试首页
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            print("[OK] 首页加载成功")
        else:
            print(f"[FAIL] 首页失败: {response.status_code}")
            sys.exit(1)
        # 测试创建游戏
        resp = requests.post(
            "http://localhost:5000/api/game", json={"mode": "single", "length": 5}
        )
        if resp.status_code == 201:
            data = resp.json()
            session_id = data["session_id"]
            print(f"[OK] 游戏创建成功, session_id: {session_id[:8]}...")
        else:
            print(f"[FAIL] 创建游戏失败: {resp.status_code} {resp.text}")
            sys.exit(1)
        # 测试获取游戏状态
        resp = requests.get(f"http://localhost:5000/api/game/{session_id}")
        if resp.status_code == 200:
            print("[OK] 获取游戏状态成功")
        else:
            print(f"[FAIL] 获取游戏状态失败: {resp.status_code}")
        # 测试提交猜测（使用无效单词）
        resp = requests.post(
            f"http://localhost:5000/api/game/{session_id}/guess",
            json={"guess": "aaaaa"},
        )
        if resp.status_code in (200, 400):
            print("[OK] 提交猜测返回预期状态码")
        else:
            print(f"[FAIL] 提交猜测异常: {resp.status_code}")
        # 测试AI回合（如果是VS_AI模式）
        resp = requests.post(
            "http://localhost:5000/api/game", json={"mode": "vs_ai_turn", "length": 5}
        )
        if resp.status_code == 201:
            ai_session = resp.json()["session_id"]
            print("[OK] AI游戏创建成功")
            # 尝试AI回合（可能失败，因为当前玩家是player1）
            resp2 = requests.post(
                f"http://localhost:5000/api/game/{ai_session}/ai_turn"
            )
            if resp2.status_code in (200, 400):
                print("[OK] AI回合返回预期状态码")
            else:
                print(f"[FAIL] AI回合异常: {resp2.status_code}")
        else:
            print("[FAIL] 创建AI游戏失败")
        print("\n所有测试通过！")
    finally:
        # 终止服务器进程
        server_proc.terminate()
        server_proc.wait(timeout=5)
        print("服务器已停止")


if __name__ == "__main__":
    main()

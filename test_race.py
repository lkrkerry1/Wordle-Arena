#!/usr/bin/env python3
"""
测试服务器竞速模式功能。
"""

import json
import subprocess
import sys
import time


# 启动服务器子进程
def start_server():
    cmd = [sys.executable, "server.py"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)  # 等待服务器启动
    return proc


# 发送HTTP请求
def http_request(method, path, data=None):
    import http.client

    conn = http.client.HTTPConnection("localhost", 5000)
    headers = {"Content-Type": "application/json"} if data else {}
    body = json.dumps(data) if data else None
    conn.request(method, path, body, headers)
    resp = conn.getresponse()
    resp_body = resp.read().decode()
    conn.close()
    try:
        return resp.status, json.loads(resp_body)
    except:
        return resp.status, resp_body


def test_race_vs_ai():
    print("测试竞速模式 vs AI...")
    # 创建游戏
    status, resp = http_request(
        "POST",
        "/api/game",
        {
            "mode": "vs_ai_race",
            "length": 5,
            "hard_mode": False,
            "word_bank": "words_gaokao.txt",
            "ai_temperature": 0.6,
            "ai_min_delay": 0.5,
            "ai_max_delay": 1.0,
        },
    )
    if status != 201:
        print(f"创建游戏失败: {status} {resp}")
        return False
    session_id = resp["session_id"]
    print(f"会话ID: {session_id}")

    # 获取游戏状态
    status, resp = http_request("GET", f"/api/game/{session_id}")
    if status != 200:
        print(f"获取游戏状态失败: {status} {resp}")
        return False
    print(f"游戏模式: {resp['mode']}")
    print(f"游戏是否结束: {resp['game_over']}")

    # 提交玩家1的猜测
    status, resp = http_request(
        "POST",
        f"/api/game/{session_id}/guess",
        {"guess": "apple", "player_id": "player1"},
    )
    if status != 200:
        print(f"猜测提交失败: {status} {resp}")
        # 可能是单词不在词典中，尝试另一个单词
        status, resp = http_request(
            "POST",
            f"/api/game/{session_id}/guess",
            {"guess": "words", "player_id": "player1"},
        )
        if status != 200:
            print(f"第二次猜测提交失败: {status} {resp}")
            return False
    print(f"猜测反馈: {resp}")

    # 等待AI猜测（等待几秒）
    time.sleep(3)

    # 再次获取游戏状态，查看是否有AI的猜测
    status, resp = http_request("GET", f"/api/game/{session_id}")
    if status != 200:
        print(f"获取游戏状态失败: {status} {resp}")
        return False
    guesses = resp["guesses"]
    print(f"总猜测数: {len(guesses)}")
    for g in guesses:
        print(f"  玩家 {g['player_id']}: {g['guess']}")

    # 检查游戏是否结束
    if resp["game_over"]:
        print(f"游戏结束，赢家: {resp.get('winner')}")

    return True


def main():
    print("启动服务器...")
    proc = start_server()
    try:
        # 等待服务器完全启动
        time.sleep(3)
        if not test_race_vs_ai():
            print("测试失败")
            sys.exit(1)
        print("测试通过")
    finally:
        proc.terminate()
        proc.wait()
        print("服务器已停止")


if __name__ == "__main__":
    main()

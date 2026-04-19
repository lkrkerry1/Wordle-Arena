#!/usr/bin/env python3
import requests

BASE = "http://localhost:5000"

# 1. 创建游戏，使用 common 词库
resp = requests.post(
    f"{BASE}/api/game",
    json={
        "mode": "single",
        "length": 5,
        "first_letter": None,
        "hard_mode": False,
        "word_bank": "common_6000_words.txt",
        "ai_temperature": 0.6,
        "ai_min_delay": 2.0,
        "ai_max_delay": 4.0,
    },
)
print("Create response:", resp.status_code, resp.text)
if resp.status_code != 201:
    print("Failed to create game")
    exit()
session = resp.json()["session_id"]
print("Session:", session)

# 2. 尝试提交猜测 "henry"
resp2 = requests.post(f"{BASE}/api/game/{session}/guess", json={"guess": "henry"})
print("Guess response:", resp2.status_code, resp2.text)
if resp2.status_code != 200:
    print("Guess failed")
else:
    print("Guess succeeded")

# 3. 获取游戏状态
resp3 = requests.get(f"{BASE}/api/game/{session}")
print("State:", resp3.status_code, resp3.text)

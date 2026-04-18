# Wordle Arena

一个功能丰富的 Wordle 类猜词游戏，支持多种游戏模式、AI 对手和竞速挑战。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## 功能特性

- **多种游戏模式**：经典模式、限时模式、练习模式、双人竞速、AI 对战
- **可调节难度**：支持自定义词长（4‑8 字母）、硬核模式（反馈约束）、时间限制
- **智能 AI 对手**：基于反馈的启发式算法，可调节思考速度与随机性
- **实时竞速看板**：双人同时猜词，实时显示对手进度与用时
- **回放与统计**：自动保存每局记录，支持历史回放与数据统计
- **图形化界面**：使用 Tkinter 构建，界面简洁、响应迅速
- **多词库支持**：内置 CET‑4、高考、全量词库，也可自定义词表

## 安装与运行

### 环境要求

- Python 3.8 或更高版本
- 无需额外依赖（仅使用标准库）

### 步骤

1. 克隆或下载本项目：
   ```bash
   git clone https://github.com/yourusername/wordle-arena.git
   cd wordle-arena
   ```

2. 直接运行主程序：
   ```bash
   python main.py
   ```

   或使用可执行脚本（若已配置）：
   ```bash
   ./main.py
   ```

## 服务器版本

除了桌面 GUI 版本，本项目还提供了一个基于 Web 的服务器版本，允许你在本地运行一个网页游戏。

### 运行服务器

1. 安装额外依赖（Flask）：
   ```bash
   pip install flask
   ```

2. 启动服务器：
   ```bash
   python server.py
   ```

3. 打开浏览器访问 [http://localhost:5000](http://localhost:5000) 即可开始游戏。

### 功能特点

- 提供与桌面版相同的核心游戏逻辑（单人模式、AI 对战等）
- 响应式 Web 界面，支持键盘输入与实时反馈
- 完整的 REST API，可用于第三方集成
- 会话管理，支持多用户同时游戏

### API 接口

- `GET /` – 返回前端页面
- `POST /api/game` – 创建新游戏
- `GET /api/game/<session_id>` – 获取游戏状态
- `POST /api/game/<session_id>/guess` – 提交猜测
- `POST /api/game/<session_id>/ai_turn` – 请求 AI 进行猜测

详细 API 文档请参阅 `server.py` 源码。

## 使用方法

1. **启动游戏**：运行 `main.py` 后，主窗口将显示菜单。
2. **选择模式**：
   - **经典模式**：单人猜词，可设置词长、是否硬核。
   - **限时模式**：在指定时间（默认 60 秒）内尽可能猜出更多单词。
   - **练习模式**：无限制尝试，适合熟悉规则。
   - **双人竞速**：两位玩家（或一位玩家与 AI）同时猜同一单词，比拼速度。
   - **AI 对战**：观看 AI 自己完成猜词过程。
3. **进行游戏**：
   - 在输入框键入单词，按 Enter 提交。
   - 格子颜色反馈：
     - 🟩 绿色：字母正确且位置正确。
     - 🟨 黄色：字母正确但位置错误。
     - ⬜ 灰色：字母不在单词中。
   - 利用反馈逐步缩小范围，最终猜出目标单词。
4. **查看结果**：游戏结束后会显示所用次数、时间，并可选择保存记录或回放。

## 配置说明

配置文件 `config.json` 位于项目根目录，可编辑以下选项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `word_bank` | 词库文件（位于 `data/` 目录） | `"words_full.txt"` |
| `word_length` | 单词长度，可选 `4`‑`8` 或 `"random"` | `"random"` |
| `hard_mode` | 硬核模式，要求每次猜测必须符合之前的反馈 | `false` |
| `ai_temperature` | AI 随机性（0 为完全确定，值越高越随机） | `0.0` |
| `ai_min_delay` | AI 最小思考延迟（秒） | `0.5` |
| `ai_max_delay` | AI 最大思考延迟（秒） | `2.0` |
| `time_limit` | 限时模式的时间限制（秒） | `60` |

## 项目结构

```
wordle-arena/
├── main.py                 # 程序入口
├── config.json             # 用户配置
├── README.md               # 本文档
├── LICENSE                 # 许可证文件
├── core/                   # 核心游戏逻辑
│   ├── game_state.py       # 游戏状态定义
│   ├── game_controller.py  # 游戏流程控制
│   ├── ai_player.py        # AI 玩家实现
│   ├── feedback.py         # 反馈计算
│   └── word_bank.py        # 词库管理
├── gui/                    # 图形界面
│   ├── main_window.py      # 主窗口与菜单
│   ├── game_board.py       # 游戏画布
│   ├── race_board.py       # 竞速看板
│   ├── replay_window.py    # 回放窗口
│   └── dialogs.py          # 设置与信息对话框
├── data/                   # 词库文件
│   ├── words_cet4.txt      # CET‑4 词汇
│   ├── words_gaokao.txt    # 高考词汇
│   └── words_full.txt      # 全量词汇
└── utils/                  # 工具模块
    └── helpers.py          # 辅助函数
```

## 开发与贡献

欢迎提交 Issue 或 Pull Request 来改进本项目。

### 代码规范

- 使用 **Ruff** 进行代码格式化与 lint。
- 遵循 **PEP 8** 风格。
- 添加适当的类型注解（Type Hints）。

### 本地开发

1. 安装开发工具：
   ```bash
   pip install ruff
   ```

2. 运行 lint：
   ```bash
   ruff check .
   ```

3. 运行测试（若有）：
   ```bash
   python -m pytest
   ```

## 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

## 致谢

- 灵感来源于 **Wordle** (Josh Wardle) 及其衍生作品。
- 词库基于公开英语词汇表整理。

## 联系

如有问题或建议，请通过 GitHub Issues 反馈。

---
**Happy Wordling!** 🎮🟩🟨⬜
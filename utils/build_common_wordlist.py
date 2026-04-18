# 文件名: build_common_wordlist.py
"""
从COCA词频文件中提取前6000个常用单词，并筛选长度为4-8的单词。
使用方法: python build_common_wordlist.py <你的coca文件>.txt
"""

import re
import sys
from pathlib import Path


def extract_top_words(file_path: Path, top_n: int = 6000) -> list[str]:
    """从词频文件中提取前N个单词。

    Args:
        file_path: 词频文件路径。
        top_n: 需要提取的单词数量（默认6000）。

    Returns:
        提取到的单词列表。
    """
    words = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            # 跳过注释行和标题行
            if line.startswith("*") or "rank" in line.lower():
                continue
            if len(words) >= top_n:
                break
            # 按制表符分割，如果不行则按空白字符分割
            if "\t" in line:
                parts = line.split("\t")
            else:
                parts = line.split()
            if len(parts) < 2:
                # 如果只有一列，则使用第一列
                raw_word = parts[0] if parts else ""
            else:
                # 第二列是词元（lemma）
                raw_word = parts[1]
            # 清洗单词，只保留字母
            word = re.sub(r"[^a-zA-Z]", "", raw_word.lower())
            if word:
                words.append(word)
    return words


def filter_by_length(words: list[str], min_len: int = 4, max_len: int = 8) -> list[str]:
    """按指定长度筛选单词，并去重、排序。

    Args:
        words: 原始单词列表。
        min_len: 最小长度（默认4）。
        max_len: 最大长度（默认8）。

    Returns:
        筛选并排序后的唯一单词列表。
    """
    return sorted(list({w for w in words if min_len <= len(w) <= max_len}))


def save_words(words: list[str], output_file: Path) -> None:
    """将单词列表保存到文件。

    Args:
        words: 单词列表。
        output_file: 输出文件路径。
    """
    with open(output_file, "w", encoding="utf-8") as f:
        for word in words:
            f.write(word + "\n")
    print(f"成功！已生成词库文件: {output_file} (共 {len(words)} 个单词)")


def main() -> None:
    """主函数：处理原始词频文件，输出Wordle词库。"""
    if len(sys.argv) < 2:
        print("使用方法: python build_common_wordlist.py <你的coca文件>.txt")
        sys.exit(1)

    raw_file = Path(sys.argv[1])
    if not raw_file.exists():
        print(f"错误: 文件未找到 '{raw_file}'")
        sys.exit(1)

    print(f"正在处理: {raw_file}...")
    # 1. 提取前6000词
    top_6000 = extract_top_words(raw_file)
    # 2. 筛选长度
    filtered_words = filter_by_length(top_6000)
    # 3. 保存结果
    output_file = raw_file.parent / "common_6000_words.txt"
    save_words(filtered_words, output_file)


if __name__ == "__main__":
    main()

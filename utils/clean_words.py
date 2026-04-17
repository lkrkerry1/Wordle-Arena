#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词库清洗脚本
功能：从包含各种混杂信息（中文释义、音标等）的文本中提取出纯英文单词，
     并按长度（4-8字母）和字母顺序进行过滤和排序。
使用方法：python clean_words.py <你的原始词汇文件>.txt
"""

import re
import sys
from pathlib import Path
from typing import List, Set


def extract_english_words(text: str) -> Set[str]:
    """使用正则表达式从文本中提取所有英文单词。"""
    words = set(re.findall(r"\b[a-zA-Z]+\b", text))
    return {word.lower() for word in words}


def filter_by_length(words: Set[str], min_len: int = 4, max_len: int = 8) -> List[str]:
    """按指定长度筛选单词，并返回按字母排序的列表。"""
    filtered = [word for word in words if min_len <= len(word) <= max_len]
    return sorted(filtered)


def save_words(words: List[str], output_file: Path) -> None:
    """将单词列表保存到文件，每行一个单词。"""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for word in words:
            f.write(word + "\n")
    print(f"✅ 处理完成！已生成词库文件: {output_file} (共 {len(words)} 个单词)")


def main() -> None:
    """主函数：处理输入的原始文件，输出清洗后的词库。"""
    if len(sys.argv) < 2:
        print("使用方法: python clean_words.py <你的原始词汇文件>.txt")
        sys.exit(1)

    raw_file = Path(sys.argv[1])
    if not raw_file.exists():
        print(f"❌ 错误: 文件未找到 '{raw_file}'")
        sys.exit(1)

    print(f"🔍 正在处理文件: {raw_file}...")
    text = raw_file.read_text(encoding="utf-8")

    # 提取、过滤并保存
    all_words = extract_english_words(text)
    filtered_words = filter_by_length(all_words)
    output_file = raw_file.parent / f"{raw_file.stem}_cleaned.txt"
    save_words(filtered_words, output_file)


if __name__ == "__main__":
    main()

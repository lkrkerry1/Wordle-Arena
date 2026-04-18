import logging


def filter_wordle_words(input_file: str, output_file: str) -> None:
    """筛选Wordle可用的纯字母单词（长度4-8）。"""
    with (
        open(input_file, "r", encoding="utf-8") as f_in,
        open(output_file, "w", encoding="utf-8") as f_out,
    ):
        for line in f_in:
            word = line.strip().lower()
            if 4 <= len(word) <= 8 and word.isalpha():
                f_out.write(word + "\n")


if __name__ == "__main__":
    logging.info("Start filter")
    filter_wordle_words(r"data\words_alpha.txt", r"data\words_full.txt")

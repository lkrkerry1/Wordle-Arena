#!/usr/bin/env python3
import sys

sys.path.insert(0, ".")
from core.word_bank import WordBank

wb = WordBank(data_dir="data", bank_name=None)
print("Loaded word bank with lengths:", wb.get_available_lengths())
word = "henry"
length = len(word)
print(f"Checking '{word}' (length {length})")
if wb.contains(word):
    print("Word found in word_bank")
else:
    print("Word NOT found in word_bank")
    # Let's see what words of length 5 are present
    words_len5 = wb.get_words_by_length(5)
    print(f"Total words of length 5: {len(words_len5)}")
    if "henry" in words_len5:
        print("Actually found in list")
    else:
        # maybe it's capitalized?
        if "henry".lower() in words_len5:
            print("Found lowercased")
        else:
            # search
            for w in words_len5[:20]:
                print(w)
            print("...")

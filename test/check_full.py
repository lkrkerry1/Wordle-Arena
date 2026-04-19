import sys

sys.path.insert(0, ".")
from core.word_bank import WordBank

wb = WordBank(data_dir="data", bank_name=None)
print("Word bank files loaded:", wb.word_lists.keys())
print("Checking 'henry' in word_sets_set[5]?")
if 5 in wb.word_sets_set:
    print("Set size:", len(wb.word_sets_set[5]))
    if "henry" in wb.word_sets_set[5]:
        print("Found!")
    else:
        print("Not found.")
        # maybe it's uppercase?
        if "henry".upper() in wb.word_sets_set[5]:
            print("Found uppercase")
        else:
            # maybe it's in another length?
            for length, s in wb.word_sets_set.items():
                if "henry" in s:
                    print(f"Found in length {length}")
                    break
else:
    print("No length 5 set")
# Also check raw word list
words5 = wb.get_words_by_length(5)
print("Total words length 5:", len(words5))
if "henry" in words5:
    print("Found in get_words_by_length")
else:
    # search
    for w in words5[:100]:
        if "henry" in w:
            print(w)
    print("...")

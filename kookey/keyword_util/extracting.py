#-*-coding:utf-8-*-

from collections import Counter
import math
import re


def get_n_gram_data(encoded_sentences, split_index, n):
    candidates = []

    for sent in encoded_sentences:
        sub_index = []

        for i in sent:
            if i != split_index:
                sub_index.append(i)
            else:
                if len(sub_index) >= n:
                    candidates += zip(*[sub_index[j:] for j in range(n)])

                sub_index = []

    return candidates


def get_co_occurrance(n_gram_candidate):
    return Counter(n_gram_candidate)


def get_ppmi(co_occurrance, co_occurrance_by_1_gram):
    ppmi = {}
    N = len(co_occurrance_by_1_gram)

    for key in co_occurrance.keys():
        mul = 1
        
        for index in key:
            mul *= co_occurrance_by_1_gram[(index,)]

        ppmi_value = round(math.log(co_occurrance[key] * N / mul), 2)

        if ppmi_value > 0:
            ppmi[key] = ppmi_value

    return ppmi


def cleansing_word_head_and_tail(word, save_characters):
    if len(word) > 0 and word[0] in save_characters:
        word[1:]

    if len(word) > 0 and word[-1] in save_characters:
        word = word[:-1]

    return word


def is_not_stop_word(word, stop_words):
    if word in stop_words:
        return False
    
    return True


def is_in_length(word, save_characters,
    en_len_min, en_len_max, kor_len_min, kor_len_max):
    save_ch = "".join(save_characters)
    english = re.compile(r"^[a-z" + save_ch + r"]+$")
    hangul = re.compile(r"^[가-힣" + save_ch + r"]+$")

    if english.match(word):
        if not (en_len_min <= len(word) <= en_len_max):
            return False

    if hangul.match(word):
        if not (kor_len_min <= len(word) <= kor_len_max):
            return False

    return True
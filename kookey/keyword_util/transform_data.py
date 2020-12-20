#-*-coding:utf-8-*-

from collections import Counter


def get_sent_by_morphs(sent, tokenizer, save_characters, save_morphs, limit):
    morphs = tokenizer.pos(sent)

    result = []
    for i in range(len(morphs)):
        word, tag = morphs[i]
        
        if (len(result) > 1 
            and word not in save_characters
            and word in result[-1]):
            continue

        if word in save_characters:
            if ((i > 0 and len(morphs[i-1][0]) < limit)
                and (i < len(morphs) - 1 and len(morphs[i+1][0]) < limit)):
                if len(result) > 1:
                    result[-1] = result[-1] + word + morphs[i+1][0]

        elif tag in save_morphs:
            result.append(word)

        else:
            result.append("")

    if len(result) > 1 and result[-1] != "":
        result = result[:-1]

    return result


def indexing(morphs):
    word_frequency = sorted(dict(Counter(morphs)).items(),
        key=lambda x:x[1], reverse=True)

    index = 0
    word_index = {}
    index_word = {}

    for key, _ in word_frequency:
        word_index[key] = index
        index_word[index] = key
        index += 1

    return word_frequency, word_index, index_word


def encoding_sentences(sentences_by_morphs, word_index):
    sent_by_index = []

    for sent in sentences_by_morphs:
        index_list = []

        for morph in sent:
            index_list.append(word_index[morph])

        sent_by_index.append(index_list)

    return sent_by_index


def decoding_words(co_occurrance, index_word):
    result = {}

    for key in co_occurrance.keys():
        word = ""

        for i in key:
            word += index_word[i]

        result[word] = co_occurrance[key]

    return sorted(result.items(), key=lambda x:x[1], reverse=True)
#-*-coding:utf-8-*-

from nltk.tokenize import sent_tokenize


def get_sent_list(tokenizer, text):
    text_list = sent_tokenize(text)

    result = []
    for sent in text_list:
        pos = tokenizer.pos(sent)

        index = [len(pos[0][0]) - 1]
        for i in range(1, len(pos)):
            index.append(index[-1] + sent[index[-1] + 1:].find(pos[i][0]) + len(pos[i][0]))

        split_index = []
        for i in range(len(pos)):
            if pos[i][1] == "SF":
                split_index.append(index[i])
            elif "EF" in pos[i][1]:
                if i < len(pos) - 1:
                    if pos[i + 1][1] != "SF":
                        split_index.append(index[i])

        if len(split_index) <= 1:
            result.append(sent)
        elif len(split_index) > 1:
            start = 0
            for i in split_index:
                if start != 0:
                    result.append(sent[start:i+1])
                    start = i + 1

    return result


def jaccard_similarity(sent_morphs, compare_morphs):
    sent_morphs_set = set(sent_morphs)
    compare_sent_set = set(compare_morphs)

    return round(len(sent_morphs_set & compare_sent_set)
                     / len(sent_morphs_set | compare_sent_set), 2)


def check_stop_sent(tokenizer, sent, compare_sents, threshold):
    check = False
    sent_morphs = tokenizer.morphs(sent)

    for compare_sent in compare_sents:
        compare_morphs = tokenizer.morphs(compare_sent)

        if jaccard_similarity(sent_morphs, compare_morphs) > threshold:
            check = True
            break

    return check


def check_stop_head(sent, stop_heads):
    check = False

    for head in stop_heads:
        length = len(head)

        if sent[:length] == head:
            check = True
            break
    
    return check
            
#-*-coding:utf-8-*-

from soynlp.hangle import compose, decompose, character_is_korean
import re


# 코드 출처 : 한국어 임베딩(저자 : 이기창님)
def sent_to_jamo(sent):

    def transform(char):
        if char == " ":
            return char
        
        cjj = decompose(char)
        if len(cjj) == 1:
            return cjj
        
        cjj_ = "".join(c if c != " " else "-" for c in cjj)
        return cjj_
    
    sent_ = []
    for char in sent:
        if  character_is_korean(char):
            sent_.append(transform(char))
        else:
            sent_.append(char)
            
    doublespace_pattern = re.compile("\s+")
    sent_ = doublespace_pattern.sub(" ", "".join(sent_))
    
    return sent_


# 코드 출처 : 한국어 임베딩(저자 : 이기창님)
def jamo_to_word(jamo):
    jamo_list, idx = [], 0
    
    while idx < len(jamo):
        if not character_is_korean(jamo[idx]):
            jamo_list.append(jamo[idx])
            idx += 1
        else:
            jamo_list.append(jamo[idx:idx+3])
            idx += 3
            
    word = ""
    for jamo_char in jamo_list:
        if len(jamo_char) == 1:
            word += jamo_char
        elif jamo_char[2] == "-":
            word += compose(jamo_char[0], jamo_char[1], " ")
        else:
            word += compose(jamo_char[0], jamo_char[1], jamo_char[2])
            
    return word


def trans_sents_for_embedding(sentences_, tokenizer, jamo):
    sentences = []

    for sent in sentences_:
        change_sent = tokenizer.morphs(sent)
        if jamo:
            change_sent = sent_to_jamo(" ".join(change_sent))
        sentences.append(change_sent)

    return sentences


def trans_words_for_tuning(train_data, test_data, embedding_word_index, jamo):
    train_encoded_word1, train_encoded_word2 = get_encoded_data(
        train_data, embedding_word_index, jamo)
    test_encoded_word1, test_encoded_word2 = get_encoded_data(
        test_data, embedding_word_index, jamo)

    max_len = get_max_len(train_encoded_word1 + train_encoded_word2
                         + test_encoded_word1 + test_encoded_word2)

    train_padded_data = get_padded_data(train_encoded_word1, train_encoded_word2,
                                       embedding_word_index, max_len)
    test_padded_data = get_padded_data(test_encoded_word1, test_encoded_word2,
                                      embedding_word_index, max_len)

    return train_padded_data, test_padded_data, max_len


def get_encoded_data(data, embedding_word_index, jamo):
    encoded_word1 = []
    encoded_word2 = []
    
    for word1, word2 in data:
        encoded_word1.append(get_encoded_word(word1, embedding_word_index, jamo))
        encoded_word2.append(get_encoded_word(word2, embedding_word_index, jamo))
        
    return encoded_word1, encoded_word2


def get_encoded_word(word, embedding_word_index, jamo):
    split_list = word.split(" ")

    result = []
    for el in split_list:
        try:
            if jamo:
                result.append(sent_to_jamo(embedding_word_index[el]))
            else:
                result.append(embedding_word_index[el])
        except:
            result.append(embedding_word_index["<UNK>"])

    return result


def get_max_len(data):
    return max([len(el) for el in data])


def get_padded_data(encoded_word1, encoded_word2, embedding_word_index, max_len):
    padded_word1 = [get_padded_word(el, embedding_word_index, max_len) for el in encoded_word1]
    padded_word2 = [get_padded_word(el, embedding_word_index, max_len) for el in encoded_word2]

    return [padded_word1, padded_word2]


def get_padded_word(encoded_word, embedding_word_index, max_len):
    pad_len = max_len - len(encoded_word)
    pad_index = embedding_word_index["<PAD>"]
    
    if pad_len >= 0:
        padded_word = encoded_word + [pad_index] * pad_len
    else:
        padded_word = encoded_word[:max_len]
        
    return padded_word



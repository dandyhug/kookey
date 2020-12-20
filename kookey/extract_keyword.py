#-*-coding:utf-8-*-

from kookey.tokenizer import Tokenizer
from kookey.keyword_util.transform_data import *
from kookey.keyword_util.extracting import *


class KeywordExtractor:

    def __init__(self,
        stop_words=[],
        tokenizer="Kkma",
        save_characters=[], save_morphs = [],
        special_characters_linking_limit=float("inf"),
        n_gram_limit=2,
        calculate_ppmi=False,
        freq_min=2,
        en_len_min=3, en_len_max=15,
        kor_len_min=2, kor_len_max=float("inf")):

        self.stop_words = stop_words

        self.tokenizer = Tokenizer(tokenizer).tokenizer

        self.save_characters = save_characters
        self.save_morphs = save_morphs
        self.special_characters_linking_limit = special_characters_linking_limit

        self.n_gram_limit = n_gram_limit
        self.calculate_ppmi = calculate_ppmi
        self.freq_min = freq_min

        self.en_len_min = en_len_min
        self.en_len_max = en_len_max
        self.kor_len_min = kor_len_min
        self.kor_len_max = kor_len_max


    def get_keyword_candidate(self, sentences):

        def extract_keyword(merged_decoded_data):
            word_collection = []

            for key, word_freq_dict in merged_decoded_data.items():
                for word, freq in word_freq_dict:
                    word = cleansing_word_head_and_tail(word, self.save_characters)

                    if (is_not_stop_word(word, self.stop_words)
                        and is_in_length(word, self.save_characters,
                        self.en_len_min, self.en_len_max, self.kor_len_min, self.kor_len_max)):
                        word_collection.append((word, freq, key))

            return word_collection

        
        _, word_index, index_word, encoded_sentences = self.encoding(sentences)
        co_occurrance_data = self.get_co_occurrance(encoded_sentences, word_index)
        decoded_data = self.decoding(co_occurrance_data, index_word)

        if self.calculate_ppmi:
            ppmi_data = self.get_ppmi(co_occurrance_data)
            decoded_ppmi_data = self.decoding(ppmi_data, index_word)

        merged_decoded_data = {**decoded_data, **decoded_ppmi_data}
        keyword_candidate = extract_keyword(merged_decoded_data)

        return keyword_candidate


    def encoding(self, sentences):
        flatten_morphs = []
        sentences_by_morphs = []

        for sent in sentences:
            morphs = get_sent_by_morphs(sent, self.tokenizer, self.save_characters, 
                self.save_morphs, self.special_characters_linking_limit)
            
            if morphs:
                flatten_morphs += morphs
                sentences_by_morphs.append(morphs)

        word_freq, word_index, index_word = indexing(flatten_morphs)
        encoded_sentences = encoding_sentences(sentences_by_morphs, word_index)

        return word_freq, word_index, index_word, encoded_sentences


    def get_co_occurrance(self, encoded_sentences, word_index):
        co_occurrance_data = {}

        for i in range(1, self.n_gram_limit + 1):
            n_gram = get_n_gram_data(encoded_sentences, word_index[""], i)
            co_occurrance = get_co_occurrance(n_gram)
            co_occurrance_data[str(i) + "_gram"] = co_occurrance

        return co_occurrance_data


    def get_ppmi(self, co_occurrance_data):
        if self.n_gram_limit < 2:
            raise RuntimeError("Limit of n-gram must be over 2.")

        ppmi_data = {}

        for i in range(2, self.n_gram_limit + 1):
            ppmi = get_ppmi(
                co_occurrance_data[str(i) + "_gram"],
                co_occurrance_data["1_gram"]
            )
            ppmi_data["ppmi-" + str(i) + "_gram"] = ppmi

        return ppmi_data


    def decoding(self, co_occurrance_data, index_word):
        decoded_data = {}

        for key in co_occurrance_data.keys():
            decoded_data[key] = decoding_words(
                co_occurrance_data[key],
                index_word
            )

        return decoded_data
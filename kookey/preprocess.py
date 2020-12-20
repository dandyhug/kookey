#-*-coding:utf-8-*-

from kookey.preprocess_util.clean_sentences import *
from kookey.preprocess_util.clean_with_regx import *
from kookey.tokenizer import Tokenizer


class Preprocess:
    
    def __init__(self,
        separate_sentences=True,
        stop_sents=[], jaccard_threshold=0.55, 
        stop_heads=[],
        save_characters=[],
        tokenizer="Kkma",
        low_case=True, remove_html=True, remove_datetime=True, 
        remove_query=True, remove_url=True, remove_email=True, 
        remove_phone=True, remove_ip=True, remove_many_whitespace=True, 
        remove_characters=True):

        self.separate_sentences = separate_sentences
        
        self.stop_sents = stop_sents
        self.jaccard_threshold = jaccard_threshold
        
        self.stop_heads = stop_heads

        self.save_characters = save_characters

        self.tokenizer = Tokenizer(tokenizer).tokenizer

        self.low_case = low_case
        self.remove_html = remove_html
        self.remove_datetime = remove_datetime
        self.remove_query = remove_query
        self.remove_url = remove_url
        self.remove_email = remove_email
        self.remove_phone = remove_phone
        self.remove_ip = remove_ip
        self.remove_many_whitespace = remove_many_whitespace
        self.remove_characters = remove_characters


    def preprocess(self, corpus):
        sentences = []

        if type(corpus) is str:
            corpus = [corpus]
        elif type(corpus) is not list:
            raise RuntimeError("Corpus must be list or string")

        for text in corpus:
            text = self.transform_case_and_remove_html(text)
            text = self.cleansing_by_options(text)
            sentences += get_sent_list(self.tokenizer, text)

        sentences = self.remove_unnecessary_sentences(sentences)

        return sentences


    def transform_case_and_remove_html(self, text):
        if self.remove_html:
            text = cleansing_html(text)

        if self.low_case:
            text = transform_lower_case(text)
        else:
            text = transform_upper_case

        return text


    def cleansing_by_options(self, text):
        if self.remove_datetime:
            text = cleansing_datetime(text)

        if self.remove_query:
            text = cleansing_query(text)

        if self.remove_url:
            text = cleansing_url(text)

        if self.remove_email:
            text = cleansing_email(text)

        if self.remove_phone:
            text = cleansing_phone_number(text)

        if self.remove_ip:
            text = cleansing_ip(text)

        if self.remove_characters:
            text = cleansing_characters(text, self.save_characters)

        if self.remove_many_whitespace:
            text = cleansing_many_whitespace(text)

        return text


    def remove_unnecessary_sentences(self, sentences):
        result_sentences = []
        for sent in sentences:
            stop_sent_check, stop_head_check = False, False

            if self.stop_sents:
                stop_sent_check = check_stop_sent(self.tokenizer, 
                    sent, self.stop_sents, self.jaccard_threshold)
            
            if self.stop_heads:
                stop_head_check = check_stop_head(sent, self.stop_heads)

            if not(stop_sent_check and stop_head_check):
                result_sentences.append(sent)

        return result_sentences

        

        
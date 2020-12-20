#-*-coding:utf-8-*-

from konlpy.tag import Mecab, Hannanum, Kkma, Komoran, Okt


class Tokenizer:

    def __init__(self, tokenizer):
        self.tokenizer = self.get_tokenizer(tokenizer)


    def get_tokenizer(self, tokenizer):
        tokenizer = tokenizer.lower()

        if tokenizer == "mecab":
            tokenizer = Mecab()

        elif tokenizer == "hannanum":
            tokenizer = Hannanum()

        elif tokenizer == "kkma":
            tokenizer = Kkma()

        elif tokenizer == "komoran":
            tokenizer = Komoran()

        elif tokenizer == "Okt":
            tokenizer = Okt()

        else:
            raise RuntimeError("Tokenizer must be the one of Mecab, Hannanum, Kkma, Komoran, Okt.")

        return tokenizer
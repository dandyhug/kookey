#-*-coding:utf-8-*-

import unittest
from kookey.extract_keyword import KeywordExtractor
from kookey.keyword_util.extracting import *


class KeywordExtractorTest(unittest.TestCase):

    def test_extract_keywords(self):
        sentences = [
            "오늘은 약 10-12도 맑음이니까 날씨가 좋아요.",
            "복합명사를 추출할 수 있는데, 이런게 복합이죠!.",
            "이번에 새로 들여온 설비의 이름은 built-in-982입니다.",
            "로그를 보니 ^$^&%&#@#$ 이렇게 적혀있네요."
        ]

        keyword_extractor = KeywordExtractor(calculate_ppmi=True,
            save_characters=["-"], save_morphs=["NNG", "SL", "SN", "OL", "NR"])

        keywords = keyword_extractor.get_keyword_candidate(sentences)

        self.assertIn(('설비', 1, '1_gram'), keywords)
        self.assertIn(('built-in-982', 1, '2_gram'), keywords)
        self.assertIn("복합명사", [el[0] for el in keywords])


    def test_get_n_gram_data(self):
        encoded_sentences = [[1, 3, 0, 2, 4, 8, 0, 3, 5, 7, 0, 9, 0],
            [1, 2, 4, 8, 0, 3, 0]]

        result = get_n_gram_data(encoded_sentences, 0, 1)
        self.assertIn((1,), result)

        result = get_n_gram_data(encoded_sentences, 0, 2)
        self.assertIn((2, 4), result)

        result = get_n_gram_data(encoded_sentences, 0, 3)
        self.assertIn((1, 2, 4), result)


    def test_get_co_occurrance(self):
        n_gram_result = [(1,), (3,), (1, 3), (2,), (4,), (8,),
            (2, 4), (4, 8), (2, 4, 8), (3,), (5,), (7,), (3, 5),
            (5, 7), (3, 5, 7), (9,), (1,), (2,), (4,), (8,),
            (1, 2), (2, 4), (4, 8), (1, 2, 4), (2, 4, 8),
            (1, 2, 4, 8), (3,)]

        result = get_co_occurrance(n_gram_result)

        self.assertEqual(result[(3,)], 3)
        self.assertEqual(result[(3, 5, 7)], 1)


if __name__ == "__main__":
    unittest.main()
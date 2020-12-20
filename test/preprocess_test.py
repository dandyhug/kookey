#-*-coding:utf-8-*-

import unittest
from kookey.preprocess import Preprocess
from kookey.preprocess_util.clean_sentences import *
from kookey.preprocess_util.clean_with_regx import *


class PreprocessTest(unittest.TestCase):

    def test_preprocess_with_corpus(self):
       preprocess = Preprocess()
       result = preprocess.preprocess("안녕하세요. 반갑습니다. 성함이     어떻게 되세요?")

       self.assertEqual([
           "안녕하세요.",
           "반갑습니다.",
           "성함이 어떻게 되세요?"
       ], result)

    
    def test_preprocess_with_list(self):
        preprocess = Preprocess()
        result = preprocess.preprocess([
            "오늘,- 날씨가 좋아요.",
            "영화는   어땠나요?",
            "오늘은 신나는 금요일이에요!><"
        ])

        self.assertEqual([
            "오늘 날씨가 좋아요.",
            "영화는 어땠나요?",
            "오늘은 신나는 금요일이에요!"
        ], result)


    def test_cleansing_html(self):
        text1 = "<html><head>테스트용html</head><body><div>오늘은 바나나가 맛있어보여요.</div></body></html>"
        result1 = cleansing_html(text1)
        self.assertEqual("테스트용html오늘은 바나나가 맛있어보여요.",  result1)

        text2 = "html이 일부만 있을 수도 있어요.<TD style='FONT-SIZE:10pt;TEXT-DECORATION:none;HEIGHT:16.5pt;"
        result2 = cleansing_html(text2)
        self.assertEqual("html이 일부만 있을 수도 있어요.", result2)


    def test_transform_case(self):
        text = "AbkAKDGKdfsopAGK"
        self.assertEqual(
            transform_lower_case(text),
            "abkakdgkdfsopagk"
        )


    def test_cleansing_datetime(self):
        text1 = "2020년 11월 27일"
        self.assertEqual(
            cleansing_datetime(text1),
            ""
        )

        text2 = "오전 6:34에 발생한 오류"
        self.assertEqual(
            cleansing_datetime(text2),
            "에 발생한 오류"
        )

        text3 = "20년 11월 27일 금요일"
        self.assertEqual(
            cleansing_datetime(text3),
            ""
        )


    def test_celansing_query(self):
        text = "select * from domain where userid=user;"
        self.assertEqual(
            cleansing_query(text),
            ""
        )


    def test_cleansing_url(self):
        text = "http://mskgox.com 에서 확인 가능합니다."
        self.assertEqual(
            cleansing_url(text),
            "에서 확인 가능합니다."
        )


    def test_cleansing_email(self):
        text = "문의는 question@question.co.kr으로 해주세요."
        self.assertEqual(
            cleansing_email(text),
            "문의는  으로 해주세요."
        )


    def test_cleansing_phone_number(self):
        text = "사무실 번호는 02-1245-4452이고, 모바일은 010-3452-3742입니다."
        self.assertEqual(
            cleansing_phone_number(text),
            "사무실 번호는  이고, 모바일은  입니다."
        )


    def test_cleansing_ip(self):
        text = "접속 ip 정보는 10.10.20.26이고 id는"
        self.assertEqual(
            cleansing_ip(text),
            "접속 ip 정보는  이고 id는"
        )


    def test_cleansing_many_whitespace(self):
        text = "오늘   발표  주제는  보시는 바와  같습니다."
        self.assertEqual(
            cleansing_many_whitespace(text),
            "오늘 발표 주제는 보시는 바와 같습니다."
        )


    def test_cleansing_characters(self):
        text = "와!>< 오늘 그 영화 봤어요?!! 정말 감동적이었어요ㅜㅜㅜ"
        self.assertEqual(
            cleansing_characters(text, []),
            "와!   오늘 그 영화 봤어요?!! 정말 감동적이었어요"
        )
        self.assertEqual(
            cleansing_characters(text, ["<", ">"]),
            "와!>< 오늘 그 영화 봤어요?!! 정말 감동적이었어요"
        )


    def test_get_sent_list(self):
        preprocess = Preprocess()
        text = "이순신은 조선 중기의 무신이었다. 본관은 덕수, 자는 여해, 시호는 충무였으며, 한성 출신이었다."
        self.assertEqual(
            get_sent_list(preprocess.tokenizer, text),
            ["이순신은 조선 중기의 무신이었다.",
            "본관은 덕수, 자는 여해, 시호는 충무였으며, 한성 출신이었다."]
        )


    def test_check_stop_sent(self):
        preprocess = Preprocess()
        self.assertEqual(
            check_stop_sent(
                preprocess.tokenizer, "이순신은 조선 중기의 무신이었다.",
                ["이순신은 조선의 무신이었다.",
                "본관은 덕수, 자는 여해, 시호는 충무였으며, 한성 출신이었다."],
                0.55
            ), True
        )


    def test_check_stop_head(self):
        self.assertEqual(
            check_stop_head(
                "※공지사항 : 이번주에는 다과회가 있습니다.",
                ["※공지사항"]
            ), True
        )


if __name__ == "__main__":
    unittest.main()
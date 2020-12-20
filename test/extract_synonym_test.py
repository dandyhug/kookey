#-*-coding:utf-8-*-

import unittest
from kookey.synonym_util.model import Embedding
from kookey.synonym_util.model import Tuning
from kookey.extract_synonym import SynonymExtractor


sentences = ["사과는 과일이다.",
    "토마토는 과일이 아니다.",
    "딸기는 과일이다."]

eval_data = [("딸기", "토마토", 1), ("토마토", "사과", 1)]
base_words = ["딸기"]
compare_words = ["토마토", "사과"]

train_data = [("사과", "딸기"), ("사과", "토마토")]
train_label = [1, 0]
test_data = [("딸기", "토마토")]
test_label = [0]


class ExtractSynonymTest(unittest.TestCase):

    def test_synonym_extractor_just_embedding(self):
        synonym_extractor = SynonymExtractor(em_threshold=0)
        candidate = synonym_extractor.get_keyword_candidate(sentences, base_words, compare_words)
        print(candidate)
        self.assertTrue(candidate[0][2] > 0)


    def test_embedding(self):
        embedding = Embedding(threshold=0)
        embedding.build_training_data(sentences)
        embedding.train()

        eval_score = embedding.eval(eval_data)
        self.assertEqual(50.0, eval_score)

        embedding.extract(base_words, compare_words)
        self.assertTrue(embedding.candidate[0][2] > 0)


    def test_synonym_extractor_until_tuning(self):
        synonym_extractor = SynonymExtractor(tuning_mode=True, tune_threshold=0)
        candidate = synonym_extractor.get_keyword_candidate(
            sentences, base_words, compare_words, train_data, train_label, test_data, test_label)
        print(candidate)
        self.assertTrue(candidate[0][2] > 0)


    def test_tuning(self):
        
        embedding = Embedding()
        embedding.build_training_data(sentences)
        embedding.train()

        tuning = Tuning(embedding.model, mode="bi_lstm")
        tuning.build_training_data(train_data, train_label, test_data, test_label)
        tuning.train()

        eval_score = tuning.eval(eval_data)
        self.assertEqual(100.0, eval_score)

        tuning.extract(base_words, compare_words)
        self.assertEqual([], tuning.candidate)


if __name__ == "__main__":
    unittest.main()


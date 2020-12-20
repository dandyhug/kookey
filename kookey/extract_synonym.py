#-*-coding:utf-8-*-

from kookey.synonym_util.model import Embedding
from kookey.synonym_util.model import Tuning

class SynonymExtractor:

    def __init__(self, seed=42, tokenizer="kkma", jamo=True, 
        skip_gram=1, learning_rate=0.05, dim_size=100, window=5, 
        min_count=5, min_n=3, max_n=6, threshold=0.85, iter=5, em_threshold=0.85,
        tuning_mode=False, train_mode="pooling_and_cos", epochs=10, tune_threshold=0.85):
        
        self.embedding = Embedding(seed, tokenizer, jamo, skip_gram,
            learning_rate, dim_size, window, min_count, min_n, max_n, 
            iter, em_threshold)

        self.tuning_mode = tuning_mode
        if tuning_mode:
            self.tuning = Tuning(self.embedding.model, jamo,
                train_mode, seed, epochs, tune_threshold)


    def get_keyword_candidate(self, sentences, base_words, compare_words,
        train_data=None, train_label=None, test_data=None, test_label=None):
        
        self.embedding.build_training_data(sentences)
        self.embedding.train()

        if self.tuning_mode:
            self.tuning.embedding_model = self.embedding.model
            self.tuning.get_embedding(self.tuning.embedding_model)

            self.tuning.build_training_data(train_data, train_label, test_data, test_label)
            self.tuning.train()

            self.tuning.extract(base_words, compare_words)

            return self.tuning.candidate

        else:
            self.embedding.extract(base_words, compare_words)
            return self.embedding.candidate

        



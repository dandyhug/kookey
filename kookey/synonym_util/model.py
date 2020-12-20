#-*-coding:utf-8-*-

from gensim.models import fasttext
from abc import abstractmethod
import numpy as np
import tensorflow as tf
from tensorflow import keras
from kookey.synonym_util import transform_data
from kookey.tokenizer import Tokenizer


class Model:

    def __init__(self):
        self.model = None
        self.candidate = []


    @abstractmethod
    def train(self):
        pass


    @abstractmethod
    def extract(self, basic_words, compared_words):
        pass


    @abstractmethod
    def save_model(self, path="model.bin"):
        pass


    def save_synonym_candidate(self, path="synonym_candidate.tsv"):
        self.check_no_candidiate()

        with open(path, "w", encoding="utf-8") as f:
            f.write("word1\tword2\tsimilarity\n")
            for word1, word2, similarity in self.candidate:
                f.write(word1 + "\t" + word2 + "\t" + str(round(similarity, 4)) + "\n")
    
    
    @abstractmethod
    def check_no_data(self):
        pass


    def check_no_model(self):
        if not self.model:
            raise RuntimeError("There are no model to save. You should call train(...) first.")


    def check_no_candidiate(self):
        if not self.candidate:
            raise RuntimeError("There are no candidate to save. You should call extract(...) first.")


class Embedding(Model):

    def __init__(self, seed=42, tokenizer="kkma", jamo=True, skip_gram=1, learning_rate=0.05, 
        dim_size=100, window=5, min_count=5, min_n=3, max_n=6, iter=5, threshold=0.85):
        super(Embedding, self).__init__()

        self.tokenizer = Tokenizer(tokenizer).tokenizer
        self.jamo = jamo
        self.sentences = []

        self.seed = seed
        self.sg = skip_gram
        self.alpha = learning_rate
        self.size = dim_size
        self.window = window
        self.min_count = min_count
        self.min_n = min_n
        self.max_n = max_n
        self.iter = iter

        self.threshold = threshold
        self.eval_detail = {}
        self.candidate = []

    
    def build_training_data(self, sentences):
        self.sentences = transform_data.trans_sents_for_embedding(
                sentences, self.tokenizer, self.jamo)


    def save_training_data(self, path="train_sentences.txt"):
        self.check_no_data()

        with open(path, "w", encoding="utf-8") as f:
            for sent in self.sentences:
                f.write(sent + "\n")

    def train(self):
        self.check_no_data()

        pre_trained_model = fasttext.FastText(seed=self.seed, sg=self.sg, 
            alpha=self.alpha, size=self.size, window=self.window, 
            min_count=self.min_count, min_n=self.min_n, max_n=self.max_n, iter=self.iter)
        pre_trained_model.build_vocab(sentences=self.sentences)
        pre_trained_model.train(sentences=self.sentences, 
            total_examples=pre_trained_model.corpus_count, epochs=5)

        self.model = pre_trained_model


    def check_no_data(self):
        if not self.sentences:
            raise RuntimeError("There are no training data. You should call build_traing_data(...) first.")


    def save_model(self, path=""):
        self.check_no_model() 
        fasttext.save_facebook_model(self.model, path)


    def eval(self, test_data):
        self.check_no_model()

        word1, word2 = [], []
        for w1, w2, _ in test_data:
            word1.append(w1)
            word2.append(w2)

        vec1, oov1 = self.get_vector(word1)
        vec2, oov2 = self.get_vector(word2)
        oov = oov1 + oov2

        cos_sim = self.cosine_similarity(vec1, vec2.T)     

        right_count = 0
        for i in range(len(test_data)):
            if i not in oov:
                if cos_sim[i][i] >= self.threshold and test_data[i][2] == 1:
                    right_count += 1
                elif cos_sim[i][i] < self.threshold and test_data[i][2] == 0:
                    right_count += 1
                self.eval_detail[test_data[i]] = cos_sim[i][i]
            else:
                self.eval_detail[test_data[i]] = "oov"

        return right_count / (len(test_data) - len(oov)) * 100


    def extract(self, basic_words, compared_words):
        candidate = []

        vec2, oov2 = self.get_vector(compared_words)

        for word1 in basic_words:

            vec1, oov1 = self.get_vector([word1])

            cos_sim = self.cosine_similarity(vec1, vec2.T)[0]

            for i in range(len(cos_sim)):
                if not oov1 and i not in oov2:
                    if cos_sim[i] >= self.threshold:
                        candidate.append((word1, compared_words[i], cos_sim[i]))

        self.candidate = candidate


    def get_vector(self, words):
        vec = []
        oov = []

        for i in range(len(words)):
            try:
                if self.jamo:
                    vec.append(self.model.wv[transform_data.sent_to_jamo(words[i])])
                else:
                    vec.append(self.model.wv[words[i]])
            except KeyError:
                oov.append(i)
                vec.append(np.zeros(self.size))
                raise Warning("OOV : " + words[i])

        vec = np.array(vec)

        return vec, oov


    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class Tuning(Model):

    def __init__(self, embedding_model, jamo=True,
        mode="pooling_and_cos", seed=42, epochs=10, threshold=0.85):
        super(Tuning, self).__init__()

        np.random.seed(seed)
        tf.random.set_seed(seed)

        self.jamo = jamo

        self.embedding_model = embedding_model
        self.get_embedding(embedding_model)

        self.train_data = []
        self.train_label = []
        self.test_data = []
        self.test_label = []
        self.max_length = -1

        self.mode = mode
        self.seed = seed
        self.epochs = epochs

        self.threshold = threshold
        self.eval_detail = {}
        self.candidate = []


    def get_embedding(self, embedding_model):
        if embedding_model:
            embedding_vocab = list(embedding_model.wv.vocab.keys())
            embedding_word_index, embedding_index_word = {}, {}

            for i, word in enumerate(embedding_vocab):
                embedding_word_index[word], embedding_index_word[i] = i, word         
            last = len(embedding_word_index)
            embedding_word_index["<UNK>"], embedding_index_word[last] = last, "<UNK>"
            embedding_word_index["<PAD>"], embedding_index_word[last+1] = last + 1, "<PAD>"

            embedding = np.random.random((len(embedding_word_index) + 1,
                                embedding_model.vector_size))

            for i, word in enumerate(embedding_word_index.keys()):
                embedding[i] = embedding_model.wv[word]

            self.embedding_vocab = embedding_vocab
            self.embedding_word_index = embedding_word_index
            self.embedding_index_word = embedding_index_word
            self.embedding_weigth = embedding

    
    def build_training_data(self, train_data, train_label, test_data, test_label):
        self.train_data, self.test_data, self.max_length = transform_data.trans_words_for_tuning(
            train_data, test_data, self.embedding_word_index, self.jamo)
        self.train_label = train_label
        self.test_label = test_label


    def train(self):
        self.check_no_data()

        if self.mode == "pooling_and_cos":
            self.train_with_pooling_and_cos()
        elif self.mode == "bi_lstm":
            self.train_with_bi_lstm()
        else:
            raise RuntimeError("training mode must be one of pooling_and_cos, bi_lstm")


    def check_no_data(self):
        if not self.train_data or not self.train_label or not self.test_data or not self.test_label:
            raise RuntimeError("There are no training data. You should call build_traing_data(...) first.")

        if (not (len(self.train_data[0]) == len(self.train_data[1]) == len(self.train_label)) 
            or not (len(self.test_data[0]) == len(self.test_data[1]) == len(self.test_label))):
            raise RuntimeError("Word pair data and label must have same length.")


    def train_with_pooling_and_cos(self):
        input1 = keras.layers.Input(shape=(None,))
        input2 = keras.layers.Input(shape=(None,))

        embedding_layers = keras.layers.Embedding(
            self.embedding_weigth.shape[0], self.embedding_weigth.shape[1],
            weights=[self.embedding_weigth], trainable=True)
        embedding_output1 = embedding_layers(input1)
        embedding_output2 = embedding_layers(input2)

        pooling_layer = keras.layers.GlobalAveragePooling1D()
        pooling_output1 = pooling_layer(embedding_output1)
        pooling_output2 = pooling_layer(embedding_output2)

        cosine_output = keras.layers.Dot(axes=1, normalize=True)(
            [pooling_output1, pooling_output2])

        output = keras.layers.Dense(1, activation='sigmoid')(cosine_output)

        tuning_model = keras.Model(inputs=[input1, input2], outputs=output)
        tuning_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        tuning_model.fit(x=[np.array(self.train_data[0]), np.array(self.train_data[1])], y=np.array(self.train_label),
            validation_data=([np.array(self.test_data[0]), np.array(self.test_data[1])], np.array(self.test_label)),
            epochs=self.epochs)

        self.model = tuning_model


    def train_with_bi_lstm(self):
        input1 = keras.layers.Input(shape=(None,))
        input2 = keras.layers.Input(shape=(None,))

        embedding_layers = keras.layers.Embedding(
            self.embedding_weigth.shape[0], self.embedding_weigth.shape[1],
            weights=[self.embedding_weigth], trainable=True)
        embedding_output1 = embedding_layers(input1)
        embedding_output2 = embedding_layers(input2)

        concat_layer = keras.layers.concatenate([embedding_output1, embedding_output2])

        bi_lstm_layer = keras.layers.Bidirectional(keras.layers.LSTM(
            100, dropout=0.3))(concat_layer)

        output = keras.layers.Dense(1, activation='sigmoid')(bi_lstm_layer)

        tuning_model = keras.Model(inputs=[input1, input2], outputs=output)
        tuning_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        tuning_model.fit(x=[np.array(self.train_data[0]), np.array(self.train_data[1])], y=np.array(self.train_label),
            validation_data=([np.array(self.test_data[0]), np.array(self.test_data[1])], np.array(self.test_label)),
            epochs=self.epochs)

        self.model = tuning_model


    def save_model(self, path="model"):
        self.check_no_model()
        self.model.save(path)


    def eval(self, test_data):
        self.check_no_model()

        word1, word2 = [], []
        for w1, w2, _ in test_data:
            word1.append(w1)
            word2.append(w2)

        vec1 = self.get_vector(word1)
        vec2 = self.get_vector(word2)

        result = self.model.predict([np.array(vec1), np.array(vec2)])
        
        right_count = 0
        for i in range(len(test_data)):
            if result[i][0] >= self.threshold:
                right_count += 1
            elif result[i][0] < self.threshold:
                right_count += 1
            self.eval_detail[test_data[i]] = result[i][0]

        return right_count / len(test_data) * 100


    def extract(self, basic_words, compared_words):
        candidate = []

        vec2 = self.get_vector(compared_words)

        for word1 in basic_words:
            vec1 = self.get_vector(word1)

            result = self.model.predict([np.array(vec1), np.array(vec2)])

            for i in range(len(result)):
                if result[i][0] >= self.threshold:
                    candidate.append((word1, compared_words[i], result[i][0]))

        self.candidate = candidate


    def get_vector(self, words):
        vec = []

        for word in words:
            encoded_word = transform_data.get_encoded_word(
                word, self.embedding_word_index, self.jamo)
            vec.append(transform_data.get_padded_word(
                encoded_word, self.embedding_word_index, self.max_length))

        return vec


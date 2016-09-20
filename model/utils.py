import numpy as np


class Utils:
    @staticmethod
    def build_text_image(word2vec, words, embedding_size=300, padding=0):
        word_vectors = []

        if padding > 0:
            words = words[:padding]

        for w in words:
            w_vec = word2vec.get_word_vector(w)
            if w_vec is None:
                word_vectors.append(np.array([0.] * embedding_size))
            else:
                word_vectors.append(w_vec)

        if padding > 0 and len(word_vectors) < padding:
            word_vectors.extend([np.array([0.0] * 300)] * (padding - len(word_vectors)))

        return word_vectors

    @staticmethod
    def mrr(y_true, y_pred):
        return None

    @staticmethod
    def map(y_true, y_pred):
        return None

    @staticmethod
    def precision_recall_f1(y_true, y_pred):
        return None

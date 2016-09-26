import numpy as np


class ModelUtils:
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

        return [word_vectors, ]

    @staticmethod
    def mrr(q_list, y_true, y_pred):
        assert sum(len(i) for i in q_list) == len(y_pred)

        index_begin = 0
        mrr = 0.0

        for q in q_list:
            index_end = index_begin + len(q)
            predictions_slice = y_pred[index_begin:index_end].flatten().tolist()

            # Pair label-prediction and sort by prediction descending order
            xx = zip(q, predictions_slice)
            xx = sorted(xx, key=lambda tup: tup[1], reverse=True)

            for idx, x in enumerate(xx):
                if x[0] == 1:
                    mrr += float(1) / (idx + 1)
                    break

            index_begin = index_end

        mrr = float(mrr) / len(q_list) * 100
        return mrr

    @staticmethod
    def map(q_list, y_true, y_pred):
        avg_prec = 0
        index_begin = 0

        for q in q_list:
            index_end = index_begin + len(q)
            predictions_slice = y_pred[index_begin:index_end].flatten().tolist()

            correct_answers = len([1 for x in q if x == 1])

            xx = zip(q, predictions_slice)
            xx = sorted(xx, key=lambda tup: tup[1], reverse=True)

            correct = 0
            wrong = 0
            av_prec_i = 0

            for idx, x in enumerate(xx):
                if x[0] == 1:
                    correct += 1
                else:
                    wrong += 1

                if x[0] == 1:
                    av_prec_i += float(correct) / (correct + wrong)

                if correct == correct_answers:
                    break

            if correct_answers > 0:
                avg_prec += av_prec_i / correct_answers

            index_begin = index_end

        omap = float(avg_prec) / len(q_list) * 100
        return omap

    @staticmethod
    def precision_recall_f1(y_true, y_pred):
        return None

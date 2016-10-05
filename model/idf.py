from collections import defaultdict
import numpy as np
import cPickle as pickle


class IDF:
    def __init__(self, stopwords):
        self.idf = defaultdict(float)
        self.n = 0
        self.stopwords = stopwords

    def fit(self, samples):
        for s in samples:
            s_words = set(s.lower().split())

            for word in s_words:
                if word in self.stopwords:
                    continue
                self.idf[word] += 1

            self.n += 1

        for k, v in self.idf.items():
            self.idf[k] = np.log(float(self.n) / v)

    def __getitem__(self, k):
        return self.idf[k]

    def load_model(self, file_path):
        pickle_obj = pickle.load(open(file_path))
        self.idf = pickle_obj[0]
        self.stopwords = pickle_obj[1]

    def save_model(self, file_path):
        pickle.dump([self.idf, self.stopwords], open(file_path, 'w'))
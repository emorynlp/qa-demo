from collections import defaultdict
import numpy as np


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

    def load_model(self, filename):
        pass

    def save_model(self, filename):
        pass
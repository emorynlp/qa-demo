import sys
import numpy as np
from scipy import spatial

reload(sys)
sys.setdefaultencoding('UTF-8')


class Word2Vec:
    def __init__(self, word2vec_filename, vocabulary):
        self.filename = word2vec_filename
        self.vocabulary = vocabulary
        self._load_base_file()
        self._add_unknown_words()

    def _load_base_file(self):
        word_vectors = dict()
        print ("opening file: %s" % self.filename)

        with open(self.filename, "rb") as f:
            header = f.readline()
            vocab_size, layer1_size = map(int, header.split())
            binary_len = np.dtype('float32').itemsize * layer1_size
            print("vocab size: %d, layer1_size: %d" % (vocab_size, layer1_size))

            for line in xrange(vocab_size):
                word = []
                while True:
                    ch = f.read(1)
                    if ch == b' ':
                        word = ''.join(word)
                        break
                    if ch != b'\n':
                        word.append(ch)

                word_vectors[word] = np.fromstring(f.read(binary_len), dtype='float32')

        print("num words already in word2vec: %d" % len(word_vectors))
        print("vocabulary size: %d" % len(self.vocabulary))
        self.word_vectors = word_vectors

    def get_word_vector(self, word):
        try:
            return self.word_vectors[word]
        except KeyError:
            return None

    def _add_unknown_words(self):
        not_present = 0
        for word in self.vocabulary:
            if word not in self.word_vectors:
                self.word_vectors[word] = np.random.uniform(-0.25, 0.25, 300)
                not_present += 1
        print ('randomized words: %d out of %d' % (not_present, len(self.vocabulary)))

    def get_similar_words(self, word, n=5):
        similarity_list = []

        if type(word) is not np.ndarray:
            word = self.word_vectors[word]

        for idx, w in enumerate(self.word_vectors):
            similarity_list.append((w, 1 - spatial.distance.cosine(self.word_vectors[w], word)))

        return (sorted(similarity_list, key=lambda x: x[1], reverse=True))[:n]

    def get_dissimilar_words(self, word, n=5):
        similarity_list = []

        if type(word) is not np.ndarray:
            word = self.word_vectors[word]

        for idx, w in enumerate(self.word_vectors):
            similarity_list.append((w, 1 - spatial.distance.cosine(self.word_vectors[w], word)))

        return (sorted(similarity_list, key=lambda x: x[1]))[:n]

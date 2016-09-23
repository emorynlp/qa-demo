import re


class SentenceFeature:
    def __init__(self, idf, stopwords=None):
        self.idf = idf
        self.stopwords = stopwords

    def extract_features(self, samples):
        f_list = []

        for s in samples:
            f_s = []
            clean_s = self._clean_str(s)
            s1 = self._clean_str(s.split('\t')[0]).split()
            s2 = self._clean_str(s.split('\t')[1]).split()

            f_s.append(self._get_overlapping_words(s1, s2))
            f_s.append(self._get_idf_overlapping_words(s1, s2))
            f_s.append(self._get_sentence_length(s1))
            f_list.append(f_s)

        return f_list

    def _get_overlapping_words(self, s1, s2):
        s1_set, s2_set = set(s1), set(s2)
        count = 0.0

        for word in s1_set:
            if word in s2_set and word not in self.stopwords:
                count += 1.0

        return count

    def _get_idf_overlapping_words(self, s1, s2):
        s1_set, s2_set = set(s1), set(s2)
        score = 0.0

        for word in s1_set:
            if word in s2_set and word not in self.stopwords:
                score += self.idf[word]

        return score

    @staticmethod
    def _get_sentence_length(s):
        return len(s)

    @staticmethod
    def _clean_str(sent):
        string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", sent)
        string = re.sub(r"\s{2,}", " ", string)
        return string.strip().lower()
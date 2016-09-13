import nltk
import re
from elasticsearch import Elasticsearch
from multiprocessing import Process, Queue
import math


class QueryPreprocessor:
    escape_rules = {'+': r'\+',
               '-': r'\-',
               '&': r'\&',
               '|': r'\|',
               '!': r'\!',
               '(': r'\(',
               ')': r'\)',
               '{': r'\{',
               '}': r'\}',
               '[': r'\[',
               '/': r'\/',
               ']': r'\]',
               '^': r'\^',
               '~': r'\~',
               '*': r'\*',
               '?': r'\?',
               ':': r'\:',
               '"': r'\"',
               ';': r'\;',
               ' ': r'\ '}

    def __init__(self):
        self.tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    def preprocess_query(self, query):
        """

        :param query:
        :return:
        """

        # escape \ first
        term = query.replace('\\', r'\\')
        return "".join([nextStr for nextStr in self._escaped_seq(term)])

    def _escaped_seq(self, term):
        """
        Yield the next string based on the
        next character (either this char
        or escaped version
        """

        for char in term:
            if char in self.escape_rules.keys():
                yield self.escape_rules[char]
            else:
                yield char

    def fix_spacing(self, text):
        fixed_text = ""
        old_sentence_split = self.tokenizer.tokenize(text)

        for s in old_sentence_split:
            reg_sentence = re.sub(r'\.(([A-Z]{1}[a-z]{1,}|A ))', r'. \1', s)

            if s != reg_sentence:
                new_sentences_after_split = [x for x in self.tokenizer.tokenize(reg_sentence) if len(x.split(" ")) > 1]
                fixed_text += " ".join(new_sentences_after_split) + " "
            else:
                fixed_text += s + " "

        return fixed_text


class QuestionQueryBuilder:
    def __init__(self):
        self.qp = QueryPreprocessor()

    def _build_query(self, q_entity, fields, top_k):
        di = dict()
        di['question'] = q_entity['question']
        di['article'] = q_entity['article']
        di['section'] = q_entity['section']

        if 'paragraph_id' in q_entity:
            di['paragraph_id'] = q_entity['paragraph_id']

        di['query_body'] = {'query':
            {
                'multi_match': {
                    'query': self.qp.preprocess_query(q_entity['question']),
                    'fields': fields
                }
            },
            'size': top_k
        }

        return di

    def build_query(self, data, fields, top_k):
        if type(data) == list:
            query_list = []
            for d in data:
                query_list.append(self._build_query(d, fields, top_k))

            return query_list
        elif type(data) == dict:
            return self._build_query(data, fields, top_k)
        else:
            raise Exception('Unsupported arg type in build_query: %s' % type(data))


class QuestionQuery:
    def __init__(self, es_server, es_index, es_type):
        self.es_server = es_server
        self.es_index = es_index
        self.es_type = es_type

    def _query_job(self, data, top_k, results_q):
        es = Elasticsearch(hosts=[self.es_server,])
        all_results = []
        for d in data:
            es_results = es.search(index=self.es_index, doc_type=self.es_type, body=d['query_body'])
            s_results = []
            for j in es_results['hits']['hits'][:top_k]:
                di = dict()
                di['article'] = j['_source']['article']
                di['section'] = j['_source']['section']

                if 'paragraph_id' in j['_source']:
                    di['paragraph_id'] = j['_source']['paragraph_id']

                if 'section_id' in j['_source']:
                    di['section_id'] = j['_source']['section_id']

                s_results.append(di)

            all_results.append({'question_entity': d, 'hits': s_results})

        results_q.put(all_results)

    def query_index(self, data, top_k, nprocs=10):
        results_q = Queue()
        procs = []
        chunksize = int(math.ceil(len(data) / float(nprocs)))

        for i in xrange(nprocs):
            p = Process(
                target=self._query_job,
                args=(data[chunksize * i:chunksize * (i + 1)], top_k, results_q))
            procs.append(p)
            p.start()

        results = []
        for i in range(nprocs):
            results.append(results_q.get())

        for p in procs:
            p.join()

        return [item for sublist in results for item in sublist]

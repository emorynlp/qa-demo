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


class QueryExecutor:
    def __init__(self, es_server, es_index, es_type):
        self.es_server = es_server
        self.es_index = es_index
        self.es_type = es_type
        self.es = Elasticsearch(hosts=[self.es_server, ])
        self.qp = QueryPreprocessor()

    def query_index(self, query, fields, top_k):
        results = []

        query_body = {'query':
            {
                'multi_match': {
                    'query': self.qp.preprocess_query(query),
                    'fields': fields
                }
            },
            'size': top_k
        }

        print query_body

        es_results = self.es.search(index=self.es_index, doc_type=self.es_type, body=query_body)
        s_results = []

        for j in es_results['hits']['hits'][:top_k]:
            di = dict()
            print j['_source']
            di['article'] = j['_source']['article']
            di['section'] = j['_source']['section']
            di['text'] = j['_source']['text']
            print j['_source']['text']

            if 'paragraph_id' in j['_source']:
                di['paragraph_id'] = j['_source']['paragraph_id']

            if 'section_id' in j['_source']:
                di['section_id'] = j['_source']['section_id']

            s_results.append(di)

        print len(s_results)
        return s_results

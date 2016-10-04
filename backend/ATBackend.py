from jsonrpc import dispatcher
from es.query import QueryExecutor
from core import BackendServer
from model.cnn import ATCNNModel
# import cPickle as pickle
from model.embedding import Word2Vec
import spacy
import json


class ATBackendServer(BackendServer):
    """
    Backend server for Answer Triggering task.
    Source: <provide a url here>
    """
    es_qe = None
    tokenizer = None
    model = None

    def __init__(self, elasticsearch_host, elasticsearch_index, elasticsearch_type, models):
        settings = json.load(open('config.json'))

        assert type(models) is list

        self.es_host = elasticsearch_host
        self.es_index = elasticsearch_index
        self.es_type = elasticsearch_type
        ATBackendServer.es_qe = QueryExecutor(self.es_host, self.es_index, self.es_type)
        ATBackendServer.cnn_model = ATCNNModel()
        ATBackendServer.cnn_model.load_model(models[0])
        # ATBackendServer.lr_model = pickle.load(models[1])

        # FIXME: provide a vocabulary from training here
        ATBackendServer.embedding = Word2Vec(settings['word2vec_bin_file'], [])
        ATBackendServer.tokenizer = spacy.load('en')
        BackendServer.__init__(self)

    @staticmethod
    @dispatcher.add_method
    def query(string):
        q_tokenized = ' '.join([i.text for i in ATBackendServer.tokenizer(string)])
        es_results = ATBackendServer.es_qe.query_index(string, ['text'], 10)

        for p in es_results:
            p_tokenized = ATBackendServer.tokenizer(p['text'])
            # sentences = [sent.string.strip() for sent in p_tokenized.sents]
            s_tokenized = []

            for s in p_tokenized.sents:
                s_tokenized.append([i.text for i in s])

            # print s_tokenized

        return es_results

    @dispatcher.add_method
    def query_test(self):
        return True

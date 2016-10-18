import json
import cPickle as pickle
import numpy as np
import spacy
from jsonrpc import dispatcher

from core import BackendServer
from es.query import QueryExecutor
from feature.sentence import SentenceFeature
from model.cnn import ATCNNModel
from model.idf import IDF
from model.utils import ModelUtils
from model.embedding import Word2Vec

from pprint import pprint


class ATBackendServer(BackendServer):
    """
    Backend server for Answer Triggering task.
    Source: <provide a url here>
    """

    query_executor = None
    tokenizer = None
    cnn_model = None
    cnn_sentence_size = 40
    lr_model = None
    lr_threshold = None
    embedding = None
    sentence_feature = None

    def __init__(self, elasticsearch_host, elasticsearch_index, elasticsearch_type, models):
        settings = json.load(open('config.json'))

        assert type(models) is list

        ATBackendServer.tokenizer = spacy.load('en')
        ATBackendServer.query_executor = QueryExecutor(elasticsearch_host, elasticsearch_index, elasticsearch_type)
        ATBackendServer.cnn_model = ATCNNModel()
        ATBackendServer.cnn_model.load_model(models[0])
        ATBackendServer.lr_model = pickle.load(open(models[1]))[0]
        ATBackendServer.lr_threshold = pickle.load(open(models[1]))[1]
        ATBackendServer.idf = IDF(None)
        ATBackendServer.idf.load_model(models[2])
        ATBackendServer.sentence_feature = SentenceFeature(ATBackendServer.idf, ATBackendServer.idf.stopwords)
        ATBackendServer.embedding = Word2Vec(None, [])
        ATBackendServer.embedding.load_model(models[3])
        BackendServer.__init__(self)

    @staticmethod
    @dispatcher.add_method
    def query(q_string, results, page):
        q_tokens = [i.text for i in ATBackendServer.tokenizer(q_string)]
        q_tokens_lemma = [i.lemma_ for i in ATBackendServer.tokenizer(q_string)]
        es_results = ATBackendServer.query_executor.query_index(' '.join(q_tokens_lemma), ['lemma_text'], results,
                                                                page*10)
        r_paragraphs = []

        cnn_samples_q, cnn_samples_s, lr_samples = [], [], []

        # Prepare a list of paragraphs to return. Each paragraph is a list of dictionaries with 'sentence' key (string)
        for p in es_results:
            p_tokens = ATBackendServer.tokenizer(p['text'])
            paragraph_list = []

            for s in p_tokens.sents:
                sentence = s.string.rstrip()
                lr_samples.extend(ATBackendServer.sentence_feature.extract_features([' '.join(q_tokens) + '\t'
                                                                                    + ' '.join(i.text for i in s)]))
                paragraph_list.append({'sentence': sentence})
                cnn_samples_q.append(ModelUtils.build_text_image(ATBackendServer.embedding, ' '.join(q_tokens),
                                                                 padding=ATBackendServer.cnn_sentence_size))
                cnn_samples_s.append(ModelUtils.build_text_image(ATBackendServer.embedding, sentence,
                                                                 padding=ATBackendServer.cnn_sentence_size))

            r_paragraphs.append(paragraph_list)

        # Retrieve sentence predictions from CNN and LR models.
        cnn_predictions = ATBackendServer.cnn_model.predict_proba([np.array(cnn_samples_q), np.array(cnn_samples_s)])
        for lr_sample, cnn_pred in zip(lr_samples, cnn_predictions):
            lr_sample.append(cnn_pred[0])

        lr_predictions = ATBackendServer.lr_model.predict_proba(lr_samples)



        pprint(r_paragraphs)

        # Assign key 'is_answer' to each sentence in all paragraphs
        print lr_predictions
        prediction_index = 0
        for paragraphs in r_paragraphs:
            for sen_dict in paragraphs:
                sen_dict['is_answer'] = 1 if lr_predictions[prediction_index][1] > ATBackendServer.lr_threshold else 0
                prediction_index += 1

        return r_paragraphs

    @staticmethod
    @dispatcher.add_method
    def query_test():
        return True

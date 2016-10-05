"""
This script performs a full experiment on provided training data for AT task.
Next, it evaluates the results on test data and shows top-k results.
"""

fixed_seed_num = 1234
import numpy as np
np.random.seed(fixed_seed_num)
import random
random.seed(fixed_seed_num)
import tensorflow
tensorflow.set_random_seed(fixed_seed_num)

import sys
import cPickle as pickle
import datetime
from optparse import OptionParser
import pickle
from keras.models import save_model

reload(sys)
sys.path.insert(0, '../')
sys.setdefaultencoding('utf-8')

from data.reader import TSVReader
from model.embedding import Word2Vec
from model.cnn import ATCNNModel
from model.lr import LRModel
from model.idf import IDF
from model.utils import ModelUtils
from feature.sentence import SentenceFeature


def pipeline(train_file, dev_file, test_file, nb_epoch, batch_size, s_size, nb_filters, top, metric):
    if metric not in ['precision', 'recall', 'f1']:
        raise ValueError('metric should be either "precision", "recall" or "f1"')

    stopwords_file = '../model/short-stopwords.txt'

    vocabulary = set()

    # Collect all lines (single line = single sample) and build a vocabulary
    train_lines, dev_lines, test_lines = [], [], []
    with open(train_file) as f:
        for l in f.readlines():
            train_lines.append(l.strip())
            vocabulary.update(l.split('\t')[0].split())
            vocabulary.update(l.split('\t')[1].split())

    with open(dev_file) as f:
        for l in f.readlines():
            dev_lines.append(l.strip())
            vocabulary.update(l.split('\t')[0].split())
            vocabulary.update(l.split('\t')[1].split())
    with open(test_file) as f:
        for l in f.readlines():
            test_lines.append(l.strip())
            vocabulary.update(l.split('\t')[0].split())
            vocabulary.update(l.split('\t')[1].split())

    # Load stopwords
    stopwords = []
    with open(stopwords_file) as f:
        for l in f.readlines():
            stopwords.append(l.strip())

    # Prepare question entities (single question with its sentences)
    r = TSVReader()
    train_qset = r.parse_file(train_file)
    dev_qset = r.parse_file(dev_file)
    test_qset = r.parse_file(test_file)

    train_samples_cnn, train_labels_cnn = [], []
    dev_samples_cnn, dev_labels_cnn = [], []
    test_samples_cnn, test_labels_cnn = [], []

    train_questions = [[i['question']]*len(i['sentences']) for i in train_qset]
    train_questions = [i for sublist in train_questions for i in sublist]
    dev_questions = [[i['question']]*len(i['sentences']) for i in dev_qset]
    dev_questions = [i for sublist in dev_questions for i in sublist]
    test_questions = [[i['question']]*len(i['sentences']) for i in test_qset]
    test_questions = [i for sublist in test_questions for i in sublist]

    idf = IDF(stopwords)
    idf.fit(train_questions + dev_questions + test_questions)
    idf.save_model('at_idf.model')

    # Prepare features (word overlapping etc for LR)
    sf = SentenceFeature(idf, stopwords)
    train_samples_lr = sf.extract_features(train_lines)
    train_labels_lr = [i for sublist in train_qset for i in sublist['labels']]

    dev_samples_lr = sf.extract_features(dev_lines)
    dev_labels_lr = [i for sublist in dev_qset for i in sublist['labels']]

    test_samples_lr = sf.extract_features(test_lines)
    test_labels_lr = [i for sublist in test_qset for i in sublist['labels']]

    train_labels_grouped = []
    for i in train_qset:
        train_labels_grouped.append(i['labels'])

    dev_labels_grouped = []
    for i in dev_qset:
        dev_labels_grouped.append(i['labels'])

    test_labels_grouped = []
    for i in test_qset:
        test_labels_grouped.append(i['labels'])

    w = Word2Vec('/mnt/ainos-research/tjurczyk/GoogleNews-vectors-negative300.bin', vocabulary)

    train_samples_cnn_q = []
    train_samples_cnn_s = []
    for q in train_qset:
        q_text= q['question']
        q_words = q_text.split(' ')

        for s, l in zip(q['sentences'], q['labels']):
            s_words = s.split(' ')
            train_labels_cnn.append(l)
            train_samples_cnn_q.append(ModelUtils.build_text_image(w, q_words, padding=s_size))
            train_samples_cnn_s.append(ModelUtils.build_text_image(w, s_words, padding=s_size))

    train_samples_cnn = [np.array(train_samples_cnn_q), np.array(train_samples_cnn_s)]

    dev_samples_cnn_q = []
    dev_samples_cnn_s = []
    for q in dev_qset:
        q_text = q['question']
        q_words = q_text.split(' ')

        for s, l in zip(q['sentences'], q['labels']):
            s_words = s.split(' ')
            dev_labels_cnn.append(l)
            dev_samples_cnn_q.append(ModelUtils.build_text_image(w, q_words, padding=s_size))
            dev_samples_cnn_s.append(ModelUtils.build_text_image(w, s_words, padding=s_size))

    dev_samples_cnn = [np.array(dev_samples_cnn_q), np.array(dev_samples_cnn_s)]

    test_samples_cnn_q = []
    test_samples_cnn_s = []
    for q in test_qset:
        q_text = q['question']
        q_words = q_text.split(' ')

        for s, l in zip(q['sentences'], q['labels']):
            s_words = s.split(' ')
            test_labels_cnn.append(l)
            test_samples_cnn_q.append(ModelUtils.build_text_image(w, q_words, padding=s_size))
            test_samples_cnn_s.append(ModelUtils.build_text_image(w, s_words, padding=s_size))

    test_samples_cnn = [np.array(test_samples_cnn_q), np.array(test_samples_cnn_s)]

    cnn = ATCNNModel(nb_row=s_size, nb_filters=nb_filters)

    results = []

    for i in xrange(nb_epoch):
        # One iteration is a single epoch run of NN and dev test on LR
        cnn.fit(train_samples_cnn, train_labels_cnn, dev_samples_cnn, dev_labels_cnn,
                q_list=dev_labels_grouped,
                nb_epoch=1, batch_size=batch_size)

        cnn.save_model('at_cnnmodel_epoch_' + str(i) + '.model')

        train_cnn_preds = cnn.predict_proba(train_samples_cnn)
        dev_cnn_preds = cnn.predict_proba(dev_samples_cnn)
        test_cnn_preds = cnn.predict_proba(test_samples_cnn)

        lr = LRModel()
        train_lr_merged_samples = []
        dev_lr_merged_samples = []
        test_lr_merged_samples = []

        for cnn_s, lr_s in zip(train_cnn_preds, train_samples_lr):
            sample = lr_s[:]
            sample.append(cnn_s[0])
            train_lr_merged_samples.append(sample)
        for cnn_s, lr_s in zip(dev_cnn_preds, dev_samples_lr):
            sample = lr_s[:]
            sample.append(cnn_s[0])
            dev_lr_merged_samples.append(sample)
        for cnn_s, lr_s in zip(test_cnn_preds, test_samples_lr):
            sample = lr_s[:]
            sample.append(cnn_s[0])
            test_lr_merged_samples.append(sample)

        lr.fit(train_lr_merged_samples, train_labels_lr)
        y_pred_dev = lr.model.predict_proba(dev_lr_merged_samples)
        y_pred_dev = np.array([j[-1] for j in y_pred_dev])
        y_pred_test = lr.model.predict_proba(test_lr_merged_samples)
        y_pred_test = np.array([j[-1] for j in y_pred_test])

        dev_e_results = ModelUtils.precision_recall_f1(dev_labels_grouped, dev_labels_lr, y_pred_dev)
        test_e_results = ModelUtils.precision_recall_f1(test_labels_grouped, test_labels_lr, y_pred_test)

        if metric == 'precision':
            sorted_dev = sorted(dev_e_results, key=lambda res: res[2], reverse=True)
        elif metric == 'recall':
            sorted_dev = sorted(dev_e_results, key=lambda res: res[3], reverse=True)
        else:
            sorted_dev = sorted(dev_e_results, key=lambda res: res[4], reverse=True)

        pickle.dump((lr, sorted_dev[0][1]), open('at_lrmodel_epoch_' + str(i) + '.model', 'w'))

        for dev_i, test_i in zip(dev_e_results, test_e_results):
            results .append(('epoch %d, thre: %.2f, '
                             'dev prec: %.2f, rec: %.2f, f1: %.2f, '
                             'test prec: %.2f rec: %.2f f1: %.2f' %
                             (i, dev_i[1], dev_i[2], dev_i[3], dev_i[4], test_i[2], test_i[3], test_i[4]),
                             dev_i[1], dev_i[2], dev_i[3], dev_i[4], test_i[2], test_i[3], test_i[4]))

    if metric == 'precision':
        sorted_results = sorted(results, key=lambda res: res[2], reverse=True)
    elif metric == 'recall':
        sorted_results = sorted(results, key=lambda res: res[3], reverse=True)
    else:
        sorted_results = sorted(results, key=lambda res: res[4], reverse=True)

    for i in sorted_results[:top]:
        print 'LR, %s' % i[0]

    conf_dict = {'train_file': train_file,
                 'dev_file': dev_file,
                 'test_file': test_file,
                 'nb_epoch': nb_epoch,
                 'batch_size': batch_size,
                 's_size': s_size,
                 'nb_filters': nb_filters,
                 'metric': metric}
    filename = __file__.rstrip('.py') + '_' + datetime.datetime.now().strftime("%Y_%m_%d__%H_%M") + '_report.pickle'

    pickle.dump((conf_dict, results, sorted_results), open(filename, 'wb'), protocol=2)


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option('--train',
                      action='store',
                      dest='train_file',
                      default=None,
                      help="tsv format for training")
    parser.add_option('--dev',
                      action='store',
                      dest='dev_file',
                      default=None,
                      help="tsv format for validation")
    parser.add_option('--test',
                      action='store',
                      dest='test_file',
                      default=None,
                      help="tsv format for testing")

    parser.add_option('--sentence_size',
                      action='store',
                      dest='sentence_size',
                      default=40,
                      help="size of padded sentence (q and a) for NN model")

    parser.add_option('--nb_filters',
                      action='store',
                      dest='nb_filters',
                      default=40,
                      help="number of convolutional filters to use in NN")

    parser.add_option('--nb_epoch',
                      action='store',
                      dest='nb_epoch',
                      default=10,
                      help="number of epochs to run the experiment")

    parser.add_option('--batch_size',
                      action='store',
                      dest='batch_size',
                      default=32,
                      help="batch size for training NN")

    parser.add_option('--top',
                      action='store',
                      dest='top_results',
                      default=5,
                      help="how many top results to store. all results are stored in pickle file after")

    parser.add_option('--metric',
                      action='store',
                      dest='metric',
                      default='map',
                      help="how many top results to store. all results are stored in pickle file after")
    (options, args) = parser.parse_args()

    if not options.train_file or not options.dev_file or not options.test_file:
        raise ValueError('Pass all files: train, dev and test.')

    pipeline(options.train_file, options.dev_file, options.test_file,
             int(options.nb_epoch), int(options.batch_size),
             int(options.sentence_size), int(options.nb_filters),
             int(options.top_results), options.metric)

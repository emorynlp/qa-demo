from data.reader import TSVReader
from model.embedding import Word2Vec
from model.cnn import ASSCNNModel
from model.lr import LRModel
from model.idf import IDF
from feature.sentence import SentenceFeature
from model.utils import ModelUtils
import numpy as np

if __name__ == '__main__':
    train_file = 'SelQA-ass-train.txt'
    dev_file = 'SelQA-ass-dev.txt'
    test_file = 'SelQA-ass-test.txt'
    stopwords_file = 'model/short-stopwords.txt'

    vocabulary = set()

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

    stopwords = []
    with open(stopwords_file) as f:
        for l in f.readlines():
            stopwords.append(l.strip())

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

    # IDF test
    idf = IDF(stopwords)
    idf.fit(train_questions+dev_questions+test_questions)

    ###########

    # Prepare features of text
    sf = SentenceFeature(idf, stopwords)
    train_samples_lr = sf.extract_features(train_lines)
    train_labels_lr = [i for sublist in train_qset for i in sublist['labels']]

    dev_samples_lr = sf.extract_features(dev_lines)
    dev_labels_lr = [i for sublist in dev_qset for i in sublist['labels']]

    test_samples_lr = sf.extract_features(test_lines)
    test_labels_lr = [i for sublist in test_qset for i in sublist['labels']]

    ###########
    train_labels_grouped = []

    for i in train_qset:
        train_labels_grouped.append(i['labels'])

    dev_labels_grouped = []

    for i in dev_qset:
        dev_labels_grouped.append(i['labels'])

    test_labels_grouped = []
    for i in test_qset:
        test_labels_grouped.append(i['labels'])

    lr = LRModel()
    print 'test only with LR:'

    lr.fit(train_samples_lr, train_labels_lr)

    y_pred = lr.model.predict_proba(test_samples_lr)
    y_pred = np.array([i[-1] for i in y_pred])
    print 'mrr: %.2f' % ModelUtils.mrr(test_labels_grouped, test_labels_lr, y_pred)

    print 'Now trying to train CNN and try it with LR:'

    w = Word2Vec('/mnt/ainos-research/tjurczyk/GoogleNews-vectors-negative300.bin', vocabulary)

    train_samples_cnn_q = []
    train_samples_cnn_s = []
    for q in train_qset:
        q_text = q['question']
        q_words = q_text.split(' ')

        for s, l in zip(q['sentences'], q['labels']):
            s_words = s.split(' ')
            train_labels_cnn.append(l)
            train_samples_cnn_q.append(ModelUtils.build_text_image(w, q_words, padding=40))
            train_samples_cnn_s.append(ModelUtils.build_text_image(w, s_words, padding=40))

    train_samples_cnn = [np.array(train_samples_cnn_q), np.array(train_samples_cnn_s)]

    dev_samples_cnn_q = []
    dev_samples_cnn_s = []
    for q in dev_qset:
        q_text = q['question']
        q_words = q_text.split(' ')

        for s, l in zip(q['sentences'], q['labels']):
            s_words = s.split(' ')
            dev_labels_cnn.append(l)
            dev_samples_cnn_q.append(ModelUtils.build_text_image(w, q_words, padding=40))
            dev_samples_cnn_s.append(ModelUtils.build_text_image(w, s_words, padding=40))

    dev_samples_cnn = [np.array(dev_samples_cnn_q), np.array(dev_samples_cnn_s)]

    test_samples_cnn_q = []
    test_samples_cnn_s = []
    for q in test_qset:
        q_text = q['question']
        q_words = q_text.split(' ')

        for s, l in zip(q['sentences'], q['labels']):
            s_words = s.split(' ')
            test_labels_cnn.append(l)
            test_samples_cnn_q.append(ModelUtils.build_text_image(w, q_words, padding=40))
            test_samples_cnn_s.append(ModelUtils.build_text_image(w, s_words, padding=40))

    test_samples_cnn = [np.array(test_samples_cnn_q), np.array(test_samples_cnn_s)]

    cnn = ASSCNNModel()

    nb_epoch = 3
    results = []

    for i in xrange(nb_epoch):
        cnn.fit(train_samples_cnn, train_labels_cnn, dev_samples_cnn, dev_labels_cnn,
                accuracy_metric=ModelUtils.mrr, q_list=dev_labels_grouped, nb_epoch=1)

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

        dev_mrr = ModelUtils.mrr(dev_labels_grouped, dev_labels_lr, y_pred_dev)
        dev_map = ModelUtils.map(dev_labels_grouped, dev_labels_lr, y_pred_dev)
        test_mrr = ModelUtils.mrr(test_labels_grouped, test_labels_lr, y_pred_test)
        test_map = ModelUtils.map(test_labels_grouped, test_labels_lr, y_pred_test)

        results.append(['epoch %d, dev map: %.2f mrr: %.2f, test map: %.2f mrr: %.2f' %
                       (i, dev_map, dev_mrr, test_map, test_mrr),
                       dev_map,
                       dev_mrr,
                       test_map,
                       test_mrr])

        print '\n\n'
        print y_pred_dev[:5]
        print 'dev mrr: %.2f' % dev_mrr

    sorted_results = sorted(results, key=lambda res: res[1], reverse=True)  # according to dev map
    for r in sorted_results[:5]:
        print 'LR, %s' % r[0]

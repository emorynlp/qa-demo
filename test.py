from data.reader import TSVReader
from model.utils import Utils
from model.embedding import Word2Vec
from model.cnn import CNNModel

if __name__ == '__main__':
    r = TSVReader()
    train_qset = r.parse_file('SelQA-ass-train.txt')
    dev_qset = r.parse_file('SelQA-ass-dev.txt')

    train_samples, train_labels = [], []
    dev_samples, dev_labels = [], []
    w = Word2Vec('/Volumes/Transcend 1/Downloads/GoogleNews-vectors-negative300.bin')

    for q in train_qset:
        q_text= q['question']
        q_words = q_text.split(' ')

        for s, l in zip(q['sentences'], q['labels']):
            s_words = s.split(' ')
            train_labels.append(l)

            image = Utils.build_text_image(w, q_words, padding=40)
            image.extend(Utils.build_text_image(w, s_words, padding=40))
            train_samples.append([image, ])

    for q in dev_qset:
        q_text= q['question']
        q_words = q_text.split(' ')

        for s, l in zip(q['sentences'], q['labels']):
            s_words = s.split(' ')
            dev_labels.append(l)

            image = Utils.build_text_image(w, q_words, padding=40)
            image.extend(Utils.build_text_image(w, s_words, padding=40))
            dev_samples.append([image, ])

    print len(train_samples)
    print len(train_samples[0])
    print len(train_samples[0][0])

    cnn = CNNModel()
    cnn.fit(train_samples, train_labels, dev_samples, dev_labels)

import logging
import os
from keras.layers.convolutional import *
from keras.layers.core import *
from keras.models import Sequential
from keras.layers.convolutional import MaxPooling2D
from sklearn.metrics import accuracy_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CNNModel:
    def __init__(self, nb_row=80, nb_filters=100, embedding=300):
        self.model = Sequential()
        self.model.add(Convolution2D(nb_filters, 2, embedding, input_shape=(1, nb_row, embedding)))
        self.model.add(Activation('tanh'))

        self.model.add(MaxPooling2D(pool_size=(nb_row/2, 1)))

        self.model.add(Flatten())
        self.model.add(Dense(1))

        self.model.add(Activation('sigmoid'))
        self.model.compile(loss='binary_crossentropy', optimizer='Adagrad')

    def fit(self, x_train, y_train, x_dev, y_dev, nb_epoch=10, batch_size=32):
        best_accuracy = 0.0
        best_accuracy_index = 0

        for e in range(nb_epoch):
            logger.info("Epoch %d" % e)

            self.model.fit(x_train, y_train, batch_size=batch_size, nb_epoch=1)

            self.model.save_weights(os.path.dirname(os.path.realpath(__file__)) + '/cnn1_model_' +
                                    str(e) + '.tmp.h5', overwrite=True)

            current_accuracy = self.score(x_dev, y_dev)
            if current_accuracy > best_accuracy:
                best_accuracy = current_accuracy
                best_accuracy_index = e

        logger.info('\nBest accuracy on dev of: %.4f achieved on epoch %d' % (best_accuracy, best_accuracy_index))

        os.rename(os.path.dirname(os.path.realpath(__file__)) + '/cnn1_model_' + str(best_accuracy_index) + '.tmp.h5',
                  os.path.dirname(os.path.realpath(__file__)) + '/cnn1_model.h5')

        for _ in os.listdir(os.path.dirname(os.path.realpath(__file__))):
            if _.endswith('.tmp.h5'):
                os.remove(_)

        self.model.load_weights('cnn1_model.h5')

    def score(self, x_test, y_test):
        predictions = self.predict(x_test)

        if len(predictions) != len(y_test):
            raise ValueError('x_test is not the same length as y_test')

        return accuracy_score(y_test, predictions)

    def predict(self, x_test):
        return self.model.predict(x_test)

    def predict_classes(self, x_test):
        return self.model.predict_classes(x_test)

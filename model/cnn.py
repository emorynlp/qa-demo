import logging
import os
from keras.layers.convolutional import *
from keras.layers.core import Activation, Reshape, Flatten
from keras.layers.convolutional import MaxPooling2D
from sklearn.metrics import accuracy_score
from keras.layers import Input, merge
from keras.models import Model, save_model, load_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ASSCNNModel:
    def __init__(self, nb_row=40, nb_filters=40, embedding=300):
        q_input = Input(shape=(1, nb_row, embedding))
        a_input = Input(shape=(1, nb_row, embedding))

        convolution = Convolution2D(nb_filters, 2, embedding, input_shape=(1, nb_row, embedding), activation='tanh')
        pool = MaxPooling2D(pool_size=(nb_row-1, 1))

        q_vector = Flatten()(pool(convolution(q_input)))
        q_vector_r = Reshape((1, nb_filters))(q_vector)
        a_vector = Flatten()(pool(convolution(a_input)))
        a_vector_r = Reshape((1, nb_filters))(a_vector)

        merge_layer = merge([q_vector_r, a_vector_r], mode='dot')
        flat = Flatten()(merge_layer)
        activation = Activation('sigmoid')(flat)
        self.model = Model(input=[q_input, a_input], output=activation)
        self.model.compile(loss='binary_crossentropy', optimizer='Adagrad')

    def fit(self, x_train, y_train, x_dev, y_dev, nb_epoch=20, batch_size=32, accuracy_metric=None, q_list=None):
        best_accuracy = 0.0
        best_accuracy_index = 0.0

        for e in range(nb_epoch):
            logger.info("Epoch %d" % e)

            self.model.fit(x_train, y_train, batch_size=batch_size, nb_epoch=1)

            self.model.save_weights(os.path.dirname(os.path.realpath(__file__)) + '/cnn1_model_' +
                                    str(e) + '.tmp.h5', overwrite=True)

            current_accuracy = accuracy_metric(q_list, y_dev, self.predict_proba(x_dev))

            if current_accuracy > best_accuracy:
                best_accuracy = current_accuracy
                best_accuracy_index = e

        logger.info('\nBest accuracy on dev of: %.4f achieved on epoch %d' % (best_accuracy, best_accuracy_index))
        self.model.load_weights(os.path.dirname(os.path.realpath(__file__)) + '/cnn1_model_' +
                                str(best_accuracy_index) + '.tmp.h5')

        for _ in os.listdir(os.path.dirname(os.path.realpath(__file__))):
            if _.endswith('.tmp.h5'):
                print _
                os.remove(os.path.dirname(os.path.realpath(__file__)) + '/' + _)

    def score(self, x_test, y_test):
        predictions = self.predict_classes(x_test)

        if len(predictions) != len(y_test):
            raise ValueError('x_test is not the same length as y_test')

        return accuracy_score(y_test, predictions)

    def predict_proba(self, x_test):
        return self.model.predict(x_test)

    def predict_classes(self, x_test):
        predictions = self.predict_proba(x_test)
        if predictions.shape[-1] > 1:
            return predictions.argmax(axis=-1)
        else:
            return (predictions > 0.5).astype('int32')

    def load_model(self, file_path):
        try:
            self.model = load_model(file_path)
        except IOError:
            raise IOError("Can't load the file")

    def save_model(self, file_path):
        save_model(self.model, file_path)
        logger.info(file_path + '.model')


class ATCNNModel:
    def __init__(self, nb_row=40, nb_filters=40, embedding=300):
        q_input = Input(shape=(1, nb_row, embedding))
        a_input = Input(shape=(1, nb_row, embedding))

        convolution = Convolution2D(nb_filters, 2, embedding, input_shape=(1, nb_row, embedding), activation='tanh')
        pool = MaxPooling2D(pool_size=(nb_row-1, 1))

        q_vector = Flatten()(pool(convolution(q_input)))
        q_vector_r = Reshape((1, nb_filters))(q_vector)
        a_vector = Flatten()(pool(convolution(a_input)))
        a_vector_r = Reshape((1, nb_filters))(a_vector)

        merge_layer = merge([q_vector_r, a_vector_r], mode='dot')
        flat = Flatten()(merge_layer)
        activation = Activation('sigmoid')(flat)
        self.model = Model(input=[q_input, a_input], output=activation)
        self.model.compile(loss='binary_crossentropy', optimizer='Adagrad')

    def fit(self, x_train, y_train, x_dev, y_dev, nb_epoch=20, batch_size=32, accuracy_metric=None, q_list=None):
        best_accuracy = 0.0
        best_accuracy_index = 0.0

        for e in range(nb_epoch):
            logger.info("Epoch %d" % e)

            self.model.fit(x_train, y_train, batch_size=batch_size, nb_epoch=1)

            self.model.save_weights(os.path.dirname(os.path.realpath(__file__)) + '/cnn1_model_' +
                                    str(e) + '.tmp.h5', overwrite=True)

    def score(self, x_test, y_test):
        predictions = self.predict_classes(x_test)

        if len(predictions) != len(y_test):
            raise ValueError('x_test is not the same length as y_test')

        return accuracy_score(y_test, predictions)

    def predict_proba(self, x_test):
        return self.model.predict(x_test)

    def predict_classes(self, x_test):
        predictions = self.predict_proba(x_test)
        if predictions.shape[-1] > 1:
            return predictions.argmax(axis=-1)
        else:
            return (predictions > 0.5).astype('int32')

    def load_model(self, file_path):
        try:
            self.model = load_model(file_path)
        except IOError:
            raise IOError("Can't load the file")

    def save_model(self, file_path):
        save_model(self.model, file_path)
        logger.info(file_path + '.model')

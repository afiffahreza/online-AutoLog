import numpy as np
import pandas as pd
import tensorflow as tf
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from keras.models import Model
from keras.layers import Input, Dense, Dropout
from keras import regularizers, initializers
from sklearn.metrics import confusion_matrix
from time import time
import pickle, logging

mpl.use('TkAgg')
np.random.seed(4999)
tf.random.set_seed(4999)

class MultilayerAutoEncoder():

    def __init__(self, input_dim=None):
        if input_dim is not None:
            self.create_autoencoder(input_dim)
            self.threshold = None
        else:
            self.autoencoder = None
            self.threshold = None

    def create_autoencoder(self, input_dim):
        input_layer = Input(shape=(input_dim,))

        layer = Dense(128, activation='relu',   #128
                        activity_regularizer=regularizers.l1(10e-5),
                        kernel_initializer=initializers.RandomNormal())(input_layer)
        
        layer = Dropout(rate=0.6)(layer)

        layer = Dense(64, activation='tanh',    #64
                      activity_regularizer=regularizers.l1(10e-5),
                      kernel_initializer=initializers.RandomNormal())(layer)
        
        layer = Dropout(rate=0.6)(layer)

        layer = Dense(128, activation='relu',   #128
                      activity_regularizer=regularizers.l1(10e-5),
                      kernel_initializer=initializers.RandomNormal())(layer)
        
        output_layer = Dense(input_dim, activation='relu',
                      activity_regularizer=regularizers.l1(10e-5),
                      kernel_initializer=initializers.RandomNormal())(layer)

        self.autoencoder = Model(inputs=input_layer, outputs=output_layer)
    
    def save_model(self, path):
        model_file = path + "model.h5"
        threshold_file = path + "threshold.pkl"
        self.autoencoder.save(model_file)
        save_threshold(self.threshold, threshold_file)
    
    def load_model(self, path):
        model_file = path + "model.h5"
        threshold_file = path + "threshold.pkl"
        self.autoencoder = tf.keras.models.load_model(model_file)
        self.threshold = load_threshold(threshold_file)
    
    def summary(self, ):
        self.autoencoder.summary()

    def train(self, x, y, percentile=99.99, visualize=False):

        epochs = 50
        batch_size = 2048
        validation_split = 0.2

        logging.info('Start training.')

        self.autoencoder.compile(optimizer='rmsprop',
                                 loss='mean_squared_error')
        start = time()
        history = self.autoencoder.fit(x, y,
                                       epochs=epochs,
                                       batch_size=batch_size,
                                       shuffle=True,
                                       validation_split=validation_split,
                                       verbose=2)
        logging.info(time() - start)

        if visualize:
            plt.plot(history.history['loss'])
            plt.plot(history.history['val_loss'])
            plt.title('model loss')
            plt.ylabel('loss')
            plt.xlabel('epoch')
            plt.legend(['train', 'test'], loc='upper left')
            plt.show()

        x_val = x[x.shape[0]-(int)(x.shape[0]*validation_split):x.shape[0]-1, :]

        logging.info(' + validation_size    : ' +  str(x_val.shape))
        logging.info(x_val)

        val_predictions = self.autoencoder.predict(x_val)
        val_mse = np.mean(np.power(x_val - val_predictions, 2), axis=1)

        threshold = np.percentile(val_mse , percentile)
        logging.info('Current threshold: ')
        logging.info(threshold)

        df_history = pd.DataFrame(history.history)
        self.threshold = threshold

        return df_history, threshold
    
    def predict(self, x, threshold):
        predictions = self.autoencoder.predict(x, verbose=0)
        mse = np.mean(np.power(x - predictions, 2), axis=1)
        y_pred = [1 if e > threshold else 0 for e in mse]
        return y_pred, mse

    def evaluate(self, x_test, y_test, threshold, visualize=False):
        predictions = self.autoencoder.predict(x_test)

        mse=np.mean(np.power(x_test - predictions, 2), axis=1)
        y_test = y_test.reset_index(drop=True)
        df_error = pd.DataFrame({'reconstruction_error' : mse, 'true_class' : y_test})
        logging.info(mse)
        logging.info('y_test***: ')
        logging.info(df_error.to_string())
        logging.info(df_error.describe(include='all'))

        compute(df_error, threshold, visualize=visualize)

def compute(df_error, threshold, visualize=False):
    y_pred = [1 if e > threshold else 0 for e in df_error.reconstruction_error.values]
    conf_matrix = confusion_matrix(df_error.true_class, y_pred)

    tn, fp, fn, tp = conf_matrix.ravel()

    recall = tp / (tp+fn)
    precision = tp / (tp+fp)
    f1 = 2 * ( (precision*recall) / (precision+recall) )
    false_alarm = 1. * fp / (tn + fp)

    logging.info('R  = ' + str(recall) )
    logging.info('P  = ' + str(precision))
    logging.info('F1 = ' + str(f1))
    logging.info('false alarm = ' + str(false_alarm))

    if visualize:
        sns.heatmap(conf_matrix, xticklabels=['Normal', 'Attack'], yticklabels=['Normal', 'Attack'], annot=True,fmt='d')
        plt.title('Confusion matrix')
        plt.ylabel('True class')
        plt.xlabel('Predicted class')
        plt.savefig('confusion_matrix_offline.png')
        plt.show()

def save_threshold(threshold, path):
    with open(path, 'wb') as f:
        pickle.dump(threshold, f)

def load_threshold(path):
    with open(path, 'rb') as f:
        threshold = pickle.load(f)
    return threshold

import numpy as np
import pandas as pd
import matplotlib as mpl
import tensorflow as tf
from keras.models import Model
from keras.layers import Input, Dense, Dropout
from keras import regularizers, initializers
from sklearn.metrics import confusion_matrix
from time import time
import pickle

mpl.use('TkAgg')
np.random.seed(4999)
tf.random.set_seed(4999)

class MultilayerAutoEncoder():

    def __init__(self, input_dim):

        input_layer = Input(shape=(input_dim,))

        layer = Dense(128, activation='relu',   #128
                        activity_regularizer=regularizers.l1(10e-5),
                        kernel_initializer=initializers.RandomNormal())(input_layer)
        
        layer = Dropout(rate=0.6)(layer);

        layer = Dense(64, activation='tanh',    #64
                      activity_regularizer=regularizers.l1(10e-5),
                      kernel_initializer=initializers.RandomNormal())(layer)
        
        layer = Dropout(rate=0.6)(layer);

        layer = Dense(128, activation='relu',   #128
                      activity_regularizer=regularizers.l1(10e-5),
                      kernel_initializer=initializers.RandomNormal())(layer)
        
        output_layer = Dense(input_dim, activation='relu',
                      activity_regularizer=regularizers.l1(10e-5),
                      kernel_initializer=initializers.RandomNormal())(layer)

        self.autoencoder = Model(inputs=input_layer, outputs=output_layer)

    def summary(self, ):
        self.autoencoder.summary()

    def train(self, x, y):

        epochs = 50
        batch_size = 2048
        validation_split = 0.1

        print('Start training.')

        self.autoencoder.compile(optimizer='rmsprop',
                                 loss='mean_squared_error')
        start = time()
        history = self.autoencoder.fit(x, y,
                                       epochs=epochs,
                                       batch_size=batch_size,
                                       shuffle=True,
                                       validation_split=validation_split,
                                       verbose=2)
        print(time() - start)

        x_val = x[x.shape[0]-(int)(x.shape[0]*validation_split):x.shape[0]-1, :]

        print(' + validation_size    : ',  x_val.shape)
        print(x_val)

        val_predictions = self.autoencoder.predict(x_val)
        val_mse = np.mean(np.power(x_val - val_predictions, 2), axis=1)

        threshold = np.percentile(val_mse , 90)
        print('Current threshold: ')
        print(threshold)

        df_history = pd.DataFrame(history.history)
        return df_history, threshold
    
    def predict(self, x, threshold):
        predictions = self.autoencoder.predict(x)
        mse = np.mean(np.power(x - predictions, 2), axis=1)
        y_pred = [1 if e > threshold else 0 for e in mse]
        return y_pred

    def evaluate(self, x_test, y_test, threshold):
        predictions = self.autoencoder.predict(x_test)

        mse=np.mean (np.power(x_test - predictions, 2), axis=1)
        y_test = y_test.reset_index(drop=True)
        df_error = pd.DataFrame({'reconstruction_error' : mse, 'true_class' : y_test})
        print(mse)
        print('y_test***: ')
        print(df_error.to_string())
        print(df_error.describe(include='all'))

        compute(df_error, threshold)

def compute(df_error, threshold):
    y_pred = [1 if e > threshold else 0 for e in df_error.reconstruction_error.values]
    conf_matrix = confusion_matrix(df_error.true_class, y_pred)

    tn, fp, fn, tp = conf_matrix.ravel()

    recall = tp / (tp+fn)
    precision = tp / (tp+fp)
    f1 = 2 * ( (precision*recall) / (precision+recall) )
    false_alarm = 1. * fp / (tn + fp)

    print('R  = ', recall );
    print('P  = ', precision);
    print('F1 = ', f1);
    print('false alarm = ', false_alarm);

def save_threshold(threshold, path):
    with open(path, 'wb') as f:
        pickle.dump(threshold, f)

def load_threshold(path):
    with open(path, 'rb') as f:
        threshold = pickle.load(f)
    return threshold

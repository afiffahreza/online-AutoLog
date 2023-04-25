from app.data import retrieve_data_train, retrieve_data_scoring, retrieve_data_file
from app.model import MultilayerAutoEncoder
from app.db import CouchDB
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

def test_retrieve_data_train():
    db = CouchDB('http://localhost:5984', 'admin', 'password')
    applications = ['catalog', 'customer', 'order', 'ingress-nginx']
    df_train = retrieve_data_train(db, applications)
    df_test = retrieve_data_scoring(db, applications)

    print("Train data:")
    print(df_train)
    print()

    print("Test data:")
    print(df_test)
    print()

    x_train = df_train.drop('label', axis=1)
    y_train = df_train['label']

    x_test = df_test.drop('label', axis=1)
    y_test = df_test['label']

    x_train = x_train.values
    x_test = x_test.values

    scaler = MinMaxScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    print("Train data scaled:")
    print(x_train_scaled)
    print()

    print("Test data scaled:")
    print(x_test_scaled)
    print()

    input_dim = x_train.shape[1]
    autoencoder = MultilayerAutoEncoder(input_dim = input_dim)

    autoencoder.summary()

    history, threshold = autoencoder.train(x_train, x_train)

    autoencoder.evaluate(x_test, y_test, threshold)

def test_local():
    # df = retrieve_data_file('./dataset/scores_labeled.csv')
    names = ['ID','NULL','R00','R01','R02','R03','R04','R05','R06','R07','R10','R11','R12','R13','R14','R15','R16','R17','R20',
            'R21','R22','R23','R24','R25','R26','R27','R30','R31','R32','R33','R34','R35','R36','R37','R40','R41','R42','R43',
            'R44','R45','R46','R47','R50','R51','R52','R53','R54','R55','R56','R57','R60','R61','R62','R63','R64','R65',
            'R66','R67','R70','R71','R72','R73','R74','R75','R76','R77','UNKNOWNLOCATION','UNSPECIFIED','Label']
    df = pd.read_csv('./dataset/BGLvector.csv', names=names, header=None, sep=',', index_col=False, dtype='unicode')
    labels = ['R00','R01','R02','R03','R04','R05','R06','R07','R10','R11','R12','R13','R14','R15','R16','R17','R20',
        'R21','R22','R23','R24','R25','R26','R27','R30','R31','R32','R33','R34','R35','R36','R37','R40','R41','R42','R43',
        'R44','R45','R46','R47','R50','R51','R52','R53','R54','R55','R56','R57','R60','R61','R62','R63','R64','R65',
        'R66','R67','R70','R71','R72','R73','R74','R75','R76','R77','UNKNOWNLOCATION','UNSPECIFIED', 'Label', 'Id']
    applications = ['R00','R01','R02','R03','R04','R05','R06','R07','R10','R11','R12','R13','R14','R15','R16','R17','R20',
        'R21','R22','R23','R24','R25','R26','R27','R30','R31','R32','R33','R34','R35','R36','R37','R40','R41','R42','R43',
        'R44','R45','R46','R47','R50','R51','R52','R53','R54','R55','R56','R57','R60','R61','R62','R63','R64','R65',
        'R66','R67','R70','R71','R72','R73','R74','R75','R76','R77','UNKNOWNLOCATION','UNSPECIFIED']
    df['Label'] = np.where(df['Label'] == 'OK', 0, 1)

    # Split anomalous and normal data
    good = df[df['Label'] == 0]
    bad = df[df['Label'] == 1]

    # Split good data into train and test
    x_train, x_test = train_test_split(good, test_size=0.2, random_state=999)

    # Concat bad data to test
    x_test = pd.concat([x_test, bad])

    # Split data into features and labels
    y_train = x_train['Label']
    y_test = x_test['Label']
    x_train = x_train.drop(['Label', 'ID'], axis=1)
    x_test = x_test.drop(['Label', 'ID'], axis=1)

    # Print data
    # print("Train data:")
    # print(x_train.head(15))
    # print()

    # print("Test data:")
    # print(x_test.head(15))
    # print()

    # Convert to numpy array
    x_train = x_train.values
    x_test = x_test.values

    # Print data
    print("Train data:")
    print(x_train)
    print()

    print("Test data:")
    print(x_test)
    print()

    # Scale data
    scaler = MinMaxScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    # Train model
    input_dim = x_train.shape[1]
    autoencoder = MultilayerAutoEncoder(input_dim = input_dim)
    autoencoder.summary()
    history, threshold = autoencoder.train(x_train_scaled, x_train_scaled)
    autoencoder.evaluate(x_test_scaled, y_test, threshold)

if __name__ == '__main__':
    test_local()
from app.data import retrieve_data_train, retrieve_data_scoring
from app.model import MultilayerAutoEncoder
from app.db import CouchDB
from sklearn.preprocessing import MinMaxScaler

if __name__ == '__main__':
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

# Data Access

from __future__ import unicode_literals
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from db import CouchDB
import pandas as pd
import numpy as np

def retrieve_data(db, applications):
    data = {}
    for app in applications:
        db_name = "train-" + app
        current_data = db.get_last(db_name)
        data[app] = current_data['data']['score']
    max_len = max([len(v) for v in data.values()])
    data['label'] = [0 for i in range(max_len)]
    return pd.DataFrame.from_dict(data)

def retrieve_data_scoring(db, applications):
    data = {}
    for app in applications:
        db_name = "score-" + app
        docs = []
        num = int(db.get_docs_count(db_name))  
        for i in range(1, num+1):
            doc = db.get(db_name, str(i))
            docs.append(doc['data']['score'])
        data[app] = docs
    data['label'] = [0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    return pd.DataFrame.from_dict(data)

if __name__ == '__main__':
    db = CouchDB('http://localhost:5984', 'admin', 'password')
    applications = ['catalog', 'customer', 'order', 'ingress-nginx']
    df_train = retrieve_data(db, applications)
    df_test = retrieve_data_scoring(db, applications)
    
    print(df_train)
    print(df_test)

    x_train = df_train.drop('label', axis=1)
    y_train = df_train['label']
    x_test = df_test.drop('label', axis=1)
    y_test = df_test['label']

    scaler = MinMaxScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)

    print(x_train)
    print(y_train)
    print(x_test)
    print(y_test)

    from sklearn.svm import OneClassSVM

    clf = OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)

    clf.fit(x_train)

    y_pred_train = clf.predict(x_train)
    y_pred_train[y_pred_train == 1] = 0
    y_pred_train[y_pred_train == -1] = 1

    print(y_train.values)
    print(y_pred_train)

    y_pred_test = clf.predict(x_test)
    y_pred_test[y_pred_test == 1] = 0
    y_pred_test[y_pred_test == -1] = 1

    print(y_test.values)
    print(y_pred_test)

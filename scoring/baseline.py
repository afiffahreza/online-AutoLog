from preprocess import read_log, preprocess, tokenize
from storing import store_normal_terms, store_normal_score
from weighting import weight
from db import CouchDB
import os

def baseline_storing(logfile, app):

    # Read file
    lines = read_log(logfile)

    # ==================== Preprocessing ====================
    lines = preprocess(lines)

    # ==================== Term weighting ====================
    wordCounts = tokenize(lines)

    couchdb_url = os.environ.get('COUCHDB_URL', 'http://localhost:5984')
    couchdb_user = os.environ.get('COUCHDB_USER', 'admin')
    couchdb_password = os.environ.get('COUCHDB_PASSWORD', 'password')
    db = CouchDB(couchdb_url, couchdb_user, couchdb_password)

    store_normal_terms(db, app, wordCounts)

def baseline_training(logfile, app):

    baseline_storing(logfile, app)


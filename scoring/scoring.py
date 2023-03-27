from preprocess import read_log, preprocess, tokenize
from db import CouchDB
import os

def scoring(logfile, app):

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
    
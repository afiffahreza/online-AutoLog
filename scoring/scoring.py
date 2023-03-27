from preprocess import read_log, preprocess, tokenize
from storing import get_normal_terms, store_score
from weighting import weight
from db import CouchDB
from datetime import datetime
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
    
    baseline = get_normal_terms(db, app)
    score = weight(baseline, wordCounts)

    score_data = {
        "score": score,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    store_score(db, app, score_data)

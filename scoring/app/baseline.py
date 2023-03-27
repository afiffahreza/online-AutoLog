from app.preprocess import read_log, preprocess, tokenize, output_file
from app.storing import store_normal_terms, store_normal_score, get_normal_terms
from app.weighting import weight_baseline
from app.db import CouchDB
from datetime import datetime
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
    
    debug = os.environ.get('DEBUG', 0)
    if debug:
        output_file(wordCounts, "output/" + app + "-baseline.txt")

def baseline_training(logfile, app):

    baseline_storing(logfile, app)

    couchdb_url = os.environ.get('COUCHDB_URL', 'http://localhost:5984')
    couchdb_user = os.environ.get('COUCHDB_USER', 'admin')
    couchdb_password = os.environ.get('COUCHDB_PASSWORD', 'password')
    db = CouchDB(couchdb_url, couchdb_user, couchdb_password)

    baseline = get_normal_terms(db, app)

    scores = weight_baseline(baseline)

    score_data = {
        "score": scores,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    store_normal_score(db, app, score_data)

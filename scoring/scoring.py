from pyspark.sql import SparkSession
from preprocess import preprocess
from weighting import tokenize, weight, store_normal_score
from db import CouchDB
import os

def score_baseline(logfile, app):

    spark = SparkSession.builder.appName("AutoLogScoring").getOrCreate()

    # Stream from file source on dataset/logs.txt
    lines = spark.read.text(logfile)

    # ==================== Preprocessing ====================
    lines = preprocess(lines)

    # ==================== Term weighting ====================
    wordCounts = tokenize(lines)
    # Convert the word counts to JSON
    wordCountsJSON = wordCounts.toJSON().collect()

    couchdb_url = os.environ.get('COUCHDB_URL', 'http://localhost:5984')
    couchdb_user = os.environ.get('COUCHDB_USER', 'admin')
    couchdb_password = os.environ.get('COUCHDB_PASSWORD', 'password')
    db = CouchDB(couchdb_url, couchdb_user, couchdb_password)

    score = weight(wordCountsJSON, db, app)

    M = 0 # TODO: get from db

    data = {
        'M': M,
        'score': score
    }

    store_normal_score(score, db, app)

    # Stop the Spark session
    spark.stop()

def score_trained(logfile, app):

    spark = SparkSession.builder.appName("AutoLogScoring").getOrCreate()

    # Stream from file source on dataset/logs.txt
    lines = spark.read.text(logfile)

    # ==================== Preprocessing ====================
    lines = preprocess(lines)

    # ==================== Term weighting ====================
    wordCounts = tokenize(lines)
    # Convert the word counts to JSON
    wordCountsJSON = wordCounts.toJSON().collect()

    couchdb_url = os.environ.get('COUCHDB_URL', 'http://localhost:5984')
    couchdb_user = os.environ.get('COUCHDB_USER', 'admin')
    couchdb_password = os.environ.get('COUCHDB_PASSWORD', 'password')
    db = CouchDB(couchdb_url, couchdb_user, couchdb_password)

    weight(wordCountsJSON, db, app)

    # Stop the Spark session
    spark.stop()
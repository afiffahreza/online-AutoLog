from pyspark.sql import SparkSession
from preprocess import preprocess
from weighting import tokenize, store
from db import CouchDB
import os

def baseline(logfile, app):

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

    store(wordCountsJSON, db, app)

    # Stop the Spark session
    spark.stop()

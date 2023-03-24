from pyspark.sql import SparkSession
from preprocess import preprocess
from weighting import tokenize, store

spark = SparkSession.builder.appName("AutoLogScoring").getOrCreate()

# Stream from file source on dataset/logs.txt
lines = spark.read.text("./dataset/Explore-logs-2023-03-15 07_36_39.txt")

# ==================== Preprocessing ====================
# Parse the lines into words, removing the variable tokens of the log lines while preserving the constant parts.
lines = preprocess(lines)

# ==================== Term weighting ====================
# Given a chunk after parsing, term weighting is done by:
# (i) tokening the log lines of the chunk into terms,
# (ii) counting the occurrences of the terms within the chunk,
# (iii) storing the baseline terms to db.

wordCounts = tokenize(lines)

# Convert the word counts to JSON
wordCountsJSON = wordCounts.toJSON().collect()
store(wordCountsJSON)

# Stop the Spark session
spark.stop()

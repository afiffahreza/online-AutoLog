from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, translate, regexp_replace, udf
from pyspark.sql.types import StringType
import numpy as np

spark = SparkSession.builder.appName("AutoLogScoring").getOrCreate()

# Stream from file source on dataset/logs.txt
lines = spark.read.text("./dataset/Explore-logs-2023-03-15 07_36_39.txt")


# ==================== Preprocessing ====================
# Parse the lines into words, removing the variable tokens of the log lines while preserving the constant parts.
# We also remove special characters and punctuation, such as #, ?, and %.

# Define regular expressions for variable tokens such as timestamps, IP addresses, random log IDs, and dates
timestamp_regex = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\+\d{2}:\d{2})?'
ip_regex = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?'
id_regex = r'[0-9a-fA-F]{32}'
date_regex = r'\d{4}/\d{2}/\d{2}|\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} \+\d{4}'
path_regex = r'/\d{1,4}'

# Replace variables with fixed tokens
lines = lines.withColumn("value", regexp_replace(lines.value, timestamp_regex, "TIMESTAMP"))
lines = lines.withColumn("value", regexp_replace(lines.value, ip_regex, "IP"))
lines = lines.withColumn("value", regexp_replace(lines.value, id_regex, "ID"))
lines = lines.withColumn("value", regexp_replace(lines.value, date_regex, "DATE"))
lines = lines.withColumn("value", regexp_replace(lines.value, path_regex, "/PATH"))

# Define a string of special characters and punctuation to remove
special_chars = '!@#$%^&*()+{}|:"<>?=[]\;\',./-_'

# Remove special characters and punctuation from the log lines
lines = lines.withColumn("value", translate(lines.value, special_chars, len(special_chars)*' '))

# Replace numbers
httpone_regex = r'\s1[01][0-9]\s'
httptwo_regex = r'\s2[02][0-9]\s'
httpthree_regex = r'\s30[0-9]\s'
httpfour_regex = r'\s4[0-5][0-9]\s'
httpfive_regex = r'\s5[01][0-9]\s'
number_regex = r'(\s+|^)[0-9]\d+(\s+|$)'
single_number_regex = r'(\s+|^)[0-9](\s+|$)'
double_number_regex = r'(\s+|^)[0-9][0-9](\s+|$)'
lines = lines.withColumn("value", regexp_replace(lines.value, httpone_regex, " HTTP1xx "))
lines = lines.withColumn("value", regexp_replace(lines.value, httptwo_regex, " HTTP2xx "))
lines = lines.withColumn("value", regexp_replace(lines.value, httpthree_regex, " HTTP3xx "))
lines = lines.withColumn("value", regexp_replace(lines.value, httpfour_regex, " HTTP4xx "))
lines = lines.withColumn("value", regexp_replace(lines.value, httpfive_regex, " HTTP5xx "))
lines = lines.withColumn("value", regexp_replace(lines.value, number_regex, " NUMBER "))
lines = lines.withColumn("value", regexp_replace(lines.value, single_number_regex, " NUMBER "))
lines = lines.withColumn("value", regexp_replace(lines.value, double_number_regex, " NUMBER "))

# Remove extra whitespace from the log lines
lines = lines.withColumn("value", regexp_replace(lines.value, r'\s+', ' '))

# Function to convert all characters to uppercase
@udf(returnType=StringType()) 
def upperCase(str):
    return str.lower()

# Change uppercase characters to lowercase
lines = lines.withColumn("value", upperCase(lines.value))


# ==================== Term weighting ====================
# Given a chunk after parsing, term weighting is done by:
# (i) tokening the log lines of the chunk into terms,
# (ii) counting the occurrences of the terms within the chunk,
# (iii) computing a numeric score for the chunk based on the occurrences of the terms.

# === (i) ===

# Split the lines into words
words = lines.select(
    explode(
        split(lines.value, " ")
    ).alias("word")
)

# Remove empty words
words = words.filter(words.word != "")

# === (ii) ===

# Count the occurrences of the terms within the chunk
wordCounts = words.groupBy("word").count()

# === (iii) ===

# Access db to get the total number of terms in all chunks

# Compute a numeric score for the chunk based on the occurrences of the terms using log entropy

# Global Weighting
# xtj: number of occurrences of term t in chunk j
# Nt: total number of occurrences of term t in all chunks
# Ptj: fraction of occurrences of term t in all chunks
# Ptj = xtj / Nt
# et: entropy of term t in all chunks
# M: total number of chunks, including the current chunk
# et = 1 + ( sum(ptj * log2(ptj)) / log2(M))

term_entropy = []

for word in wordCounts:
    # Get the total number of occurrences of term t in all chunks
    Nt = 0 # TODO: get from db
    Nt += word.count
    # Get the number of chunks
    M = 0 # TODO: get from db
    M += 1
    # Compute the log entropy of term t in all chunks
    M = 0 # TODO: get from db
    sum_Ptj_log2_Ptj = 0
    for i in range(M):
        # Get the number of occurrences of term t in chunk j
        xtj = 0 # TODO: get from db
        # Compute the fraction of occurrences of term t in all chunks
        Ptj = xtj / Nt
        # Compute the sum of the product of Ptj and log2(Ptj)
        sum_Ptj_log2_Ptj += Ptj * np.log2(Ptj)
    et = 1 + (sum_Ptj_log2_Ptj / np.log2(M))
    # Save et to term_entropy
    term_entropy.append({"word": word.word, "score": et})

# Local Weighting
# xt: number of occurrences of term t
# wt: weight of term t
# wt = log2(1+xt)
local_weight = []
for word in wordCounts:
    # Get the number of occurrences of term t
    xt = word.count
    # Compute the weight of term t
    wt = np.log2(1+xt)
    # Save wt to term_entropy
    local_weight.append({"word": word.word, "score": wt})

# Final chunk score
# s: score of the chunk
# s = root(sum(square(et log2(1+xt))))
score = 0
for i in range(len(term_entropy)):
    score += term_entropy[i].score * local_weight[i].score
score = np.sqrt(score)

# Output the score of the chunk
print(score)

# Stop the Spark session
spark.stop()

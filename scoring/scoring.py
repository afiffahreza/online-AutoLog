from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, translate, regexp_replace
import re

spark = SparkSession.builder.appName("AutoLogScoring").getOrCreate()

# Stream from file source on dataset/logs.txt
lines = spark.read.text("./dataset/Explore-logs-2023-03-15 07_36_39.txt")

# Parse the lines into words, removing the variable tokens of the log lines while preserving the constant parts.
# We also remove special characters and punctuation, such as #, ?, and %.

# Remove timestamps from the log lines, which are the first 25 characters of each line.
# example format: 2023-03-15T07:35:42+07:00
lines = lines.withColumn("value", lines.value.substr(26, 1000))

# Define regular expressions for IP addresses and random log IDs
ip_regex = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?'
id_regex = r'[0-9a-fA-F]{32}'
date_regex = r'\d{4}/\d{2}/\d{2}|\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} \+\d{4}'
path_regex = r'/\d{1,4}'
# Replace IP addresses and random log IDs with fixed tokens
lines = lines.withColumn("value", regexp_replace(lines.value, ip_regex, "IP"))
lines = lines.withColumn("value", regexp_replace(lines.value, id_regex, "ID"))
lines = lines.withColumn("value", regexp_replace(lines.value, date_regex, "DATE"))
lines = lines.withColumn("value", regexp_replace(lines.value, path_regex, "PATH"))

# Define a string of special characters and punctuation to remove
special_chars = '!@#$%^&*()_+{}|:"<>?-=[]\;\',./'
# Remove special characters and punctuation from the log lines
lines = lines.withColumn("value", translate(lines.value, special_chars, len(special_chars)*' '))

# Split the lines into words
words = lines.select(
    explode(
        split(lines.value, " ")
    ).alias("word")
)

# Term weighting
# Given a chunk after parsing, term weighting is done by:
# (i) tokening the log lines of the chunk into terms,
# (ii) counting the occurrences of the terms within the chunk,
# (iii) computing a numeric score for the chunk based on the occurrences of the terms.
# Tokenization is applied to all the lines, including those pertaining to negations in the log files.

# Count the occurrences of the terms within the chunk
wordCounts = words.groupBy("word").count()

# Output the results
wordCounts.show()

# Save the result to a file, overwriting the existing file
wordCounts.coalesce(1).write.mode("overwrite").format("com.databricks.spark.csv").option("header", "true").save("output")

# Stop the Spark session when done
spark.stop()
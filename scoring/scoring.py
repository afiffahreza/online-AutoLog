from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split

spark = SparkSession.builder.appName("AutoLogScoring").getOrCreate()

# Stream from file source on dataset/logs.txt
lines = spark.read.text("./dataset/Explore-logs-2023-03-15 07_36_39.txt")

# Parse the lines into words, removing the variable tokens of the log lines while preserving the constant parts.
# We also remove special characters and punctuation, such as #, ?, and %.

# Remove timestamps from the log lines, which are the first 25 characters of each line.
# example format: 2023-03-15T07:35:42+07:00
lines = lines.withColumn("value", lines.value.substr(26, 1000))

# Split the lines into words
words = lines.select(
    explode(
        split(lines.value, " ")
    ).alias("word")
)

# Remove special characters and punctuation
words = words.filter(words.word != "#")
words = words.filter(words.word != "?")
words = words.filter(words.word != "%")

# Remove the variable tokens of the log lines while preserving the constant parts
words = words.filter(words.word != "GET")
words = words.filter(words.word != "POST")
words = words.filter(words.word != "HTTP/1.1")
words = words.filter(words.word != "HTTP/1.0")
words = words.filter(words.word != "HTTP/2")
words = words.filter(words.word != "HTTP/3")
words = words.filter(words.word != "DELETE")
words = words.filter(words.word != "PUT")
words = words.filter(words.word != "PATCH")
words = words.filter(words.word != "OPTIONS")
words = words.filter(words.word != "HEAD")

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

# Save the result to a file
wordCounts.coalesce(1).write.format("com.databricks.spark.csv").option("header", "true").save("output")

# Stop the Spark session when done
spark.stop()
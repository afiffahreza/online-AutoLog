from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, translate, regexp_replace, udf
from pyspark.sql.types import StringType

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
special_chars = '!@#$%^&*()+{}|:"<>?=[]\;\',./'

# Remove special characters and punctuation from the log lines
lines = lines.withColumn("value", translate(lines.value, special_chars, len(special_chars)*' '))

# Remove double quotes, singular - and _ characters from the log lines
lines = lines.withColumn("value", regexp_replace(lines.value, r'(\s-\s)|(\s_\s)|"', ' '))

# Replace numbers
http_status_one_regex = r'\s1[01][0-9]\s'
http_status_two_regex = r'\s2[02][0-9]\s'
http_status_three_regex = r'\s30[0-9]\s'
http_status_four_regex = r'\s4[0-5][0-9]\s'
http_status_five_regex = r'\s5[01][0-9]\s'
number_regex = r'\s+\d\s+'
lines = lines.withColumn("value", regexp_replace(lines.value, http_status_one_regex, " HTTP_STATUS_1xx "))
lines = lines.withColumn("value", regexp_replace(lines.value, http_status_two_regex, " HTTP_STATUS_2xx "))
lines = lines.withColumn("value", regexp_replace(lines.value, http_status_three_regex, " HTTP_STATUS_3xx "))
lines = lines.withColumn("value", regexp_replace(lines.value, http_status_four_regex, " HTTP_STATUS_4xx "))
lines = lines.withColumn("value", regexp_replace(lines.value, http_status_five_regex, " HTTP_STATUS_5xx "))
lines = lines.withColumn("value", regexp_replace(lines.value, number_regex, " NUMBER "))

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

# Split the lines into words
words = lines.select(
    explode(
        split(lines.value, " ")
    ).alias("word")
)

# Count the occurrences of the terms within the chunk
wordCounts = words.groupBy("word").count()

# Output the results
wordCounts.show()

# Save the result to a csv file, overwriting the existing file
wordCounts.coalesce(1).write.mode("overwrite").format("com.databricks.spark.csv").option("header", "true").save("output")

# Output the result to a json file, overwriting the existing file
# wordCounts.coalesce(1).write.mode("overwrite").json("json_output")

# Stop the Spark session
spark.stop()

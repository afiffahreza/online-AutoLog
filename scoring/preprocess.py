import re

def read_log(logfile):
    print("Reading log file: " + logfile)
    with open(logfile, 'r') as f:
        lines = f.readlines()
    return lines

def preprocess(lines):
    print("Preprocessing log file...")

    # Define regular expressions for variable tokens such as timestamps, IP addresses, random log IDs, and dates
    timestamp_regex = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\+\d{2}:\d{2})?'
    ip_regex = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?'
    id_regex = r'[0-9a-fA-F]{32}'
    date_regex = r'\d{4}/\d{2}/\d{2}|\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} \+\d{4}'
    path_regex = r'/\d{1,4}'

    # Replace variable tokens with a placeholder
    lines = [re.sub(timestamp_regex, "TIMESTAMP", line) for line in lines]
    lines = [re.sub(ip_regex, "IP", line) for line in lines]
    lines = [re.sub(id_regex, "ID", line) for line in lines]
    lines = [re.sub(date_regex, "DATE", line) for line in lines]
    lines = [re.sub(path_regex, "/PATH", line) for line in lines]

    # Replace special characters with a space
    special_regex = r'[^a-zA-Z0-9\s]'
    lines = [re.sub(special_regex, " ", line) for line in lines]

    # Replace numbers
    number_regex = r'\d+'
    lines = [re.sub(number_regex, "NUMBER", line) for line in lines]

    # Replace multiple spaces with a single space
    lines = [re.sub(r'\s+', ' ', line) for line in lines]

    # Remove leading and trailing whitespace
    lines = [line.strip() for line in lines]

    # Remove empty lines
    lines = [line for line in lines if line]

    # Lowercase all characters
    lines = [line.lower() for line in lines]

    print("Preprocessing complete.")

    return lines

def tokenize(lines):
    # Split each line into a list of words
    words = [line.split() for line in lines]

    # Flatten the list of lists into a single list
    words = [word for line in words for word in line]

    # Count the occurrences of each word
    word_counts = {}
    for word in words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
    
    return word_counts

def output_file(word_count_dict, filename):
    print("Writing to file: " + filename)
    # Create the file if it doesn't exist, otherwise overwrite it
    with open(filename, 'w') as f:
        for word, count in word_count_dict.items():
            f.write(word + " " + str(count) + "\n")

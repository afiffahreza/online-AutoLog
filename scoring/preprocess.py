from pyspark.sql.functions import translate, regexp_replace, udf
from pyspark.sql.types import StringType
import re

# ==================== Helper Functions ====================
# Function to get http status message with http status code input
def get_http_status(status_code):
    http_status_codes = {
        100: 'Continue',
        101: 'Switching Protocols',
        102: 'Processing',
        103: 'Early Hints',
        200: 'OK',
        201: 'Created',
        202: 'Accepted',
        203: 'Non-Authoritative Information',
        204: 'No Content',
        205: 'Reset Content',
        206: 'Partial Content',
        207: 'Multi-Status',
        208: 'Already Reported',
        226: 'IM Used',
        300: 'Multiple Choices',
        301: 'Moved Permanently',
        302: 'Found',
        303: 'See Other',
        304: 'Not Modified',
        305: 'Use Proxy',
        306: '(Unused)',
        307: 'Temporary Redirect',
        308: 'Permanent Redirect',
        400: 'Bad Request',
        401: 'Unauthorized',
        402: 'Payment Required',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        407: 'Proxy Authentication Required',
        408: 'Request Timeout',
        409: 'Conflict',
        410: 'Gone',
        411: 'Length Required',
        412: 'Precondition Failed',
        413: 'Payload Too Large',
        414: 'URI Too Long',
        415: 'Unsupported Media Type',
        416: 'Range Not Satisfiable',
        417: 'Expectation Failed',
        418: "I'm a teapot",
        421: 'Misdirected Request',
        422: 'Unprocessable Entity',
        423: 'Locked',
        424: 'Failed Dependency',
        425: 'Too Early',
        426: 'Upgrade Required',
        428: 'Precondition Required',
        429: 'Too Many Requests',
        431: 'Request Header Fields Too Large',
        451: 'Unavailable For Legal Reasons',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout',
        505: 'HTTP Version Not Supported',
        506: 'Variant Also Negotiates',
        507: 'Insufficient Storage',
        508: 'Loop Detected',
        510: 'Not Extended',
        511: 'Network Authentication Required'
    }
    
    status_message = http_status_codes.get(status_code, 'NUMBER')

    if status_message == 'NUMBER':
        return "NUMBER"
    else:    
        return f"http{status_code}{status_message.replace(' ', '')}"

# Function to convert all http status codes to a single token
@udf(returnType=StringType())
def replace_http_status(line):
    # Define regular expressions for http status codes
    http_status_regex = r'\s\d{3}\s'
    # Check if the line contains http status codes
    if re.search(http_status_regex, line):
        # Get the http status code
        status_code = int(re.search(http_status_regex, line).group(0).strip())
        # Replace the http status code with a single token
        line = re.sub(http_status_regex, f" {get_http_status(status_code)} ", line)
    return line

# Function to convert all characters to lowercase
@udf(returnType=StringType())
def to_lower(s):
    return s.lower()

# ==================== Preprocessing ====================
# Parse the lines into words, removing the variable tokens of the log lines while preserving the constant parts.
# We also remove special characters and punctuation, such as #, ?, and %.
def preprocess(l):
    lines = l
    # Define regular expressions for variable tokens such as timestamps, IP addresses, random log IDs, and dates
    timestamp_regex = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\+\d{2}:\d{2})?'
    ip_regex = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?'
    id_regex = r'[0-9a-fA-F]{32}'
    date_regex = r'\d{4}/\d{2}/\d{2}|\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} \+\d{4}'
    path_regex = r'/\d{1,4}'
    # Replace variable tokens with a placeholder
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
    # possible_http_regex = r'(\s+|^)(\d{3})(\s+|$)'
    number_regex = r'\d+'
    # lines = lines.withColumn("value", regexp_replace(lines.value, possible_http_regex, replace_http_status('value')))
    # lines = lines.withColumn("value", replace_http_status(lines.value))
    lines = lines.withColumn("value", regexp_replace(lines.value, number_regex, " NUMBER "))

    # Remove extra whitespace from the log lines
    lines = lines.withColumn("value", regexp_replace(lines.value, r'\s+', ' '))

    # Change uppercase characters to lowercase
    lines = lines.withColumn("value", to_lower(lines.value))

    return lines

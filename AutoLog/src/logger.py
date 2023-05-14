import re, subprocess, os

def log_generator(app, time_start, time_end):
    file_dir = os.path.dirname(os.path.realpath(__file__))
    current_dir = os.path.dirname(file_dir)
    filename = f"{current_dir}/output/{app}-log-{time_start}.txt"
    loki_url = os.environ.get('LOKI_URL', 'http://localhost/loki')
    query = "'{app=\""+app+"\"}'"
    # logcli query $query --addr=$LOKI_URL --from=$time_end --to=$NOW --limit=5000 > ./output/$app-log-$NOW.txt
    command = "logcli query "+query+" --addr="+loki_url+" --from="+time_end+" --to="+time_start+" --limit=5000  > "+filename
    print("Command to be executed: ", command)
    subprocess.run(command, shell=True)
    return filename

def log_remover(app, time_start):
    file_dir = os.path.dirname(os.path.realpath(__file__))
    current_dir = os.path.dirname(file_dir)
    filename = f"{current_dir}/output/{app}-log-{time_start}.txt"
    # rm ./output/$app-log-$NOW.txt
    subprocess.run(["rm", filename])

def read_log(logfile):
    print("Reading log file: " + logfile)
    with open(logfile, 'r') as f:
        lines = f.readlines()
    # remove first 3 lines
    lines = lines[3:]
    return lines

def preprocess(lines):
    lines = [re.sub('<:.+?:>', '', line) for line in lines]
    lines = [re.sub('[^a-zA-Z0-9\s]', '', line) for line in lines]
    lines = [re.sub('\s+', ' ', line) for line in lines]
    lines = [line.strip() for line in lines]
    lines = [line.lower() for line in lines]
    return lines

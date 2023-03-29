import subprocess, os

def log_generator(app, current_time, ten_seconds_ago):
    file_dir = os.path.dirname(os.path.realpath(__file__))
    current_dir = os.path.dirname(file_dir)
    filename = f"{current_dir}/output/{app}-log-{current_time}.txt"
    loki_url = os.environ.get('LOKI_URL', 'http://localhost/loki')
    query = "'{app=\""+app+"\"}'"
    # logcli query $query --addr=$LOKI_URL --from=$TEN_SECONDS_AGO --to=$NOW --limit=5000 > ./output/$app-log-$NOW.txt
    command = "logcli query "+query+" --addr="+loki_url+" --from="+ten_seconds_ago+" --to="+current_time+" --limit=5000  > "+filename
    print("Command to be executed: ", command)
    subprocess.run(command, shell=True)
    return filename

def log_remover(app, current_time):
    file_dir = os.path.dirname(os.path.realpath(__file__))
    current_dir = os.path.dirname(file_dir)
    filename = f"{current_dir}/output/{app}-log-{current_time}.txt"
    # rm ./output/$app-log-$NOW.txt
    subprocess.run(["rm", filename])

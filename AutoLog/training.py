import os, datetime
import pandas as pd
from src.logger import get_logs
from src.scoring import Scoring
from src.model import MultilayerAutoEncoder, save_threshold
from grafana_loki_client import Client
from sklearn.preprocessing import MinMaxScaler

def file_scoring(filename):
    print("Reading baseline score from", filename)
    scoring = Scoring()
    scoring.load(filename)
    return scoring.calculate_baseline_score()

def loki_scoring(loki_client, app, baseline_time_start, baseline_time_end, log_period, save_path=None):
    print("Collecting & scoring baseline logs for", app)
    print("Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    time_start = baseline_time_start

    scoring = Scoring()

    while time_start < baseline_time_end:
        time_end = datetime.datetime.strptime(time_start, '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(seconds=log_period)
        time_end = time_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        lines = get_logs(loki_client, app, time_start, time_end)
        scoring.add_lines(lines)
        time_start = time_end
    
    if save_path is not None:
        scoring.save(save_path)

    print("Finished scoring baseline logs for", app)
    print("Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return scoring.calculate_baseline_score()

def model_training(scores, save_path=None):
    print("Training model...")
    print("Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    df = pd.DataFrame.from_dict(scores)
    x_train = df.values
    scaler = MinMaxScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    input_dim = x_train.shape[1]
    autoencoder = MultilayerAutoEncoder(input_dim = input_dim)
    history, threshold = autoencoder.train(x_train_scaled, x_train_scaled)

    if save_path is not None:
        model_file = save_path + "model.h5"
        autoencoder.autoencoder.save(model_file)
        threshold_file = save_path + "threshold.pkl"
        save_threshold(threshold, threshold_file)

    print("Finished training model...")
    print("Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return autoencoder, threshold

if __name__ == "__main__":

    starting_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("Starting training...")
    print("Time start: ", starting_time)
    print("\n")

    applications = os.environ.get('APPLICATIONS', 'frontend cartservice productcatalogservice currencyservice paymentservice shippingservice emailservice checkoutservice recommendationservice adservice').split(' ')
    log_period = int(os.environ.get('LOG_PERIOD', 10))
    baseline_time_start = os.environ.get('BASELINE_TIME_START', '2023-05-18T10:00:00Z')
    baseline_time_end = os.environ.get('BASELINE_TIME_END', '2023-05-18T22:10:00Z')
    loki_url = os.environ.get('LOKI_URL', 'http://localhost:3100')
    mode = os.environ.get('MODE', 'file')
    prefix_output_dir = os.environ.get('PREFIX_OUTPUT_DIR', './output/test230519/')

    if not os.path.exists(prefix_output_dir):
        os.makedirs(prefix_output_dir)

    print("Parameters: ")
    print("Applications: ", applications)
    print("Log period: ", log_period)
    print("Baseline start at: ", baseline_time_start)
    print("Baseline end at: ", baseline_time_end)
    print("Loki URL: ", loki_url)
    print("\n")

    loki_client = Client(base_url=loki_url)
    
    scores = {}

    for app in applications:
        filename = prefix_output_dir + app + '-baseline-score.pkl'
        if mode == 'file':
            score = file_scoring(filename)
        else:
            score = loki_scoring(loki_client, app, baseline_time_start, baseline_time_end, log_period, filename)
        scores[app] = score

    autoencoder, threshold = model_training(scores, prefix_output_dir)

    print("Model Summary: ")
    autoencoder.summary()

    print("\n")
    print("Finished training...")
    print("Time end: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Total time: ", datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(starting_time, '%Y-%m-%d %H:%M:%S'))

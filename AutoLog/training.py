import os, datetime, subprocess, logging
import pandas as pd
from src.logger import get_logs
from src.scoring import Scoring
from src.model import MultilayerAutoEncoder
from grafana_loki_client import Client
from sklearn.preprocessing import MinMaxScaler

def file_scoring(filename):
    logging.info("Reading baseline score from " + str(filename))
    scoring = Scoring()
    scoring.load(filename)
    return scoring.calculate_baseline_score()

def loki_scoring(loki_client, app, baseline_time_start, baseline_time_end, log_period, save_path=None):
    logging.info("Collecting & scoring baseline logs for " + str(app))
    logging.info("Time: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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

    logging.info("Finished scoring baseline logs for " + str(app))
    logging.info("Time: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    return scoring.calculate_baseline_score()

def model_training(scores, save_path=None):
    logging.info("Training model...")
    logging.info("Time: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    df = pd.DataFrame.from_dict(scores)
    x_train = df.values
    scaler = MinMaxScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    input_dim = x_train.shape[1]
    autoencoder = MultilayerAutoEncoder(input_dim = input_dim)
    history, threshold = autoencoder.train(x_train_scaled, x_train_scaled)

    if save_path is not None:
        autoencoder.save_model(save_path)

    logging.info("Finished training model...")
    logging.info("Time: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    return autoencoder, threshold

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    starting_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info("Starting training...")
    logging.info("Time start: " + str(starting_time))

    applications = os.environ.get('APPLICATIONS', 'frontend cartservice productcatalogservice currencyservice paymentservice shippingservice emailservice checkoutservice recommendationservice adservice').split(' ')
    log_period = int(os.environ.get('LOG_PERIOD', 10))
    baseline_time_start = os.environ.get('BASELINE_TIME_START', '2023-05-18T10:00:00Z')
    baseline_time_end = os.environ.get('BASELINE_TIME_END', '2023-05-19T10:00:00Z')
    loki_url = os.environ.get('LOKI_URL', 'http://localhost:3100')
    mode = os.environ.get('MODE', 'loki')
    prefix_output_dir = os.environ.get('PREFIX_OUTPUT_DIR', './model/')
    gcs_bucket = os.environ.get('GCS_BUCKET', 'autolog-gke')
    environment = os.environ.get('ENVIRONMENT', 'local')

    if environment != 'local':
        subprocess.run(['echo', os.environ.get('GCLOUD_SERVICE_ACCOUNT'), '>', '/etc/gcloud/service-account.json'])
        subprocess.run(['gcloud', 'auth', 'activate-service-account', '--key-file=/etc/gcloud/service-account.json'])

    if not os.path.exists(prefix_output_dir):
        os.makedirs(prefix_output_dir)

    logging.info("Parameters: ")
    logging.info("Applications: " + str(applications))
    logging.info("Log period: " + str(log_period))
    logging.info("Baseline start at: " + str(baseline_time_start))
    logging.info("Baseline end at: " + str(baseline_time_end))
    logging.info("Loki URL: " + str(loki_url))

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

    logging.info("Pushing model folder to GCS...")
    subprocess.run(['gsutil', '-m', 'cp', '-r', prefix_output_dir, 'gs://' + gcs_bucket])

    logging.info("Finished training...")
    logging.info("Time end: " + str( datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    logging.info("Total time: " + str( datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(starting_time, '%Y-%m-%d %H:%M:%S')))

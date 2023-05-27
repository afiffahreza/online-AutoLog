import os, datetime, time, subprocess, logging
import pandas as pd
from src.logger import get_logs
from src.scoring import Scoring
from src.model import MultilayerAutoEncoder
from grafana_loki_client import Client
from prometheus_client import start_http_server, Enum

def serve_scoring(loki_client, app, current_time, log_period, filename):

    scoring = Scoring()
    scoring.load(filename)

    time_start = datetime.datetime.strptime(current_time, '%Y-%m-%dT%H:%M:%SZ') - datetime.timedelta(seconds=log_period)
    time_start = time_start.strftime('%Y-%m-%dT%H:%M:%SZ')
    lines = get_logs(loki_client, app, time_start, current_time)

    return scoring.calculate_score(lines)

def model_serving(autoencoder, scores):
    df = pd.DataFrame(scores, index=[0])
    x = df.values
    anomaly, RE = autoencoder.predict(x, autoencoder.threshold)
    return anomaly[0], RE[0]

if __name__ == "__main__":

    applications = os.environ.get('APPLICATIONS', 'frontend cartservice productcatalogservice currencyservice paymentservice shippingservice emailservice checkoutservice recommendationservice adservice').split(' ')
    log_period = int(os.environ.get('LOG_PERIOD', 10))
    loki_url = os.environ.get('LOKI_URL', 'http://localhost:3100')
    prefix_output_dir = os.environ.get('PREFIX_OUTPUT_DIR', './model/')
    gcs_bucket = os.environ.get('GCS_BUCKET', 'autolog-gke')
    environment = os.environ.get('ENVIRONMENT', 'local')

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if environment != 'local':
        logging.info("Running on GKE")
        subprocess.run(['echo', os.environ.get('GCLOUD_SERVICE_ACCOUNT'), '>', '/etc/gcloud/service-account.json'])
        subprocess.run(['gcloud', 'auth', 'activate-service-account', '--key-file=/etc/gcloud/service-account.json'])
    
    if not os.path.exists(prefix_output_dir):
        os.makedirs(prefix_output_dir)
    
    last_path = prefix_output_dir.split('/')[-2]
    logging.info("Downloading model from GCS bucket")
    subprocess.run(['gsutil', '-m', 'cp', '-r', 'gs://' + gcs_bucket + '/' + last_path + '/*', prefix_output_dir])

    logging.info("Parameters: ")
    logging.info("Applications: " + str(applications))
    logging.info("Log period: " + str(log_period))
    logging.info("Loki URL: " + loki_url)

    loki_client = Client(base_url=loki_url)
    autoencoder = MultilayerAutoEncoder()
    autoencoder.load_model(prefix_output_dir)
    logging.info("Model loaded")
    logging.info("Threshold: " + str(autoencoder.threshold))

    start_http_server(8000)
    anomaly_metric = Enum('autolog_anomaly', 'Anomaly metric', states=['normal', 'anomaly'])

    time_start = datetime.datetime.now()
    
    while True:
        scores = {}
        tz = datetime.timezone(datetime.timedelta(hours=0))
        current_time = datetime.datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%SZ')
        for app in applications:
            filename = prefix_output_dir + app + '-baseline-score.pkl'
            scores[app] = serve_scoring(loki_client, app, current_time, log_period, filename)
        
        anomaly, reconstruction_error = model_serving(autoencoder, scores)
        logging.info("Reconstruction error: " + str(reconstruction_error) + " | Anomaly: " + str(anomaly))

        del scores

        anomaly_metric.state('anomaly' if anomaly == 1 else 'normal')

        time.sleep(log_period - ((datetime.datetime.now() - time_start).total_seconds() % log_period))

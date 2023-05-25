import os, datetime, time
import pandas as pd
from src.logger import get_logs
from src.scoring import Scoring
from src.model import MultilayerAutoEncoder
from grafana_loki_client import Client
from prometheus_client import start_http_server, Enum

def serve_scoring(loki_client, app, log_period, filename):

    scoring = Scoring()
    scoring.load(filename)

    tz = datetime.timezone(datetime.timedelta(hours=0))
    time_end = datetime.datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%SZ')
    time_start = datetime.datetime.strptime(time_end, '%Y-%m-%dT%H:%M:%SZ') - datetime.timedelta(seconds=log_period)
    time_start = time_start.strftime('%Y-%m-%dT%H:%M:%SZ')
    lines = get_logs(loki_client, app, time_start, time_end)

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

    print("Parameters: ")
    print("Applications: ", applications)
    print("Log period: ", log_period)
    print("Loki URL: ", loki_url)
    print("\n")

    loki_client = Client(base_url=loki_url)
    autoencoder = MultilayerAutoEncoder()
    autoencoder.load_model(prefix_output_dir)

    start_http_server(8000)
    anomaly_metric = Enum('autolog_anomaly', 'Anomaly metric', states=['normal', 'anomaly'])

    print("Threshold: ", autoencoder.threshold)

    time_start = datetime.datetime.now()
    
    while True:
        scores = {}
        for app in applications:
            filename = prefix_output_dir + app + '-baseline-score.pkl'
            scores[app] = serve_scoring(loki_client, app, log_period, filename)
        
        anomaly, reconstruction_error = model_serving(autoencoder, scores)
        print("Reconstruction error: ", reconstruction_error, " | Anomaly: ", anomaly)

        anomaly_metric.state('anomaly' if anomaly == 1 else 'normal')

        time.sleep(log_period - ((datetime.datetime.now() - time_start).total_seconds() % log_period))

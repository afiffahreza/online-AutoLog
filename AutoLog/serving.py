import os, datetime, time
import pandas as pd
from src.logger import get_logs
from src.scoring import Scoring
from src.model import load_model
from grafana_loki_client import Client

def serve_scoring(loki_client, app, log_period, filename):

    scoring = Scoring()
    scoring.load(filename)

    tz = datetime.timezone(datetime.timedelta(hours=0))
    time_end = datetime.datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%SZ')
    time_start = datetime.datetime.strptime(time_end, '%Y-%m-%dT%H:%M:%SZ') - datetime.timedelta(seconds=log_period)
    time_start = time_start.strftime('%Y-%m-%dT%H:%M:%SZ')
    lines = get_logs(loki_client, app, time_start, time_end)

    return scoring.calculate_score(lines)

def model_serving(scores, filename):
    print("Detecting anomalousness...")
    print("Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    autoencoder = load_model(filename)
    df = pd.DataFrame.from_dict(scores)
    x = df.values
    anomaly = autoencoder.predict(x)

    print("Finished training model...")
    print("Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return anomaly

if __name__ == "__main__":

    applications = os.environ.get('APPLICATIONS', 'frontend cartservice productcatalogservice currencyservice paymentservice shippingservice emailservice checkoutservice recommendationservice adservice').split(' ')
    log_period = int(os.environ.get('LOG_PERIOD', 10))
    loki_url = os.environ.get('LOKI_URL', 'http://localhost:3100')
    prefix_output_dir = os.environ.get('PREFIX_OUTPUT_DIR', './output/test230519/')

    print("Parameters: ")
    print("Applications: ", applications)
    print("Log period: ", log_period)
    print("Loki URL: ", loki_url)
    print("\n")

    loki_client = Client(base_url=loki_url)
    
    while True:
        scores = {}
        for app in applications:
            filename = prefix_output_dir + app + '-baseline-score.pkl'
            scores[app] = serve_scoring(loki_client, app, log_period, filename)
        
        print("Scores: ", scores)

        time.sleep(log_period)

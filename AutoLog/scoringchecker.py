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
    scoring.print_terms()
    print("\n")
    return scoring.calculate_baseline_score()

if __name__ == "__main__":

    starting_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("Starting training...")
    print("Time start: ", starting_time)
    print("\n")

    applications = os.environ.get('APPLICATIONS', 'frontend cartservice productcatalogservice currencyservice paymentservice shippingservice emailservice checkoutservice recommendationservice adservice').split(' ')
    prefix_output_dir = os.environ.get('PREFIX_OUTPUT_DIR', './output/test230521/')

    if not os.path.exists(prefix_output_dir):
        os.makedirs(prefix_output_dir)

    print("Parameters: ")
    print("Applications: ", applications)
    print("\n")

    scores = {}

    for app in applications:
        filename = prefix_output_dir + app + '-baseline-score.pkl'
        score = file_scoring(filename)
        scores[app] = score

    print("\n")
    print("Finished training...")
    print("Time end: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Total time: ", datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(starting_time, '%Y-%m-%d %H:%M:%S'))

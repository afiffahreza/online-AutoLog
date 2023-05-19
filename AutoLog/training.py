import os, datetime
from src.logger import get_logs
from src.scoring import Scoring
from src.model import MultilayerAutoEncoder
from grafana_loki_client import Client

if __name__ == "__main__":

    print("Starting training...")
    print("Time start: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("\n")

    applications = os.environ.get('APPLICATIONS', 'frontend cartservice').split(' ')
    # applications = os.environ.get('APPLICATIONS', 'frontend cartservice productcatalogservice currencyservice paymentservice shippingservice emailservice checkoutservice recommendationservice adservice').split(' ')
    log_period = int(os.environ.get('LOG_PERIOD', 10))
    baseline_time_start = os.environ.get('BASELINE_TIME_START', '2023-05-18T10:00:00Z')
    baseline_time_end = os.environ.get('BASELINE_TIME_END', '2023-05-18T11:00:00Z')
    loki_url = os.environ.get('LOKI_URL', 'http://localhost:3100')

    print("Applications: ", applications)
    print("Log period: ", log_period)
    print("Baseline start at: ", baseline_time_start)
    print("Baseline end at: ", baseline_time_end)
    print("Loki URL: ", loki_url)

    print("\n")

    loki_client = Client(base_url=loki_url)
    
    # Collecting Baseline Logs
    scores = {}
    for app in applications:
        print("Collecting baseline logs for", app)
        print("Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        time_start = baseline_time_start

        logs = []

        scoring = Scoring()

        while time_start < baseline_time_end:
            time_end = datetime.datetime.strptime(time_start, '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(seconds=log_period)
            time_end = time_end.strftime('%Y-%m-%dT%H:%M:%SZ')
            lines = get_logs(loki_client, app, time_start, time_end)
            scoring.add_lines(lines)
            time_start = time_end
        
        print("Scoring baseline logs for", app)
        print("Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        score = scoring.calculate_baseline_score()
        scoring.save('./output/test230519/'+app+'-baseline-score.pkl')
        scores[app] = score

        print("Finished collecting baseline logs for", app)
        print("Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("\n")

    print("Baseline scores: ", scores)
    print("Time end: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

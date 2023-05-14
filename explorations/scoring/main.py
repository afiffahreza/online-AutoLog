import os, time
from datetime import datetime, timedelta, timezone
from app.baseline import baseline_storing, baseline_training, baseline_reset
from app.scoring import scoring
from app.logger import log_generator, log_remover
from app.anomaly_detection import start_anomaly_detection, trigger_anomaly_detection

if __name__ == "__main__":

    print("Starting scoring service...\n\n")

    applications = os.environ.get('APPLICATIONS', 'catalog customer order ingress-nginx').split(' ')
    target_num_baseline = int(os.environ.get('TARGET_NUM_BASELINE', 10))
    log_period = int(os.environ.get('LOG_PERIOD', 10))
    reset_baseline = os.environ.get('RESET_BASELINE', 0)
    anomaly_detector_url = os.environ.get('ANOMALY_DETECTOR_URL', 'standalone')
    baselien_start_timerange = os.environ.get('BASELINE_START_TIMERANGE', '')
    baseline_end_timerange = os.environ.get('BASELINE_END_TIMERANGE', '')

    print("Applications: ", applications)
    print("Target number of baseline: ", target_num_baseline)
    print("Log period: ", log_period)

    print("\n")

    # Reset baseline
    if reset_baseline == 1:
        print("Resetting baseline...")
        for app in applications:
            baseline_reset(app)
        print("Resetting baseline done")
        print("\n")

    # Collecting Baseline Logs
    current_num_baseline = 0
    while current_num_baseline < target_num_baseline:
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ten_seconds_ago = (datetime.now(timezone.utc) - timedelta(seconds=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        print("Collecting baseline logs...")
        print(f"Current number of baseline at {current_time} : {current_num_baseline} / {target_num_baseline}")
        print("\n")

        for app in applications:
            log = log_generator(app, current_time, ten_seconds_ago)
            print("Storing baseline for ", app)
            baseline_storing(log, app)
            print("Storing baseline for ", app, " done")
            print("\n")
            log_remover(app, current_time)
        current_num_baseline += 1
        time.sleep(log_period)
    
    # Training Baseline
    for app in applications:
        print("Training baseline for ", app)
        baseline_training(app)
        print("Training baseline for ", app, " done")
        print("\n")
    
    if anomaly_detector_url != "standalone":
        start_anomaly_detection(anomaly_detector_url)

    # Scoring
    while True:
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ten_seconds_ago = (datetime.now(timezone.utc) - timedelta(seconds=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        print("Scoring...")
        print(f"Current time: {current_time}")
        for app in applications:
            log = log_generator(app, current_time, ten_seconds_ago)
            print("Scoring ", app)
            scoring(log, app)
            print("Scoring ", app, " done")
            print("\n")
            log_remover(app, current_time)
        if anomaly_detector_url != "standalone":
            trigger_anomaly_detection(anomaly_detector_url)
        time.sleep(log_period)
    
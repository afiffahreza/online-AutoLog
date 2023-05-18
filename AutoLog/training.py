import os, time, datetime, json, sys
from src.logger import log_generator, log_remover, read_log, preprocess
from src.scoring import Scoring
from src.model import MultilayerAutoEncoder
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from drain3.file_persistence import FilePersistence


if __name__ == "__main__":

    print("Starting training...\n\n")

    applications = os.environ.get('APPLICATIONS', 'frontend cartservice productcatalogservice').split(' ')
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

    persistence = FilePersistence("drain3_state.bin")

    config = TemplateMinerConfig()
    config.load(os.path.dirname(__file__) + "/drain3.ini")
    config.profiling_enabled = False

    
    # Collecting Baseline Logs
    scores = {}
    for app in applications:
        time_start = baseline_time_start

        template_miner = TemplateMiner(persistence, config)
        logs = []

        while time_start < baseline_time_end:
            time_end = datetime.datetime.strptime(time_start, '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(seconds=log_period)
            time_end = time_end.strftime('%Y-%m-%dT%H:%M:%SZ')
            logfile = log_generator(app, time_start, time_end, loki_url)
            lines = read_log(logfile)
            logs.append(lines)
            log_remover(app, time_start)
            time_start = time_end

            for line in lines:
                template_miner.add_log_message(line)
        
        scoring = Scoring()

        for lines in logs:
            current_lines = []
            for line in lines:
                result = template_miner.match(line)
                template = result.get_template()
                if template is not None:
                    current_lines.append(template)
                else:
                    current_lines.append(line)
            scoring.add_lines(preprocess(current_lines))
        
        score = scoring.calculate_baseline_score()
        scoring.save('./output/test230518/'+app+'-baseline-score.pkl')
        scores[app] = score

    print("Baseline scores: ", scores)


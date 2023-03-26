import sys
from baseline import baseline
from scoring import score_baseline, score_trained

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: spark-submit scoring.py <mode> <logfile> <app>")
        print("Example: spark-submit scoring.py baseline dataset/logs.txt app1")
        exit(-1)
    mode = sys.argv[1]
    logfile = sys.argv[2]
    app = sys.argv[3]
    if mode == "baseline":
        baseline(logfile, app)
    elif mode == "score_baseline":
        score_baseline(logfile, app)
    elif mode == "score_trained":
        score_trained(logfile, app)
import sys
from baseline import baseline_storing, baseline_training
from scoring import scoring

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("ERROR! Invalid number of arguments")
        print("Usage: python3 main.py <mode> <app> <logfile>")
        print("Example: python3 main.py baseline app1 dataset/logs.txt")
        print("Available modes: baseline, train, scoring")
        exit(-1)
    mode = sys.argv[1]
    app = sys.argv[2]
    logfile = sys.argv[3]
    if mode == "baseline":
        baseline_storing(logfile, app)
    elif mode == "training":
        baseline_training(logfile, app)
    elif mode == "scoring":
        scoring(logfile, app)
    else:
        print("ERROR! Invalid mode")
        print("Available modes: baseline, train, scoring")
        exit(-1)
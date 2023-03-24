import sys
from baseline import baseline

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: spark-submit main.py <mode> <logfile> <app>")
        print("Example: spark-submit main.py baseline dataset/logs.txt app1")
        exit(-1)
    mode = sys.argv[1]
    logfile = sys.argv[2]
    app = sys.argv[3]
    if mode == "baseline":
        baseline(logfile, app)
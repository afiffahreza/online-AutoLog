import requests

def start_anomaly_detection(url):
    print("Sending signal done to anomaly detector...")
    requests.post(url + "/done")

def trigger_anomaly_detection(url):
    print("Sending trigger to anomaly detector...")
    requests.post(url + "/trigger")

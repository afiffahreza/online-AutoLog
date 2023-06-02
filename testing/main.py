from prometheus_client import Enum, make_asgi_app, Counter
from fastapi import FastAPI
from fault_injector import inject_faults
import threading, logging

# Create app
app = FastAPI(debug=False)

# Add prometheus asgi middleware to route /metrics requests
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

anomaly_metric = Enum(
    'autolog_injected_anomaly', 'Anomaly metric',
    states=['normal', 'anomaly']
)

# Counter to track the number of injected anomalies
injected_anomalies = Counter('injected_anomalies', 'Number of injected anomalies')

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s')

# /fault endpoint to inject anomaly
@app.post("/fault")
async def faults():
    # check if there is a thread running
    if threading.active_count() > 1:
        return {"message": "Anomalies already injected"}
    # start a thread to inject anomalies
    threading.Thread(target=inject_faults, args=(anomaly_metric, injected_anomalies)).start()
    return {"message": "Anomalies injected"}

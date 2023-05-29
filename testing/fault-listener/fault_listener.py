from prometheus_client import Enum, make_asgi_app, Counter
from fastapi import FastAPI

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

# /fault endpoint to inject anomaly
@app.post("/fault")
async def inject_anomaly():
    anomaly_metric.state('anomaly')
    injected_anomalies.inc()
    return {"message": "Anomaly injected"}

# /reset endpoint to reset anomaly
@app.post("/reset")
async def reset_anomaly():
    anomaly_metric.state('normal')
    return {"message": "Anomaly reset"}

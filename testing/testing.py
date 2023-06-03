import os
from prometheus_api_client import PrometheusConnect

prometheus_host = os.environ.get('PROMETHEUS_HOST', 'http://localhost:9090')

prom = PrometheusConnect(url=prometheus_host, disable_ssl=True)

# Get the list of all the metrics that the Prometheus host scrapes
print(prom.all_metrics())

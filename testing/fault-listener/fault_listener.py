from flask import Flask
from prometheus_client import Enum, make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

app = Flask(__name__)

anomaly_metric = Enum(
    'autolog_anomaly', 'Anomaly metric',
    states=['normal', 'anomaly']
)

# Counter to track the number of injected anomalies
injected_anomalies = Counter('injected_anomalies', 'Number of injected anomalies')


@app.route('/fault', methods=['POST'])
def inject_anomaly():
    # Increment the counter for injected anomalies
    injected_anomalies.inc()

    # Set the anomaly metric to 'anomaly'
    anomaly_metric.state('anomaly')

    return {'message':'Anomaly injected successfully'}


@app.route('/reset', methods=['POST'])
def reset_anomaly():
    # Set the anomaly metric back to 'normal'
    anomaly_metric.state('normal')

    return 'Anomaly reset successfully'


def create_app():
    dispatcher_app = DispatcherMiddleware(app, {
        '/metrics': make_wsgi_app()
    })
    return dispatcher_app


if __name__ == '__main__':
    dispatcher_app = create_app()
    run_simple('localhost', 5000, dispatcher_app)

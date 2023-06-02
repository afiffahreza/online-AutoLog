import yaml, time, threading, logging, os, random
from kubernetes import config, client
from prometheus_client import Enum, Counter, start_http_server

def anomaly_metric_on(anomaly_metric, injected_anomalies):
    # set the anomaly metric to 'anomaly' and increment the injected anomalies counter after 10s that the function is called
    threading.Timer(10.0, anomaly_metric.state, args=['anomaly']).start()
    threading.Timer(10.0, injected_anomalies.inc).start()

def anomaly_metric_off(anomaly_metric):
    # set the anomaly metric to 'normal' after 10s that the function is called
    threading.Timer(10.0, anomaly_metric.state, args=['normal']).start()

def inject_anomaly(api, resource_file, target):
    resource_dict = yaml.load(open(resource_file), Loader=yaml.FullLoader)
    resource_dict['spec']['selector']['labelSelectors']['app'] = target
    name = resource_dict['metadata']['name']
    logging.info("Injecting anomaly: " + name + " to " + target)

    chaos_type = resource_file.split('/')[2]

    api.create_namespaced_custom_object(
        group="chaos-mesh.org",
        version="v1alpha1",
        namespace="default",
        plural=chaos_type,
        body=resource_dict,
    )

    logging.info("Anomaly injected")

    return name

def remove_anomaly(api, resource_file, name):
    logging.info("Removing anomaly: " + name)
    
    chaos_type = resource_file.split('/')[2]

    api.delete_namespaced_custom_object(
        group="chaos-mesh.org",
        version="v1alpha1",
        namespace="default",
        plural=chaos_type,
        name=name,
    )

    logging.info("Anomaly removed")

if __name__ == "__main__":
    applications = os.environ.get('APPLICATIONS', 'frontend cartservice productcatalogservice currencyservice paymentservice shippingservice emailservice checkoutservice recommendationservice adservice').split(' ')
    template_files_prefix = os.environ.get('TEMPLATE_FILES_PREFIX', './templates/')
    template_files = os.environ.get('TEMPLATE_FILES', 'podchaos/pod-failure.yaml podchaos/pod-kill.yaml').split(' ')
    anomaly_duration = int(os.environ.get('ANOMALY_DURATION', '10'))
    anomaly_graceful = int(os.environ.get('ANOMALY_GRACEFUL', '5'))
    anomaly_interval = int(os.environ.get('ANOMALY_INTERVAL', '60'))
    target_anomalies = int(os.environ.get('TARGET_ANOMALIES', '5'))

    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s')

    anomaly_metric = Enum(
        'autolog_injected_anomaly', 'Anomaly metric',
        states=['normal', 'anomaly']
    )
    injected_anomalies = Counter('injected_anomalies', 'Number of injected anomalies')

    start_http_server(8000)

    logging.info("Starting fault injector")
    current_anomalies = 0

    config.load_kube_config()
    api = client.CustomObjectsApi()

    while True:
        if current_anomalies < target_anomalies:
            target = random.choice(applications)
            template_file = random.choice(template_files)

            injected = inject_anomaly(api, template_files_prefix + template_file, target)
            anomaly_metric_on(anomaly_metric, injected_anomalies)

            time.sleep(anomaly_duration)
            remove_anomaly(api, template_files_prefix + template_file, injected)
            anomaly_metric_off(anomaly_metric)

            current_anomalies += 1

            logging.info("Current anomalies: " + str(current_anomalies))
            if current_anomalies == target_anomalies:
                logging.info("Target anomalies reached, fault injector stopped")

            time.sleep(anomaly_interval)

        else:
            logging.info("Target anomalies reached, fault injector stopped")
            time.sleep(3600)

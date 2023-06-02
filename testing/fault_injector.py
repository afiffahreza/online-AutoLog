import yaml, time, threading, logging
from kubernetes import config, client

def anomaly_metric_on(anomaly_metric, injected_anomalies):
    # set the anomaly metric to 'anomaly' and increment the injected anomalies counter after 10s that the function is called
    threading.Timer(10.0, anomaly_metric.state, args=['anomaly']).start()
    threading.Timer(10.0, injected_anomalies.inc).start()

def anomaly_metric_off(anomaly_metric):
    # set the anomaly metric to 'normal' after 10s that the function is called
    threading.Timer(10.0, anomaly_metric.state, args=['normal']).start()

def inject_anomaly(api, resource_file, chaos_type):
    resource_dict = yaml.load(open(resource_file), Loader=yaml.FullLoader)
    logging.info("Injecting anomaly: " + chaos_type + " with resource:" + str(resource_dict))

    api.create_namespaced_custom_object(
        group="chaos-mesh.org",
        version="v1alpha1",
        namespace="default",
        plural=chaos_type,
        body=resource_dict,
    )

    logging.info("Anomaly injected")

def remove_anomaly(api, resource_file, chaos_type):
    resource_dict = yaml.load(open(resource_file), Loader=yaml.FullLoader)
    resource_name = resource_dict['metadata']['name']
    logging.info("Removing anomaly: " + chaos_type + " with resource:" + str(resource_dict))

    api.delete_namespaced_custom_object(
        group="chaos-mesh.org",
        version="v1alpha1",
        namespace="default",
        plural=chaos_type,
        name=resource_name,
    )

    logging.info("Anomaly removed")

def inject_faults(anomaly_metric, injected_anomalies):
    config.load_kube_config()

    api = client.CustomObjectsApi()

    resource_files = [
        './podchaos/pod-failure-1.yaml',
        './podchaos/pod-kill-1.yaml',
        './stresschaos/memory-stress-1.yaml',
        './stresschaos/cpu-stress-1.yaml',
    ]

    for resource_file in resource_files:
        chaos_type = resource_file.split('/')[1].split('-')[0]
        inject_anomaly(api, resource_file, chaos_type)
        anomaly_metric_on(anomaly_metric, injected_anomalies)
        time.sleep(10)
        remove_anomaly(api, resource_file, chaos_type)
        anomaly_metric_off(anomaly_metric)

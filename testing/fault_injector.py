import yaml, time
from kubernetes import config, client

def inject_anomaly(api, resource_file, chaos_type):
    resource_dict = yaml.load(open(resource_file), Loader=yaml.FullLoader)
    print("Injecting anomaly: " + chaos_type + " with resource:")
    print(resource_dict)

    api.create_namespaced_custom_object(
        group="chaos-mesh.org",
        version="v1alpha1",
        namespace="default",
        plural=chaos_type,
        body=resource_dict,
    )

    print("Anomaly injected")

def remove_anomaly(api, resource_file, chaos_type):
    resource_dict = yaml.load(open(resource_file), Loader=yaml.FullLoader)
    resource_name = resource_dict['metadata']['name']
    print("Removing anomaly: " + chaos_type + " with resource:")
    print(resource_dict)

    api.delete_namespaced_custom_object(
        group="chaos-mesh.org",
        version="v1alpha1",
        namespace="default",
        plural=chaos_type,
        name=resource_name,
    )

    print("Anomaly removed")

if __name__ == '__main__':
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
        time.sleep(30)
        remove_anomaly(api, resource_file, chaos_type)

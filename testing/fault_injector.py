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

    print("Pod failure injected")

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

    print("Pod failure removed")

if __name__ == '__main__':
    config.load_kube_config()

    api = client.CustomObjectsApi()

    resource_file = './pod-failure/test1.yaml'
    
    inject_anomaly(api, resource_file, "podchaos")
    time.sleep(100)
    remove_anomaly(api, resource_file, "podchaos")

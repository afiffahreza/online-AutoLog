# Kubernetes

This documentation is a summary of some Kubernetes tutorials I watched on YouTube.

Links:

- [Kubernetes Tutorial for Beginners [FULL COURSE in 4 Hours] - YouTube](https://youtu.be/X48VuDVv0do)

- [Kubernetes Course - Full Beginners Tutorial (Containerize Your Apps!) - YouTube](https://youtu.be/d6WC5n9G_sM)

## Terminology and Key Features

Kubernetes (k8s) is container orchestration system: create containers on different servers automatically.

Kubernetes takes care of:

- Automatic deployment of the containerized applications across different servers

- Distribution of the load across multiple servers

- Auto scaling of the deployed applications

- Monitoring and health check of the containers

- Replacement of the failed containers

Features that orchestration tools offer:

- High availability / no downtime

- Scalability / high performance

- Disaster recovery with backup and restore

Container runtimes supported: docker (mostly used), CRI-O, containerd.

Several terminologies used a lot in k8s are pod, node, and cluster

## Main k8s Components

### Pod

Pod is the smallest unit in the k8s world. Containers are created inside the pod. There can be several containers inside a pod. There can also be shared volumes and shared IP addres inside a pod. One container per pod is the most common use case. Each pod gets its own ephemeral IP address. New IP address will be assigned on re-creation. To get a static IP address, we can use service.

### Node

Node is basically the server. Pods are created inside of the node. K8s will automatically deploy pods on different nodes. Inside of a node, there are several k8s process such as:

- Container runtime: runs container inside of each node

- Kubelet: node agent that runs on each node, it can register the node with the master api server

- Kube proxy network communication inside of each node and between nodes

There are also some processes that are exclusive to the master node such as:

- API Server: cluster gateway and the main point of communication between nodes, also acts as a gatekeeper for authentication

- Scheduler: planning the distribution of the load

- Controller Manager: single point which controls everything inside the kubernetes cluster, detects cluster state changes

- etcd: service which stores logs, cluster changes get stored in the key value store

- Cloud Controller Manager: cloud service manager (GKE, EKS, etc), this also provides IP address for services, load balancers, etc.

- DNS service: name resolution

### Cluster

Kubernetes cluster consist of nodes. In practice, k8s cluster is usually made up of multiple masters, where each master noderuns its master processes. API server inside the master nodes is load balanced and the etcd store forms a distributed storage across all master nodes.

### Service

Service is a static IP address that is attached to a Pod. The lifecycle of Pod and Service is not connected. There are 2 kinds of services, internal which is only accessible inside the node and external which is publicly accessible.

### Ingress

Ingress is used to forward URLs to services, so we don't need to use external service which URL is usually `http://service-ip:port`, not `https://app.com` which uses domain and secure protocol. 

### ConfigMap

ConfigMap is basically the external configuration of application. For example, we can store database URL by connecting it to a service, so that we don't need to rebuild the application image that used the DB everytime the DB re-creates.

### Secret

Secret is used to store secret data like credentials, not in a plain text format but in base64 encoded.

### Volume

It attaches a storage (local/physical or remote) to a pod, so when it restarts, it won't lose any data. K8s doesn't manage data persistance.

### Deployment

Deployment is a blueprint for any application pods. In practice, we don't really create pods and instead, we create deployments. In deployments, we can specify of how many replicas of a pod we want, which will be distributed in different nodes. Service that is connected to the pod and its replicas will be acting as a load balancer. Replicas is also used for backup if any of the pods failed.

**Deployment is used for stateless apps!**

### StatefulSet

DB and any stateful app can't be replicated via deployment because database has state and they all need to access the same shared data storage to avoid data inconsistencies. DB are often hosted outside of k8s cluster because it's not easy to deploy a StatefulSet.

**StatefulSet is used for Stateful apps or databases!**

## MiniKube and kubectl

MiniKube is used for testing cluster setup locally by creating a virtual environment and the cluster nodes will run inside it.

kubectl is a command line tool for k8s cluster.

### Main `kubectl` Commands

- List any resource
  `kubectl get [pods/services/nodes/replicaset]`

- Create deployment
  `kubectl create deployment NAME --image=image`

- Edit deployment
  `kubectl edit deployment NAME`

- Get logs from a pod
  `kubectl logs POD_NAME`

- Describe pods
  `kubectl describe pod POD_NAME`

- Interactive Terminal
  `kubectl exec -it POD_NAME -- bin/bash`

- Delete pods (by deleting the deployment)
  `kubectl delete deployment DEPLOYMENT_NAME`

- Create or Update resources using configuration file
  `kubectl apply -f CONFIG-FILE.yaml`

- Delete resources using configuration file
  `kubectl delete -f CONFIG-FILE.yaml`

## Kubernetes YAML Configuration File

Each configuration file has 3 parts:

1. metadata (name, labels, etc)

2. specification, where its attributes are specific to the kind

3. status (automatically generated and edited by k8s) --> basis of the self healing

The following is an example of a Deployment configuration. It creates a ReplicaSet to bring up three nginx Pods.  

```yaml
# nginx-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

In this example:  

- A Deployment named nginx-deployment is created, indicated by the `.metadata.name field.`

- The Deployment creates three replicated Pods, indicated by the `.spec.replicas` field.

- The `.spec.selector` field defines how the Deployment finds which Pods to manage. In this case, you select a label that is defined in the Pod template (`app: nginx`). However, more sophisticated selection rules are possible, as long as the Pod template itself satisfies the rule.

- The template field contains the following sub-fields:
  
  - The Pods are labeled `app: nginx` using the `.metadata.labels field`.
  
  - The Pod template's specification, or `.template.spec` field, indicates that the Pods run one container, nginx, which runs the nginx Docker Hub image at version 1.14.2.
  
  - Create one container and name it nginx using the `.spec.template.spec.containers[0].name` field.

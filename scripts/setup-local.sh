#!/bin/bash
set -e

# Create kind cluster
kind create cluster --config k8s/local/cluster.yaml

# Change k8s context to kind
kubectx kind-autolog

# Apply loki stack
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
kubectl apply -f k8s/loki-stack/namespace.yaml
helm upgrade --values k8s/loki-stack/values.yaml --install loki -n loki-stack grafana/loki-stack

# Apply microservice demo
kubectl apply -k k8s/microservices/overlays/local

# Apply ingress-nginx controllers & ingresses
kubectl apply -k k8s/ingress-nginx/overlays/local

# Apply couchdb for autolog
helm repo add couchdb https://apache.github.io/couchdb-helm
helm repo update
helm upgrade --values k8s/online-autolog/couchdb/values.yaml --install couchdb --version=3.3.1 -n online-autolog couchdb/couchdb

# Print grafana password
echo "Grafana password: $(kubectl get secret loki-grafana -n loki-stack -o jsonpath="{.data.admin-password}" | base64 --decode ; echo)"

# Print couchdb password
echo "Couchdb password: $(kubectl get secret couchdb -n online-autolog -o jsonpath="{.data.adminPassword}" | base64 --decode ; echo)"

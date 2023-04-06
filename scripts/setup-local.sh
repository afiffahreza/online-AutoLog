#!/bin/bash
set -e

# Create kind cluster
kind create cluster --config k8s/local/cluster.yaml

# Change k8s context to kind
kubectx kind-autolog

# Apply ingress-nginx controllers
kubectl apply -k k8s/ingress-nginx/overlays/local

# Apply loki stack
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
kubectl apply -k k8s/loki-stack/overlays/local/
helm upgrade --values k8s/loki-stack/values.yaml --install loki -n loki-stack grafana/loki-stack

# Apply microservice demo
kubectl apply -k k8s/microservices/overlays/local

# Apply couchdb for autolog
helm repo add couchdb https://apache.github.io/couchdb-helm
helm repo update
kubectl apply -f k8s/online-autolog/base/namespace.yaml
helm upgrade --values k8s/online-autolog/couchdb/values.yaml --install couchdb --version=4.2.0 -n online-autolog couchdb/couchdb

# Apply autolog
# kubectl apply -k k8s/online-autolog/overlays/local/

# Print grafana password
echo "Grafana password: $(kubectl get secret loki-grafana -n loki-stack -o jsonpath="{.data.admin-password}" | base64 --decode ; echo)"

# Print couchdb password
echo "AutoLog Couchdb password: $(kubectl get secret couchdb-couchdb -n online-autolog -o jsonpath="{.data.adminPassword}" | base64 --decode ; echo)"

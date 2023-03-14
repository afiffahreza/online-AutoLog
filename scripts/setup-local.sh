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

# Print grafana password
echo "Grafana password: $(kubectl get secret loki-grafana -n loki-stack -o jsonpath="{.data.admin-password}" | base64 --decode ; echo)"

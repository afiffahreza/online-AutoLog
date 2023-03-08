#!/bin/bash
set -e

# Get current directory
pwd=$(pwd)

# Create kind cluster
kind create cluster --config $pwd/k8s/local/cluster.yaml

# Change k8s context to kind
kubectx kind-autolog

# Apply loki stack
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
kubectl apply -f $pwd/k8s/loki-stack/namespace.yaml
helm upgrade --values k8s/loki-stack/values.yaml --install loki -n loki-stack grafana/loki-stack

# Apply apps
kubectl apply -k $pwd/k8s/app/echo-app/overlays/local
kubectl apply -k $pwd/k8s/app/error-app/overlays/local
kubectl apply -k $pwd/k8s/app/list-app/overlays/local

# Apply ingress-nginx controllers & ingress
kubectl apply -k $pwd/k8s/ingress-nginx/overlays/local
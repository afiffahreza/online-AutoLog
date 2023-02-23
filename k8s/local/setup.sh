#!/bin/bash

# Get current directory
pwd=$(pwd)

# Create kind cluster
kind create cluster --config $pwd/k8s/local/cluster.yaml

# Change k8s context to kind
kubectx kind-autolog

# Apply ingress-nginx controllers & ingress
kubectl apply -k $pwd/k8s/ingress-nginx/overlays/local

# Apply apps
kubectl apply -k $pwd/k8s/app/helloworld/overlays/local
kubectl apply -k $pwd/k8s/app/echo/overlays/local
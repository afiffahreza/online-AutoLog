#!/bin/bash
set -e

kubectx kind-autolog

# Get Grafana password
kubectl get secret loki-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
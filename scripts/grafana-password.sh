#!/bin/bash
set -e

kx kind-autolog

# Get Grafana password
kg secret loki-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
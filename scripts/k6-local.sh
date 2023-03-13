#!/bin/bash
set -e

docker run --net="host" -i --rm grafana/k6 run - <k6/script.js
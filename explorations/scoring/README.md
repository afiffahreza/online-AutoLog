# AutoLog Scoring Component
This component is responsible for scoring logs. It is a simple Python script that reads the data from txt file, scores it and writes the results to a Couch database.

## Usage
`python3 main.py`

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `APPLICATIONS` | List of applications to be scored in string, separated by space. | `"catalog customer order ingress-nginx"` |
| `TARGET_NUM_BASELINE` | Number of chunk for each application needed before changin into scoring mode. | `10` |
| `LOG_PERIOD` | Period of taking in logs and scoring it in second. | `10` |
| `RESET_BASELINE` | Reset the baseline database when set to 1. | `0` |
| `ANOMALY_DETECTOR_URL` | URL of the anomaly detection applications which trigger will be sent to. | `http://localhost/anomaly-detection` |
| `LOKI_URL` | URL of the Loki database. | `"http://localhost/loki"` |
| `COUCHDB_URL` | URL of the CouchDB database. | `"http://localhost:5984"` |
| `COUCHDB_USER` | Username of the CouchDB database. | `"admin"` |
| `COUCHDB_PASSWORD` | Password of the CouchDB database. | `"password"` |
| `DEBUG` | Set to 1 to enable debug mode. | `0` |

## Log Retriever - Shell Mode Documentation (Deprecated)

We will be using LogCLI to retrieve logs from Loki. LogCLI is a command line tool that allows you to query logs from Loki. It is a simple tool that can be used to query logs from Loki. It is a simple tool that can be used to query logs from Loki.

### Setup
`export LOKI_ADDR=http://localhost/loki`

### Querying Logs
`logcli query '{app="loki"}' --limit=5000` 

### Querying Logs with time range
`logcli query '{app="loki"}' --from=2020-01-01T00:00:00Z --to=2020-01-01T00:00:00Z --limit=5000`

### Getting current time with the format required by LogCLI
`date -u +"%Y-%m-%dT%H:%M:%SZ"`

### Querying Logs with time range last 10s using date
`logcli query '{app="loki"}' --from=$(date -u +"%Y-%m-%dT%H:%M:%SZ" -d "10 seconds ago") --to=$(date -u +"%Y-%m-%dT%H:%M:%SZ") --limit=5000`

### Outputting logs to a file
`logcli query '{app="loki"}' --limit=5000 > logs.txt`

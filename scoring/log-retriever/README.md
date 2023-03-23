# Log Retriever

We will be using LogCLI to retrieve logs from Loki. LogCLI is a command line tool that allows you to query logs from Loki. It is a simple tool that can be used to query logs from Loki. It is a simple tool that can be used to query logs from Loki.

## Setup
`export LOKI_ADDR=http://localhost/loki`

## Querying Logs
`logcli query '{app="loki"}' --limit=5000` 

## Querying Logs with time range
`logcli query '{app="loki"}' --from=2020-01-01T00:00:00Z --to=2020-01-01T00:00:00Z --limit=5000`

## Getting current time with the format required by LogCLI
`date -u +"%Y-%m-%dT%H:%M:%SZ"`

## Querying Logs with time range last 10s using date
`logcli query '{app="loki"}' --from=$(date -u +"%Y-%m-%dT%H:%M:%SZ" -d "10 seconds ago") --to=$(date -u +"%Y-%m-%dT%H:%M:%SZ") --limit=5000`

## Outputting logs to a file
`logcli query '{app="loki"}' --limit=5000 > logs.txt`
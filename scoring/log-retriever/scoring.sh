#!/bin/bash
set -e

# Get arguments
machine=$1

# Create temp directory called output if it doesn't exist
if [ ! -d ./log-retriever/output ]; then
    mkdir ./log-retriever/output
fi

# Create state file if it doesn't exist
if [ ! -f ./log-retriever/output/log_state.txt ]; then
    echo "0" > ./log-retriever/output/log_state.txt
fi

# If statefile exists, get $CURRENT_BASELINE_LOGS, else set to 0
if [ -f ./log-retriever/output/log_state.txt ]; then
    export CURRENT_BASELINE_LOGS=$(cat ./log-retriever/output/log_state.txt)
else
    export CURRENT_BASELINE_LOGS=0
fi

# Get current time and time 10 seconds ago
if [ "$machine" == "local" ]; then
    export NOW=$(gdate -u +"%Y-%m-%dT%H:%M:%SZ")
    export TEN_SECONDS_AGO=$(gdate -u +"%Y-%m-%dT%H:%M:%SZ" -d "10 seconds ago")
    export LOKI_ADDR="http://localhost/loki"
    export APPLICATIONS="catalog order customer ingress-nginx"
    export TARGET_BASELINE_LOGS=10
else
    export NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    export TEN_SECONDS_AGO=$(date -u +"%Y-%m-%dT%H:%M:%SZ" -d "10 seconds ago")
fi

# Select mode
if [ "$CURRENT_BASELINE_LOGS" -lt "$TARGET_BASELINE_LOGS" ]; then
    echo "Running baseline mode..."
    export MODE="baseline"
fi
if [ "$CURRENT_BASELINE_LOGS" -eq "$TARGET_BASELINE_LOGS" ]; then
    echo "Running training mode..."
    export MODE="training"
fi
if [ "$CURRENT_BASELINE_LOGS" -gt "$TARGET_BASELINE_LOGS" ]; then
    echo "Running scoring mode..."
    export MODE="scoring"
fi

echo "Running scoring script..."
echo "Environment variables:"

# Output Environments
echo "NOW: $NOW"
echo "TEN SECONDS AGO: $TEN_SECONDS_AGO"
echo "APPLICATIONS: $APPLICATIONS"
echo "LOKI URL: $LOKI_ADDR"
echo "TARGET NUMBER OF BASELINE LOGS: $TARGET_BASELINE_LOGS"
echo "CURRENT NUMBER OF BASELINE LOGS: $CURRENT_BASELINE_LOGS"

for app in $APPLICATIONS; do
    echo "Retrieving logs for $app..."
    query="{app=\"$app\"}"
    echo "Query: $query"
    logcli query $query --from=$TEN_SECONDS_AGO --to=$NOW --limit=5000 > ./log-retriever/output/$app-log-$NOW.txt
    python3 main.py $MODE $app ./log-retriever/output/$app-log-$NOW.txt
done

# Update state file if mode is baseline or training
if [ "$MODE" == "baseline" ] ||  [ "$MODE" == "training" ]; then
    echo "Updating state file..."
    echo "Current baseline logs: $CURRENT_BASELINE_LOGS"
    export CURRENT_BASELINE_LOGS=$(($CURRENT_BASELINE_LOGS + 1))
    echo $CURRENT_BASELINE_LOGS > ./log-retriever/output/log_state.txt
fi

echo "Finished running scoring script."
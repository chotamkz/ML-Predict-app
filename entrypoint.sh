#!/bin/sh

set -e

trap 'kill -TERM $PID' TERM INT

echo "Starting the ML service..."
exec python main.py

PID=$!

wait $PID
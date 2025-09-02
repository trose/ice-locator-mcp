#!/bin/bash
# Script to keep the display awake during work sessions
# Usage: ./keep_awake.sh [duration_in_seconds]
# Default duration is 60 minutes (3600 seconds)

DURATION=${1:-3600}  # Default to 60 minutes if no duration specified

# Check if caffeinate is already running and stop it
EXISTING_PROCESSES=$(pgrep caffeinate)
if [ ! -z "$EXISTING_PROCESSES" ]; then
    echo "Stopping existing caffeinate processes..."
    pkill caffeinate
    sleep 1  # Give processes time to terminate
fi

echo "Keeping display awake for $DURATION seconds..."
caffeinate -u -t $DURATION &
CAFFEINATE_PID=$!

echo "Caffeinate process started with PID: $CAFFEINATE_PID"
echo "To stop manually, run: kill $CAFFEINATE_PID"
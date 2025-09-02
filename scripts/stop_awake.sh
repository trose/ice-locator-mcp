#!/bin/bash
# Script to stop caffeinate processes
# Usage: ./stop_awake.sh

echo "Stopping all caffeinate processes..."

# Check if any caffeinate processes are running
EXISTING_PROCESSES=$(pgrep caffeinate)

if [ -z "$EXISTING_PROCESSES" ]; then
    echo "No caffeinate processes found"
    exit 0
fi

echo "Found caffeinate processes: $EXISTING_PROCESSES"
pkill caffeinate

# Wait a moment and check if processes are still running
sleep 1
REMAINING_PROCESSES=$(pgrep caffeinate)

if [ -z "$REMAINING_PROCESSES" ]; then
    echo "Successfully stopped all caffeinate processes"
else
    echo "Warning: Some processes may still be running: $REMAINING_PROCESSES"
    echo "Force killing remaining processes..."
    pkill -9 caffeinate
    echo "Force kill completed"
fi
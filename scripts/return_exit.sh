#!/bin/bash

LOG="/home/luis/work/thesis/api/log"
echo "" > "$LOG"

exit_return() {
  # Perform the PUT request indicating the exit return value
  local task_id=$1
  local exit_value=$2
  local url="https://5289-213-22-250-155.ngrok.io/ci_task"

  local body="{ \"task_id\": \"$TASK_ID\", \"exit_code\": \"$exit_value\" }"
  local put_response=$(curl -X PUT -H "Content-Type: application/json" -d "$body" "$url")
  if [ -z "$put_response" ]; then
    echo "PUT request failed or received empty response."
    exit 1
  fi

  exit $exit_value
}

# Function to execute a command with error handling
execute_command() {
  local cmd="$1"
  # local error_message="$2"
  echo "CI Executing: $cmd" >> $LOG
  eval "$cmd" >> $LOG
  result=$?
  if [ $result -ne 0 ]; then
    # echo "$error_message"
    exit_return $TASK_ID 1
  fi
}
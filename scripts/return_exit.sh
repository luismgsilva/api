#!/bin/bash

exit_return() {
  # Perform the PUT request indicating the exit return value
  local task_id=$1
  local exit_value=$2
  local url="https://90cb-213-22-250-155.ngrok.io/ci_task"

  local body="{ \"task_id\": \"$TASK_ID\", \"exit_code\": \"$exit_value\" }"
  local put_response=$(curl -X PUT -H "Content-Type: application/json" -d "$body" "$url")
  if [ -z "$put_response" ]; then
    echo "PUT request failed or received empty response."
    exit 1
  fi

  exit $exit_value
}
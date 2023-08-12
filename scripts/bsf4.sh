#!/bin/bash

source "/home/luis/work/thesis/api/scripts/return_exit.sh"
TASK_NAME=$1
TASK_ID=$2

# Example usage of execute_command function
execute_command "echo $TASK_NAME" #\
  # "Failed to echo TASK NAME."

execute_command "export PATH=\"/home/luis/work/bsf/bsf-main:\$PATH\"" #\
  # "Failed to set PATH."

# Read and execute the commands from commands_to_import.txt
while IFS= read -r cmd
do
  execute_command "$cmd"
done < "scripts/$TASK_NAME.txt"

exit_return $TASK_ID 0

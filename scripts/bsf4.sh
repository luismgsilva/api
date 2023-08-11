#!/bin/bash

source "/home/luis/work/thesis/api/scripts/return_exit.sh"

TASK_NAME=$1
TASK_ID=$2

# Example usage of execute_command function
execute_command "echo $TASK_NAME" \
  "Failed to echo TASK NAME."

execute_command "export PATH=\"/home/luis/work/bsf/bsf-main:\$PATH\"" \
  "Failed to set PATH."

execute_command "cd /home/luis/work/bsf/builder" \
  "Failed to change directory to /home/luis/work/bsf/builder."

execute_command "bsf clean -y" \
  "Failed to clean BSF."

execute_command "bsf execute qemu" \
  "Failed to execute BSF."

execute_command "module use --append /home/luis/work/bsf/builder/mod" \
  "Failed to use MODULE"

execute_command "module load qemu" \
  "Failed to load MODULE"

execute_command "qemu-system-arc --version" \
  "Failed to version QEMU"

exit_return $TASK_ID 0

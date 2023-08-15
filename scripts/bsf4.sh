#!/bin/bash

source "/scratch/luiss/bsf/api/scripts/return_exit.sh"
BSF_BUILDER="/scratch/luiss/bsf/builder-ci"
SOURCES="$BSF_BUILDER/sources"
#WORKTREE=/home/luis/work/thesis/worktree/playground/

TASK_NAME="$1"
TASK_ID="$2"
BRANCH="$3"
execute_command "echo $BRANCH"
BRANCH="${BRANCH##*/}"
BEFORE="$4"
AFTER="$5"

execute_command "echo $BRANCH"
execute_command "echo $BEFORE"
execute_command "echo $AFTER"

execute_command "echo $TASK_NAME"

execute_command "export PATH=\"/scratch/luiss/bsf/testing-framework:\$PATH\""
execute_command "cd $BSF_BUILDER"
execute_command "bsf set GCC_SRC=main"
execute_command "bsf set BINUTILS_GDB_SRC=main"
execute_command "bsf set GLIBC_SRC=main"
execute_command "bsf set NEWLIB_SRC=main"
execute_command "bsf set QEMU_SRC=main"

get_versions

# Read and execute the commands from commands_to_import.txt
while IFS= read -r cmd
do
  execute_command "$cmd"
done < "/scratch/luiss/bsf/api/scripts/$TASK_NAME.txt"

exit_return $TASK_ID 0

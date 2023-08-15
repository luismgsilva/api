#!/bin/bash

LOG="/scratch/luiss/bsf/api/log"
echo "" > "$LOG"

exit_return() {
  # Perform the PUT request indicating the exit return value
  local task_id=$1
  local exit_value=$2
  local url="http://127.0.0.1:8000/ci_task"

  git -C $SOURCES/$TASK_NAME.git worktree remove $SOURCES/worktree/$TASK_NAME || true
  git -C $SOURCES/$TASK_NAME.git branch -D $BRANCH || true

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
  eval "$cmd" &>> $LOG
  result=$?
  if [ $result -ne 0 ]; then
    # echo "$error_message"
    exit_return $TASK_ID 1
  fi
}



get_versions() {

  if [[ $(git -C "$SOURCES/main/$TASK_NAME" rev-parse --abbrev-ref HEAD) != "$BRANCH" ]]; then
    execute_command "echo 'workstree'"
    git -C $SOURCES/$TASK_NAME.git fetch --all -p
    git -C $SOURCES/$TASK_NAME.git worktree add $SOURCES/worktree/$TASK_NAME --checkout -b $BRANCH snps/$BRANCH

    execute_command "echo '1'"

    # COMMIT_HASHES=$(git -C $SOURCES/worktree/$TASK_NAME log -2 --format=format:'%H')
    HASH1=$(git -C $SOURCES/worktree/$TASK_NAME log -1 --format=format:'%H')
    execute_command "echo '2'"
    # IFS=$'\n' read -d '' -ra hash_array <<< $COMMIT_HASHES
    execute_command "echo '3'"

    # HASH1=${hash_array[0]}
    # HASH2=${hash_array[1]}
    execute_command "echo '4'"

    # if [[ $HASH1 != $AFTER || $HASH2 != $BEFORE ]]; then
    if [[ $HASH1 != $AFTER ]]; then
        git -C $SOURCES/worktree/$TASK_NAME checkout $AFTER
        HASH1=$(git -C $SOURCES/worktree/$TASK_NAME log -1 --format=format:'%H')
    fi
    execute_command "echo '5'"

    # if [[ $HASH1 != $AFTER || $HASH2 != $BEFORE ]]; then
    if [[ $HASH1 != $AFTER ]]; then
        execute_command "echo $HASH1"
        execute_command "echo $AFTER"
        execute_command "echo 'workstree: not good' && false"
    fi
    execute_command "echo '6'"

    cd $BSF_BUILDER

    TMP="${TASK_NAME//-/_}"
    bsf set ${TMP^^}_SRC=worktree
    execute_command "echo 'workstree: good'"
else
    execute_command "echo 'main: arc64'"

    git -C $SOURCES/main/$TASK_NAME fetch
    git -C $SOURCES/main/$TASK_NAME pull

    HASH1=$(git -C $SOURCES/main/$TASK_NAME log -1 --format=format:'%H')
    if [[ $HASH1 != $AFTER ]]; then
        git -C $SOURCES/main/$TASK_NAME checkout $AFTER
    fi

    if [[ $HASH1 != $AFTER ]]; then
        execute_command "echo 'main: not good '"
        false
    fi
    execute_command "echo 'main: good'"
fi

}
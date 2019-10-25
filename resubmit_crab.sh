#! /bin/bash
# Author: Izaak Neutelings (October, 2019)
function peval { echo ">>> $@"; eval "$@"; }

TASKS="$@"

for task in $TASKS; do
  #echo ">>> $task"
  peval "crab resubmit -d $task"
done
#! /bin/bash
# Author: Izaak Neutelings (October, 2019)
function peval { echo -e ">>> \e[1m$@\e[0m"; eval "$@"; }

if [[ $# -lt 2 ]]; then
  echo ">>> Not enough arguments! Please use 'crab.sh <command> <task directories>'."
  exit 1
fi

CMD="$1"
TASKS="${@:2}"

if [ "$CMD" = "rm" ]; then
  peval "rm -rf $TASKS"
else
  for task in $TASKS; do
    #echo ">>> crab $CMD -d $task"
    peval "crab $CMD -d $task"
  done
fi

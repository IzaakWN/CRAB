#! /bin/bash
# Author: Izaak Neutelings (October, 2019)
function peval { echo -e ">>> \e[1m$@\e[0m"; eval "$@"; }

# ENSURE ARGUMENTS
if [[ $# -lt 2 ]]; then
  echo ">>> Not enough arguments! Please use 'crab.sh <command> <task directories>'."
  exit 1
fi

# PARSE ARGUMENTS
CMD="$1"
OPTS=""
TASKS="" 
for arg in "${@:2}"; do
  [ "${arg:0:2}" = '--' ] && OPTS+="$arg " || TASKS+="$arg "
done

# EXECUTE
if [ "$CMD" = "rm" ]; then
  peval "rm -rf $TASKS"
else
  for task in $TASKS; do
    #echo ">>> crab $CMD -d $task"
    peval "crab ${CMD} ${OPTS}-d ${task}"
  done
fi

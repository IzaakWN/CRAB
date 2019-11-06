#! /bin/bash
# Author: Izaak Neutelings (October, 2019)
function peval { echo -e ">>> \e[1m$@\e[0m"; eval "$@"; }
#set -e # exit on first error

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

# CHECK COMMAND
CMDS="submit resubmit status report kill rm"
CMS_VALID=0
for cmd in $CMDS; do
  [ $cmd = $CMD ] && CMS_VALID=1 && break
done
[ $CMS_VALID -lt 1 ] && echo ">>> '$CMD' not a valid command to crab.sh, please choose from: '${CMDS// /', '}'" && exit 1

# EXECUTE
if [ "$CMD" = "rm" ]; then
  peval "rm -rf $TASKS"
else
  for task in $TASKS; do
    #echo ">>> crab $CMD -d $task"
    peval "crab ${CMD} ${OPTS}-d ${task}"
  done
fi

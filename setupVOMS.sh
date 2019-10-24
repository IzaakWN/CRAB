#! /bin/bash
function peval { echo ">>> $@"; eval "$@"; }

printf ">>> voms-proxy-info --timeleft\n"
TIMELEFT=$(voms-proxy-info --timeleft)
if [[ $TIMELEFT -lt 36000 ]]; then # 10 hours
   if [[ $TIMELEFT -gt 0 ]]; then
     echo ">>> voms valid for less than 10 hours (`date -u -d @$TIMELEFT +"%-H hours, %-M minutes and %-S seconds"`)"
   else
     echo ">>> voms not valid anymore..."
   fi
   peval "voms-proxy-init -voms cms -valid 400:0"
else
  echo ">>> voms still valid for another `date -u -d @$TIMELEFT +"%-d days, %-H hours and %-M minutes"`"
fi

#! /bin/bash
# Author: Izaak Neutelings (June 2022)
function peval { echo -e ">>> $@"; eval "$@"; }
function div { printf '#%.0s' $(seq 100); echo; }
div
START=`date +%s`
echo "Job start at `date`"

# USER OPTIONS
OUTDIR="$1"
CONFIG="$2"
CFGARGS="${@:3}"
WORKDIR="$PWD"
BASEDIR="$(dirname $CONFIG)"
CMSSWSRC=""
for dir in `ls -d $BASEDIR/CMSSW_*_*/src`; do
  if [ -d $dir -a "$CMSSWSRC" ]; then
    echo ">>> WARNING! Found another CMSSW directory in $BASEDIR !!! Using $CMSSWSRC..."
  elif [ -d $dir ]; then
    CMSSWSRC="$dir"
  else
    echo ">>> Could not find CMSSW directory in $BASEDIR"
    exit 1
  fi
done
div
echo ">>> WORKDIR=$WORKDIR"
echo ">>> BASEDIR=$BASEDIR"
echo ">>> CMSSWSRC=$CMSSWSRC"
echo ">>> CONFIG=$CONFIG"
echo ">>> CFGARGS=$CFGARGS"
echo ">>> OUTDIR=$OUTDIR"
echo ">>> JOBID=$JOBID"
echo ">>> TASKID=$TASKID"
div
peval "pwd"
peval "ls -hlt"

# CMSSW
div
peval "source /cvmfs/cms.cern.ch/cmsset_default.sh"
peval "export SCRAM_ARCH=slc7_amd64_gcc700"
#peval "export SCRAM_ARCH=slc6_amd64_gcc700"
peval "cd $CMSSWSRC"
peval "cmsenv" #peval "eval `scramv1 runtime -sh`"
peval "cd $WORKDIR"
#peval "env | sort"
div

# EXECUTE MAIN FUNCTIONALITY
peval "cd $WORKDIR"
peval "cmsRun $CONFIG $CFGARGS"

# COPY BACK TO EOS
# https://batchdocs.web.cern.ch/tutorial/exercise11.html
div
peval "pwd"
peval "ls -hlt"
peval "ls -hlt $BASEDIR"
#peval "rm -v GENSIM_LHE*.root"
if [ "$OUTDIR" ]; then
  peval "export EOS_MGM_URL=root://eosuser.cern.ch"
  peval "eos cp GENSIM*.root $OUTDIR/"
fi
peval "rm -rf *.root" # clean and prevent CONDOR file transfer
div
END=`date +%s`; RUNTIME=$((END-START))
echo "Job complete at `date`"
printf "Took %d minutes %d seconds" "$(( $RUNTIME / 60 ))" "$(( $RUNTIME % 60 ))"
div
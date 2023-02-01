#! /bin/bash
# Author: Izaak Neutelings (June 2020)
function peval { echo -e ">>> $@"; eval "$@"; }
function pline { printf '=%.0s' `seq 1 ${1:-80}`; echo; }
echo ">>> Start..."
peval "date"
START=`date +%s`
peval "ulimit -a"

# SETTING
JOBNAME=$1
CARDDIR=$2
QUEUEMODE="local"
JOBSTEP="ALL"
SCRAM_ARCH=$3
CMSSW_VERSION=$4
#BASEDIR="/eos/user/i/ineuteli/prod"
#BASEDIR="/afs/cern.ch/user/i/ineuteli/prod/LQ_Request2020"
#BASEDIR="/eos/user/i/ineuteli/prod/LQ_Request2020"
BASEDIR="/afs/cern.ch/user/i/ineuteli/prod/CRAB/CMSSW_10_6_19/src"
#BASEDIR="/afs/cern.ch/user/i/ineuteli/prod/CRAB/LQ_Thesis2023"
WORKDIR="$BASEDIR/genproductions/bin/MadGraph5_aMCatNLO"
OUTDIR="/eos/user/i/ineuteli/public/LQ_PhDThesis"
GRIDPACK="${JOBNAME}_${SCRAM_ARCH}_${CMSSW_VERSION}_tarball.tar.xz"
#LOG="$OUTDIR/${JOBNAME}_${SCRAM_ARCH}_${CMSSW_VERSION}.log"
#export PATH="/cvmfs/sft.cern.ch/lcg/releases/Python/3.8.6-3199b/x86_64-centos7-gcc10fp-opt/bin/:$PATH" # for python version >= 3.7 for MadGraph
pline
echo "JOBNAME=$JOBNAME"
echo "CARDDIR=$CARDDIR"
echo "QUEUEMODE=$QUEUEMODE"
echo "HOME=$HOME"
echo "USER=$USER"
echo "HOSTNAME=$HOSTNAME"
echo "PWD=$PWD"
echo "BASEDIR=$BASEDIR"
echo "WORKDIR=$WORKDIR"
#echo "LOG=$LOG"
echo "GRIDPACK=$GRIDPACK"
echo "OUTDIR=$OUTDIR"
#echo "PATH=$PATH"
#peval "source /cvmfs/sft.cern.ch/lcg/views/LCG_102b/x86_64-centos7-gcc12-dbg/setup.sh" # for python version >= 3.7 for MadGraph
#peval "python --version"
#peval "python3 --version"

# ACTUAL JOB
pline
peval "source $VO_CMS_SW_DIR/cmsset_default.sh"
peval "export SCRAM_ARCH=$SCRAM_ARCH"
peval "cd $WORKDIR"
peval "pwd" #2>&1 | tee -a $LOG
peval "ls -hlt" #2>&1 | tee -a $LOG
peval "./gridpack_generation.sh $JOBNAME $CARDDIR local ALL $SCRAM_ARCH $CMSSW_VERSION" #2>&1 | tee -a $LOG
pline #| tee -a $LOG

# FINISH
peval "ls -hlt" #2>&1 | tee -a $LOG
[[ ! -d $OUTDIR ]] && peval "mkdir -p $OUTDIR" #2>&1 | tee -a $LOG
peval "mv $GRIDPACK $OUTDIR" #2>&1 | tee -a $LOG
#peval "mv $LOG $OUTDIR"
peval "rm -rf $JOBNAME"
peval "date"
END=`date +%s`
SECS=$((END-START))
printf ">>> Done in %02d:%02d:%02d.\n" "$(($SECS/3600))" "$(($SECS%3600/60))" "$(($SECS%60))"
pline
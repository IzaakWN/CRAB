#! /bin/bash
# Author: Izaak Neutelings (June 2020)
echo ">>> Start..."
function peval { echo -e ">>> $@"; eval "$@"; }
peval "ulimit -a"

# SETTING
JOBNAME=$1
CARDDIR=$2
QUEUEMODE="local"
JOBSTEP="ALL"
SCRAM_ARCH=$3
CMSSW_VERSION=$4
BASEDIR="/afs/cern.ch/user/i/ineuteli/production/LQ_Request2020/GenerateMC"
WORKDIR="$BASEDIR/genproductions/bin/MadGraph5_aMCatNLO"
echo "JOBNAME=$JOBNAME"
echo "CARDDIR=$CARDDIR"
echo "QUEUEMODE=$QUEUEMODE"
echo "HOME=$HOME"
echo "USER=$USER"
echo "HOSTNAME=$HOSTNAME"
echo "PWD=$PWD"
echo "BASEDIR=$BASEDIR"
echo "WORKDIR=$WORKDIR"

# ACTUAL JOB
peval "source $VO_CMS_SW_DIR/cmsset_default.sh"
peval "export SCRAM_ARCH=$SCRAM_ARCH"
peval "cd $WORKDIR"
peval "ls"
peval "./gridpack_generation.sh $JOBNAME $CARDDIR local ALL $SCRAM_ARCH $CMSSW_VERSION"

# FINISH
echo ">>> Done."
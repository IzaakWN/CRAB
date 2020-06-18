#! /bin/bash
# Author: Izaak Neutelings (June 2020)
function peval { echo -e ">>> $@"; eval "$@"; }
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
BASEDIR="/afs/cern.ch/user/i/ineuteli/production/LQ_Request2020"
#BASEDIR="/eos/user/i/ineuteli//production/LQ_Request2020"
WORKDIR="$BASEDIR/genproductions/bin/MadGraph5_aMCatNLO"
OUTDIR="/eos/user/i/ineuteli/public/forEXO"
GRIDPACK="${JOBNAME}_${SCRAM_ARCH}_${CMSSW_VERSION}_tarball.tar.xz"
echo "JOBNAME=$JOBNAME"
echo "CARDDIR=$CARDDIR"
echo "QUEUEMODE=$QUEUEMODE"
echo "HOME=$HOME"
echo "USER=$USER"
echo "HOSTNAME=$HOSTNAME"
echo "PWD=$PWD"
echo "BASEDIR=$BASEDIR"
echo "WORKDIR=$WORKDIR"
echo "OUTDIR=$OUTDIR"

# ACTUAL JOB
peval "source $VO_CMS_SW_DIR/cmsset_default.sh"
peval "export SCRAM_ARCH=$SCRAM_ARCH"
peval "cd $WORKDIR"
peval "ls"
peval "./gridpack_generation.sh $JOBNAME $CARDDIR local ALL $SCRAM_ARCH $CMSSW_VERSION"

# FINISH
peval "ls -hlt"
peval "mv $GRIDPACK $OUTDIR"
peval "rm -rf $JOBNAME"
peval "date"
END=`date +%s`
SECS=$((END-START))
printf ">>> Done in %02d:%02d:%02d.\n" "$(($SECS/3600))" "$(($SECS%3600/60))" "$(($SECS%60))"
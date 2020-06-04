#! /usr/bin/env python
# Author: Izaak Neutelings (November, 2019)
# grep -l Aborting submit_sge/Scalar*
# for d in $SAMPLES/Scalar*M1*GENSIM; do
#   I=""; for i in `seq 1 4`; do [ ! -e $d/GENSIM_$i.root ] && I+="$i "; done;
#   [[ $I ]] && echo "./submit_sge.py -g gridpacks/$(basename $d | sed 's/_GENSIM//')_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz -N 5000 -i $I";
# done
import os, sys
import subprocess
import time
from argparse import ArgumentParser
from utils import ensureDirectory

usage = """Submit SGE jobs to generate GENSIM samples."""
parser = ArgumentParser(prog='submit_sge',description=usage,epilog="Succes!")
parser.add_argument('pset',             type=str, nargs='?', action='store', default="pset_GENSIM.py",
                    metavar='FILE',     help="parameter-set configuration file to submit" )
parser.add_argument('-m', '--mock-sub', dest="submit", default=True, action='store_false',
                                        help="do not submit job to batch (mock submit)")
parser.add_argument('-s', '--sample',   dest="samples", nargs='+', default=[ ], action='store',
                    metavar="SAMPLE",   help="list of signals to get output for" )
parser.add_argument('-N', '--nevents',  default=5000, action='store',
                                        help="number of event to be generated in each job")
parser.add_argument('-c', '--ncores',   type=int, default=2, action='store',
                                        help="number of core in each job")
parser.add_argument('-q', '--queue',    choices=['all.q','short.q','long.q'], default=None, action='store',
                    metavar='QUEUE',    help="job queue" )
parser.add_argument('-M', '--mass',     dest="masses", type=int, nargs='+', default=[ 1000 ], action='store',
                    metavar='MASS',     help="LQ mass point(s) to run over" )
parser.add_argument('-g', '--gridpack', dest="gridpacks", nargs='+', default=[ ],
                                        help="gridpack(s) to submit" )
parser.add_argument('-p', '--priority', type=int, default=10, action='store',
                                        help="submit with priority (default=10)" )
parser.add_argument('-i', '--index',    dest="indices", type=int, nargs='+', default=[ ], action='store',
                    metavar='INDEX',    help="indices to run over" )
parser.add_argument('-t', '--tag',      type=str, default="", action='store',
                                        help="extra tag for output")                     
args = parser.parse_args()

director     = 'root://t3dcachedb03.psi.ch:1094/'
cmsswversion = "CMSSW_10_2_16_patch1"
WORKPATH     = "/work/ineuteli/production/LQ_Legacy" #/%s/src"%(cmsswversion)
DATAPATH     = director+"/pnfs/psi.ch/cms/trivcat/store/user/ineuteli/samples/"
pset         = args.pset             # e.g. pset_GENSIM.py
nevents      = args.nevents          # number of events to be generated
queue        = args.queue or ('short.q' if nevents<=5000 else 'all.q')
                                     # all.q (10h), short.q (90 min.)
ncores       = args.ncores           # "nb_core" in input/mg5_configuration.txt should be the same number!
samples      = args.samples          
masses       = args.masses           
gridpacks    = args.gridpacks        
tag          = args.tag              
first        = 1                     # first index of a sample
last         = 1                     # last index of a sample
indices      = args.indices or range(first,last+1)
nJobs        = 0


def main():
    global pset, gridpacks, samples, ncores, nevents, masses, indices, nJobs, tag
    
    INPUTDIR  = "gridpacks"
    REPORTDIR = "%s/submit_sge"%(WORKPATH)
    gpversion = "slc6_amd64_gcc630_CMSSW_9_3_16"
    ensureDirectory(REPORTDIR)
    
    # SUBMIT GRIDPACKS
    for gridpack in gridpacks:
      assert os.path.isfile(gridpack), "Gridpack '%s' is not a file!"%(gridpack)
      jobname = getSampleNameFromGridpack(gridpack)
      for index in indices:
        submitSampleToSGE(pset,gridpack,jobname,index,N=nevents,tag=tag)
    
    # SUBMIT SAMPLE x MASS
    for sample in samples:
      for mass in masses:
        gridpack = "%s/%s_M%s_%s_tarball.tar.xz"%(INPUTDIR,sample,mass,gpversion)
        jobname  = "%s_M%s"%(sample,mass)
        for index in indices:
          submitSampleToSGE(pset,gridpack,jobname,index,N=nevents,tag=tag)
    
    print ">>> submitted %s jobs"%(nJobs)
    

def getSampleNameFromGridpack(gridpack):
  gridpack = os.path.basename(gridpack)
  for pattern in ['_slc6_','_slc7_','_CMSSW_',]:
    if pattern in gridpack:
      gridpack = gridpack[:gridpack.index(pattern)]
      break
  return gridpack
  

def submitSampleToSGE(pset,gridpack,sample,index=-1,N=-1,ncores=ncores,tag=tag):
    """Submit PSet config file and gridpack to SGE batch system."""
    global nJobs
    jobname  = sample
    gridpack = os.path.abspath(gridpack)
    options  = ""
    if index>0:
      jobname = "%s_%d"%(jobname,index)
      options = "%s -i %d"%(options,index)
    qoptions = "-q %s -N %s"%(queue,jobname)
    if N>0:
      options = "%s -N %s"%(options,N)
    if tag:
      options = "%s -t %s"%(options,tag)
    if ncores>1:
      qoptions = "%s -pe smp %d"%(qoptions,ncores)
      options  = "%s -c %s"%(options,ncores)
    options = options.lstrip(' ')
    command = "qsub %s submit_sge.sh %s %s %s %s"%(qoptions.strip(),pset,gridpack,sample,options.strip())
    print ">>> %s"%(command.replace(jobname,"\033[;1m%s\033[0;0m"%jobname,1))
    nJobs  += 1
    if not args.submit:
      return
    sys.stdout.write(">>> ")
    sys.stdout.flush()
    os.system(command)
    print ">>> "
    

if __name__ == '__main__':
  print "\n>>> "
  main()
  print ">>> done\n"
  

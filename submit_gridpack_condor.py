#! /usr/bin/env python
# Author: Izaak Neutelings (June 2020)
# Note:
#  - Clone genproductions (official or private) with gridpack_generation.sh and cards:
#      cd /eos/user/i/ineuteli/prod
#      git clone git@github.com:cms-sw/genproductions.git genproductions
#      git clone git@github.com:IzaakWN/genproductions.git genproductions
#  - Gridpack working areas can get large; O(400MB) per gridpack
#  - AFS has a limited space (up to 10 GB, use `fs listquota`)
#    => use CMSSW working directory on EOS
#  - HTCondor jobs cannot be submitted from EOS
#    => submit from AFS
#  - git push does not work on EOS
from __future__ import print_function # for python3 compatibility
import os, sys
from create_cards import createcards, subplaceholders
from utils import ensuredir, subkey, warning

#print sys.path
#basedir = "/eos/user/i/ineuteli/production/LQ_Request2020/genproductions/bin/MadGraph5_aMCatNLO"
#basedir = "genproductions/bin/MadGraph5_aMCatNLO"
arch_dict = {
  '2016':   ('slc6_amd64_gcc481','CMSSW_7_1_45_patch3'),
  '2017':   ('slc6_amd64_gcc630','CMSSW_9_3_17'),
  '2018':   ('slc6_amd64_gcc700','CMSSW_10_2_20'),
  'UL2016': ('slc7_amd64_gcc700','CMSSW_10_6_31'),
}
arch_dict['UL2017'] = arch_dict['UL2016']
arch_dict['UL2018'] = arch_dict['UL2016']


def findHTCondorBindings():
  # export PYTHONPATH=/usr/lib64/python2.6/site-packages
  import htcondor
  print(os.path.dirname(htcondor.__file__))
  

def submit(sample,carddir,scram,cmssw,mock=False):
  #command = "sbatch -J gridpack_%s submit_gridpack_generation_SLURM.sh %s %s"%(sample,sample,carddir)
  #command = "qsub -N gridpack_%s submit_gridpack_generation_SGE.sh %s %s %s %s"%(sample,sample,carddir,scram,cmssw)
  command = "./submit_condor_gridpack_generation.sh %s %s %s %s"%(sample,carddir,scram,cmssw)
  print(command)
  if not mock:
    os.system(command)
  

def submitArgFile(jobname,argfile,jobdir="jobs",mock=False):
  logdir  = ensuredir(os.path.join(jobdir,'log'))
  logfile = os.path.join(logdir,"%s.$(ClusterId).$(ProcId).log"%(jobname))
  command = "condor_submit -batch-name %s -append mylogfile='%s' submit_gridpack_condor.sub -queue arg from %s"%(jobname,logfile,argfile)
  print(">>> %s"%(command))
  if not mock:
    os.system(command)
  

def createArgFile(jobname,name,masses,scram,cmssw,carddir,jobdir="jobs",workdir=None):
  ensuredir(jobdir)
  jobname = jobname.replace('$MASS','')
  fname = os.path.join(jobdir,"args_%s.txt"%(jobname))
  print(">>> %s"%(jobname))
  with open(fname,'w+') as file:
    for mass in masses:
      ###for lambd in lambdas:
      ###print ">>> mass=%s, lambda=%s"%(mass,lambd)
      ###lambd   = str(lambd).replace('.','p')
      name_    = subkey(name,MASS=mass) #"%sScalarLQToBTau_M%s_L%s"%(proc,mass,lambd)
      carddir_ = subkey(carddir,MASS=mass) #"%sScalarLQToBTau_M%s_L%s"%(proc,mass,lambd)
      ###if carddir_[0]!='/':
      ###  carddir_ = os.path.abspath(carddir_)
      ###carddir_ = os.path.join(carddir,name_)
      fulldir  = os.path.abspath(carddir_) #os.path.join(basedir,carddir)
      workdir_ = os.path.join(workdir,name_)
      if not os.path.exists(fulldir):
        print(warning("createArgFile: Sample card directory does not exist! %r"%(fulldir),pre=">>> "))
      if os.path.exists(workdir_): # created by gridpack_generation.sh
        print(warning("createArgFile: Work directory already exists! Please remove %r"%(workdir_),pre=">>> "))
      if workdir: # create path relative to gridpack_generation.sh in workdir
        carddir_ = os.path.relpath(carddir_,workdir)
      if workdir and workdir[0]=='/' and fulldir[0]=='/' and workdir.split('/')[:2]!=fulldir.split('/')[:2]:
        print(warning("createArgFile: carddir and workdir are not on the same system? carddir=%s vs. workdir=%s"%(fulldir,workdir),pre=">>> "))
      args = "%s %s %s %s"%(name_,carddir_,scram,cmssw)
      print(">>>   %s"%(args))
      file.write(args+'\n')
  return fname
  

def main(args):
  #findHTCondorBindings()
  
  create    = args.create
  mock      = args.mock
  #carddirs  = ["cards/production/2017/13TeV/ScalarLQ/"]
  carddirs  = args.carddirs
  cardname  = args.cardname or "$NAME_M$MASS_L$LAMBDA"
  jobname   = "$NAME_L$LAMBDA_$ERA" # no mass
  eras      = args.eras
  ###models    = args.models #['VectorLQ','ScalarLQ']
  ###procs     = args.procs #['Single',] #'Pair']
  #masses    = [600,800,1000,1200,1400,1700,2000] #500,800,1100,1400,1700,2000,2300]
  masses    = args.masses or [600,1400,2000]
  lambdas   = args.lambdas or [1.0]
  jobdir    = args.jobdir #"jobs/"
  basedir   = args.workdir or "/afs/cern.ch/user/i/ineuteli/prod/CRAB/CMSSW_10_6_19/src"
  #basedir   = args.workdir or "/eos/user/i/ineuteli/prod" #CMSSW_10_6_19/src"
  workdir   = os.path.join(basedir,"genproductions/bin/MadGraph5_aMCatNLO")
  if basedir.startswith('/eos/'): # on EOS: ensure cards relative to workdir
    outdir  = os.path.join(basedir,'cards/$CARDNAME')
  else: # on AFS
    outdir  = os.path.join(jobdir,'cards/$CARDNAME')
  verbosity = args.verbosity+2
  #lambdas   = [1.5,2.0,2.5]
  #jobname   = "%sScalarLQToBTau_L%s_%s"%(proc,lambd,era)
  #sample    = "%sScalarLQToBTau_M%s_L%s"%(proc,mass,lambd)
  #jobname   = "$PROC$SPIN$MODEL_L$LAMBDA_$MASS_$ERA"
  #os.chdir(basedir)
  assert os.path.exists(workdir), "Working directory %s does not exist!"%(workdir)
  
  for carddir in carddirs:
    if create: # create datacards locally
      print(">>> Create data cards...")
      paramdict = { 'LAMBDA': lambdas }
      names = createcards(carddir,cardname,masses,paramdict,outdir=outdir,verb=verbosity)
      name_ = names[0]
    else: # use datacards in CMSSW
      name_ = os.basename(carddir.rstrip('/'))
      ###basedir = "$CMSSW_BASE/genproductions/bin/MadGraph5_aMCatNLO"
      ###fulldir = os.path.join(basedir,carddir)
      ###if not os.path.exists(fulldir):
      ###  print(">>> Card directory does not exist! %r"%(fulldir))
    for era in eras:
      scram, cmssw = arch_dict[era]
      ###for model in models:
      ###  for proc in procs:
      
      # PRINT
      if verbosity>=1:
        print(">>> "+'='*90)
        print(">>> name     = %r"%name_)
        print(">>> cardname = %r"%cardname)
        print(">>> jobname  = %r"%jobname)
        print(">>> carddir  = %s"%carddir)
        print(">>> workdir  = %s"%workdir)
        print(">>> outdir   = %s"%outdir)
        print(">>> masses   = %s"%masses)
        print(">>> lambdas  = %s"%lambdas)
        print(">>> era      = %s"%era)
        print(">>> scram    = %s"%scram)
        print(">>> cmssw    = %s"%cmssw)
      print(">>> "+'='*90)
      
      for lambd in lambdas:
        lambd     = str(lambd).replace('.','p')
        jobname_  = subplaceholders(jobname,NAME=name_,LAMBDA=lambd,ERA=era) #,MODEL=model,PROC=proc
        cardname_ = subkey(cardname,NAME=name_,LAMBDA=lambd,ERA=era) # ignore $MASS
        carddir_  = subkey(outdir,CARDNAME=cardname_,NAME=name_,LAMBDA=lambd,ERA=era)
        if verbosity>=2:
          #print(">>> carddir=%r, era=%r, lambda=%r, name=%r, scram=%r, cmssw=%r"%(carddir,era,lambd,name,scram,cmssw))
          print(">>> lambda=%r, name=%r, jobname=%r, cardname=%r -> %r"%(lambd,name_,jobname_,cardname,cardname_))
        argfile  = createArgFile(jobname_,cardname_,masses,scram,cmssw,carddir_,jobdir=jobdir,workdir=workdir)
        submitArgFile(jobname_,argfile,jobdir=jobdir,mock=mock)
        print()
      #for mass in masses:
      #  for lambd in lambdas:
      #    print(">>> mass=%s, lambda=%s"%(mass,lambd))
      #    lambd   = str(lambd).replace('.','p')
      #    sample  = "%sScalarLQToBTau_M%s_L%s"%(proc,mass,lambd)
      #    samdir  = os.path.join(carddir,sample)
      #    fulldir = os.path.join(basedir,samdir)
      #    if not os.path.exists(fulldir):
      #      print(">>> Sample card directory does not exist! %r"%(fulldir))
      #    submit(sample,samdir,scram,cmssw)
      #    print()
  

if __name__=='__main__':
  print()
  from argparse import ArgumentParser
  description = '''Create gridpack with condor jobs.'''
  parser = ArgumentParser(prog="submit_gridpack_condor",description=description,epilog="Good luck!")
  parser.add_argument('carddirs',          type=str, nargs='+', action='store',
                       metavar='CARDDIRS', help="directoy with cards" )
  parser.add_argument('-c', '--create',    dest='create', action='store_true',
                                           help="create cards before submitting" )
  parser.add_argument('-m', '--mock',      action='store_true',
                                           help="mock submit (for debugging)" )
  ###parser.add_argument(      '--model',     dest='models', nargs='+', choices=['VectorLQ','ScalarLQ'],
  ###                                         help="models" )
  ###parser.add_argument('-p', '--proc',      dest='procs', nargs='+', choices=['Pair','Single','NonRes'],
  ###                                         help="processes" )
  parser.add_argument('-n', '--cardname',  type=str, action='store', default=None,
                                           help="card name (placeholders allowed)" )
  parser.add_argument('-M', '--mass',      dest='masses', nargs='+', type=int,
                                           help="select masses" )
  parser.add_argument('-L', '--lambda',    dest='lambdas', nargs='+', default=[1.0], type=float,
                                           help="select lambdas" )
  parser.add_argument('-y', '--era',       dest='eras', nargs='+', default=['UL2017'], #choices=[2016,2017,2018], 
                                           help="select year/era" )
  ###parser.add_argument('-o', '--outdir',    default='jobdir/cards',
  ###                                         help="output directory for cards" )
  parser.add_argument('-j', '--jobdir',    default='jobs',
                                           help="output directory for cards" )
  parser.add_argument('-w', '--workdir',   help="parent directory of genproductions" )
  parser.add_argument('-v', "--verbose",   dest='verbosity', type=int, nargs='?', const=2, default=1,
                                           help="set level of verbosity, default=%(default)s" )
  args = parser.parse_args()
  main(args)
  print(">>> Done.")
  print()
  

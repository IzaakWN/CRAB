#! /usr/bin/env python
# Author: Izaak Neutelings (June 2020)
# Note:
#  - Clone cards:
#      git clone git@github.com:IzaakWN/genproductions.git genproductions
#  - Gridpack working area's can get large, O(400MB)
#  - AFS has a limited space (up to 10 GB), use
#      fs listquota
#  - HTCondor jobs cannot be submitted from EOS
#  - git push does not work on EOS
import os, sys
#print sys.path
#basedir = "/eos/user/i/ineuteli//production/LQ_Request2020/genproductions/bin/MadGraph5_aMCatNLO"
basedir = "genproductions/bin/MadGraph5_aMCatNLO"
carddir = "cards/production/2017/13TeV/ScalarLQ/"


def findHTCondorBindings():
  # export PYTHONPATH=/usr/lib64/python2.6/site-packages
  import htcondor
  print os.path.dirname(htcondor.__file__)
  

def submit(sample,carddir,scram,cmssw):
  #command = "sbatch -J gridpack_%s submit_gridpack_generation_SLURM.sh %s %s"%(sample,sample,carddir)
  #command = "qsub -N gridpack_%s submit_gridpack_generation_SGE.sh %s %s %s %s"%(sample,sample,carddir,scram,cmssw)
  command = "./submit_condor_gridpack_generation.sh %s %s %s %s"%(sample,carddir,scram,cmssw)
  print command
  os.system(command)
  

def submitArgFile(jobname,argfile):
  logfile = "log/%s.$(ClusterId).$(ProcId).log"%(jobname)
  command = "condor_submit -batch-name %s -append mylogfile='%s' submit_gridpack_HTCondor.sub -queue arg from %s"%(jobname,logfile,argfile)
  print ">>> %s"%(command)
  os.system(command)
  

def createArgFile(jobname,proc,masses,lambd,scram,cmssw):
  fname = "args_%s.txt"%(jobname)
  print ">>> %s"%(jobname)
  with open(fname,'w+') as file:
    for mass in masses:
      #for lambd in lambdas:
      #print ">>> mass=%s, lambda=%s"%(mass,lambd)
      #lambd   = str(lambd).replace('.','p')
      sample  = "%sScalarLQToBTau_M%s_L%s"%(proc,mass,lambd)
      samdir  = os.path.join(carddir,sample)
      fulldir = os.path.join(basedir,samdir)
      workdir = os.path.join(basedir,sample)
      if not os.path.exists(fulldir):
        print ">>> Sample card directory does not exist! %r"%(fulldir)
      if os.path.exists(workdir):
        print ">>> Work directory already exists! Please remove %r"%(workdir)
      args = "%s %s %s %s"%(sample,samdir,scram,cmssw)
      print ">>>   %s"%(args)
      file.write(args+'\n')
  return fname
  

def main(args):
  #findHTCondorBindings()
  
  years   = [2017,] #2018] #[2016,2017,2018]
  procs   = ['Single',] #'Pair']
  masses  = [600,800,1000,1200,1400,1700,2000] #500,800,1100,1400,1700,2000,2300]
  lambdas = [1.5,2.0,2.5]
  if args.masses:
    masses = args.masses
  if args.lambdas:
    lambdas = args.lambdas
  if args.year:
    years = [args.year]
  arch_dict = {
    2016: ('slc6_amd64_gcc481','CMSSW_7_1_45_patch3'),
    2017: ('slc6_amd64_gcc630','CMSSW_9_3_17'),
    2018: ('slc6_amd64_gcc700','CMSSW_10_2_20'),
  }
  fulldir = os.path.join(basedir,carddir)
  if not os.path.exists(fulldir):
    print ">>> Card directory does not exist! %r"%(fulldir)
  #os.chdir(basedir)
  
  for year in years:
    scram, cmssw = arch_dict[year]
    for proc in procs:
      for lambd in lambdas:
        lambd   = str(lambd).replace('.','p')
        jobname = "%sScalarLQToBTau_L%s_%s"%(proc,lambd,year)
        argfile = createArgFile(jobname,proc,masses,lambd,scram,cmssw)
        submitArgFile(jobname,argfile)
        print
      #for mass in masses:
      #  for lambd in lambdas:
      #    print ">>> mass=%s, lambda=%s"%(mass,lambd)
      #    lambd   = str(lambd).replace('.','p')
      #    sample  = "%sScalarLQToBTau_M%s_L%s"%(proc,mass,lambd)
      #    samdir  = os.path.join(carddir,sample)
      #    fulldir = os.path.join(basedir,samdir)
      #    if not os.path.exists(fulldir):
      #      print ">>> Sample card directory does not exist! %r"%(fulldir)
      #    submit(sample,samdir,scram,cmssw)
      #    print
  

if __name__=='__main__':
  print
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('-m', '--mass',      dest='masses', nargs='+', type=int, default=None, action='store',
                                           help="select masses" )
  parser.add_argument('-L', '--lambda',    dest='lambdas', nargs='+', type=float, default=None, action='store',
                                           help="select lambdas" )
  parser.add_argument('-y', '--year',      dest='year', choices=[2016,2017,2018], type=int, default=2017, action='store',
                                           help="select year" )
  parser.add_argument('-v', '--verbose',   dest='verbose', default=False, action='store_true',
                                           help="set verbose" )
  args = parser.parse_args()
  main(args)
  print ">>> Done."
  print


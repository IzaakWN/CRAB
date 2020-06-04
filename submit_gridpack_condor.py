#! /usr/bin/env python
# Author: Izaak Neutelings (June 2020)
import os, sys
from utils import bold, warning, ensureDirectory
#print sys.path
basedir = "GenerateMC/genproductions/bin/MadGraph5_aMCatNLO"
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
  """Submit argument file to HTCondor."""
  logfile = "log/%s.$(ClusterId).$(ProcId).log"%(jobname)
  command = "condor_submit -batch-name %s -append mylogfile='%s' submit_gridpack_HTCondor.sub -queue arg from %s"%(jobname,logfile,argfile)
  print ">>> "+warning(command)
  os.system(command)
  

def createArgFile(jobname,proc,masses,lambdas,scram,cmssw):
  """Create argument file for HTCondor."""
  fname = "args_%s.txt"%(jobname)
  print ">>> %s"%(jobname)
  with open(fname,'w+') as file:
    for mass in masses:
      for lambd in lambdas:
        #print ">>> mass=%s, lambda=%s"%(mass,lambd)
        lambd   = str(lambd).replace('.','p')
        sample  = "%sScalarLQToBTau_M%s_L%s"%(proc,mass,lambd)
        samdir  = os.path.join(carddir,sample)
        fulldir = os.path.join(basedir,samdir)
        workdir = os.path.join(basedir,sample)
        if not os.path.exists(fulldir):
          print ">>> "+warning("Sample card directory does not exist! %r"%(fulldir))
        if os.path.exists(workdir):
          print ">>> "+warning("Work directory already exists! Please remove %r"%(workdir))
        args = "%s %s %s %s"%(sample,samdir,scram,cmssw)
        print ">>>   %s"%(args)
        file.write(args+'\n')
  return fname
  

def main():
  #findHTCondorBindings()
  
  years   = [2018] #[2016,2017,2018]
  procs   = ['Single',] #'Pair']
  masses  = [500,800,1100,1400,1700,2000,2300]
  lambdas = [1.5,2.0,2.5]
  arch_dict = {
    2016: ('slc6_amd64_gcc481','CMSSW_7_1_45_patch3'),
    2017: ('slc6_amd64_gcc630','CMSSW_9_3_17'),
    2018: ('slc6_amd64_gcc700','CMSSW_10_2_20'),
  }
  fulldir = os.path.join(basedir,carddir)
  if not os.path.exists(fulldir):
    print ">>> "+warning("Card directory does not exist! %r"%(fulldir))
  #os.chdir(basedir)
  ensureDirectory("log")
  
  for year in years:
    scram, cmssw = arch_dict[year]
    for proc in procs:
      jobname = "%sScalarLQToBTau_%s"%(proc,year)
      argfile = createArgFile(jobname,proc,masses,lambdas,scram,cmssw)
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
  main()
  print ">>> Done."
  print


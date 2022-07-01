#! /bin/env python3
# Author: Izaak Neutelings (June 2022)
#   https://github.com/IzaakWN/CRAB/blob/master/pset_GENSIM.py
#   https://github.com/MiT-HEP/MCProduction
# Instructions:
#   mkdir -p test_DYJetsToMuTauh && cd test_DYJetsToMuTauh
#   curl -s -k https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_test/TAU-RunIISummer20UL18wmLHEGEN-00006 > setup_DYJetsToMuTauh.sh
#   sed -i 's/exit $GEN_ERR/echo "# IGNORE ERROR $GEN_ERR from request_fragment_check.py"/' setup_DYJetsToMuTauh.sh
#   sed -i 's/EVENTS=[0-9]\+/EVENTS=500/' setup_DYJetsToMuTauh.sh
#   bash setup_DYJetsToMuTauh.sh # setup CMSSW, fragment and generate GENSIM
#   ./submit_fragment.py -t _DYJetsToMuTauh test_DYJetsToMuTauh/TAU-RunIISummer20UL18wmLHEGEN-00006_1_cfg.py -N 100 -n 10000 -v2
import os, re, glob
import getpass # for getpass.getuser()
import subprocess
rexp_fname = re.compile(r"(.*fileName\s*=\s*cms.untracked.string)[^,]+,")
rexp_nevts = re.compile(r"(.*(?:input|nEvents)\s*=\s*cms.untracked.u?int32)[^,]+")


def warning(string,**kwargs):
  print(f">>> \033[1m\033[93m{kwargs.get('pre','')}Warning!\033[0m\033[93m {string}\033[0m")
  

def green(string,**kwargs):
  return f"\033[32m{string}\033[0m"
  

def ensuredir(dirname,verb=0):
  """Make directory if it does not exist."""
  if not dirname:
    return ""
  if not os.path.exists(dirname):
    if verb>=1:
      print(">>> Creating directory %s..."%(dirname))
    os.makedirs(dirname)
    if not os.path.exists(dirname):
      print(">>> Failed to make directory %s..."%(dirname))
  return dirname
  

def writefragment(oldfrag,newfrag,verb=0):
  """Write a fragment for job submission."""
  print(f">>> writefragment: Writing fragment for job: {oldfrag} -> {newfrag}")
  head = """#! /usr/bin/env cmsRun
# Generated with submit_fragment.py"""
  opts = """# USER OPTIONS
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('analysis')
#options.register('tag',     "",mytype=VarParsing.varType.string)
options.register('index',   -1,mytype=VarParsing.varType.int)
options.register('outdir', ".",mytype=VarParsing.varType.string)
options.register('maxevts',100,mytype=VarParsing.varType.int)
options.register('seed',    -1,mytype=VarParsing.varType.int)
options.parseArguments()
tag     = options.tag
index   = options.index
outdir  = options.outdir
seed    = options.seed
maxevts = options.maxevts
if index>=0:
  tag += "_%04d"%(index)
outfile_RAW = "file:%s/GENSIM%s.root"%(outdir,tag)
outfile_LHE = "file:%s/LHE%s.root"%(outdir,tag)
print(">>> %-11s = %r"%('index',index))
print(">>> %-11s = %r"%('seed',seed))
print(">>> %-11s = %r"%('maxevts',maxevts))
print(">>> %-11s = %r"%('outfile_RAW',outfile_RAW))
print(">>> %-11s = %r"%('outfile_LHE',outfile_LHE))
"""
  seed = """
# RANDOM SEED
if seed>0:
  process.RandomNumberGeneratorService.externalLHEProducer.initialSeed = int(seed)
else:
  from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper
  randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)
  randSvc.populate() # set random number each cmsRun
"""
  
  # READ OLD FRAGMENT
  hasopts  = False
  hasrand  = False
  oldlines = [ ]
  if verb>=1:
    print(f">>> writefragment: Opening {oldfrag}...")
  with open(oldfrag,'r') as oldfile:
    for line in oldfile.readlines():
      if 'VarParsing' in line:
        hasopts = True
        warning(f"Fragment {oldfrag} already has VarParsing...",pre="writefragment: ")
      if 'process.RandomNumberGeneratorService' in line:
        hasrand = True
      oldlines.append(line)
  
  # WRITE NEW FRAGMENT
  flag = None
  if verb>=1:
    print(f">>> writefragment: Writing {newfrag}...")
  if os.path.isfile(newfrag):
    warning(f"{newfrag} already exists!",pre="writefragment: ")
  with open(newfrag,'w') as newfile:
    for line in head.split('\n'):
      writeline(newfile,line,verb=verb)
    for line in oldlines:
      vline = line.rstrip('\n')
      if 'cms.Process' in line: # insert user options
        for optline in opts.split('\n'):
          writeline(newfile,optline,verb=verb)
      elif 'process.maxEvents' in line or 'process.externalLHEProducer' in line:
        flag = 'maxevts'
      elif 'process.LHEoutput' in line:
        flag = 'LHE'
      elif 'process.RAWSIMoutput' in line:
        flag = 'RAW'
      elif flag=='maxevts' and ('input' in line or 'nEvents' in line):
        line  = rexp_nevts.sub(fr"\1(maxevts)",line)
        vline = rexp_nevts.sub(fr"\1({green('maxevts')})",vline)
        flag  = None
      elif flag=='RAW' and 'fileName' in line:
        line  = rexp_fname.sub(r"\1(outfile_RAW),",line)
        vline = rexp_fname.sub(fr"\1({green('outfile_RAW')}),",vline)
        flag  = None
      elif flag=='LHE' and 'fileName' in line:
        line  = rexp_fname.sub(fr"\1(outfile_LHE),",line)
        vline = rexp_fname.sub(fr"\1({green('outfile_LHE')}),",vline)
        flag  = None
      if verb>=3:
        print(f">>> writefragment:   {vline}")
      newfile.write(line)
    for line in seed.split('\n'):
      writeline(newfile,line,verb=verb)
  
  return oldfrag
  

def writeline(file,line,verb=0):
  if verb>=2:
    print(f">>> writefragment:   {green(line)}")
  file.write(line+'\n')
  return line
  

###def cmsenv(fragment,verb=0):
###  """Source CMSSW environment for fragment before submitting."""
###  # DOES NOT WORK: causes bunch of library issues
###  # https://stackoverflow.com/questions/3503719/emulating-bash-source-in-python
###  #print(">>> cmsenv: Setting up CMSSW environment...")
###  outdir  = os.path.dirname(fragment) or '.'
###  cmsdirs = glob.glob(f"{outdir}/CMSSW_*_*/src")
###  if not cmsdirs:
###    raise IOError(f"Did not find CMSSW directory in {outdir}...")
###  elif len(cmsdirs)>=2:
###    warning(f"Found more than one CMSSW directory in {outdir}! Going with first: {','.join(cmsdirs)}",pre="cmsenv: ")
###  cmsdir = cmsdirs[0]
###  print(f">>> cmsenv: Setting up CMSSW environment from {cmsdir}...")
###  cmscmd = f"export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch && source $VO_CMS_SW_DIR/cmsset_default.sh"+\
###           f" && cd {cmsdir} && cmsenv  && export PYTHONHOME=$(scram tool info python | grep PYTHON_BASE | sed 's/PYTHON_BASE=//') && cd -"
###           #f" && export PYTHONHOME=$(which python | sed -e 's,/bin/python,,')"
###  #if not os.path.isfile("init_env"):
###  srccmd = f"env -i sh -c '{cmscmd} && env'"
###  for line in subprocess.getoutput(srccmd).split('\n'): #sorted(
###    if verb>=2 and 'PYTHONHOME' in line:
###      print(f">>> cmsenv:   {green(line)}")
###    elif verb>=3:
###      print(f">>> cmsenv:   {line}")
###    if '=' not in line:
###      continue
###    key, value = line.split('=')
###    if '{' in value and '}' not in value:
###      value += "; }" # close bracket ?
###    os.environ[key]= value
###    if key=='PYTHON27PATH' and 'PYTHONPATH' not in os.environ: #and 'PYTHONHOME' not in os.environ:
###      if verb>=2:
###        print(">>> cmsenv:   "+green(f"PYTHONPATH={value}"))
###      os.environ['PYTHONPATH'] = value # to fix 'Could not find platform independent libraries' error
  

def submit(fragment,njobs,nevts,outdir="",first=None,indices=None,logdir="",tag="",dry=False,slc6=False,verb=0):
  """Submit fragment to HTCondor."""
  print(">>> Submitting...")
  indir    = os.path.dirname(fragment) or '.'
  fullfrag = os.path.abspath(fragment)
  ensuredir(os.path.join(indir,logdir)) # log directory
  ensuredir(outdir) # ensure output directory exists before submitting
  #args    = f"{outdir} {fullfrag} maxevts={nevts} index=$(ProcId) seed=$$([$(ProcId)+1])" # start from 0
  args    = f"{outdir} {fullfrag} maxevts={nevts} index=$$([$(ProcId)+1]) seed=$$([$(ProcId)+1])" # start from 1
  if tag:
    args += f" tag={tag}"
  if indices:
    indices_ = [ ]
    for index in indices:
      if isinstance(index,str) and index.count(':')==1:
        start, end = index.split(':') # e.g. '1:4' = [1, 2, 3, 4]
        for i in range(int(start),int(end)+1):
          indices_.append(i)
      else:
        indices_.append(int(index))
    args  = args.replace('$(ProcId)','$(i)')
    queue = f"-queue i in {', '.join(str(i) for i in indices_)}"
    #queue = f"-a 'queue i from ( {', '.join(str(i) for i in indices_)} )'"
  elif first:
    args  = args.replace('$(ProcId)','$(i)')
    queue = f"-queue i from seq {first} {first+njobs-1} \|"
    #queue = f"-a 'queue from seq {first} {njobs}|'"
  else:
    queue   = f"-queue {njobs}"
  name    = f"{os.path.basename(fragment).replace('.py','')}"
  log     = os.path.join(logdir,f"submit_fragment{tag}.$(ClusterId).$(ProcId).log")
  subcmd  = f"condor_submit submit_fragment.sub -a 'initialdir={indir}' -a 'mylogfile={log}'"
  subcmd += f" -a 'arguments={args}'" # -a 'should_transfer_files=no'
  subcmd += f" -batch-name {name} {queue}" #-queue '{queue}'
  if slc6:
    subcmd += f" -a 'requirements = (OpSysAndVer =?= \"SLCern6\")'"
  if verb>=4:
    subcmd += " -verbose"
  print(">>> "+subcmd)
  if not dry:
    os.system(subcmd)
  

def main(args):
  fragments = args.fragments
  nevts     = args.nevts
  first     = args.first
  indices   = args.indices
  njobs     = args.njobs
  tag       = args.tag
  dry       = args.dry
  #slc6      = args.slc6
  outdir    = args.outdir
  logdir    = "log/"
  verbosity = args.verbosity
  
  for oldfrag in fragments:
    tag_ = tag or '_'+os.path.basename(oldfrag).replace('_cfg.py','').replace('.py','')
    
    # PREPARE JOB FRAGMENT
    newfrag = oldfrag.replace('_cfg.py','.py').replace('.py',tag+'_job.py')
    writefragment(oldfrag,newfrag,verb=verbosity)
    
    #### PREPARE CMSSW ENVIRONMENT
    ###cmsenv(oldfrag,verb=verbosity) # breaks library paths
    
    # SUBMIT
    submit(newfrag,njobs,nevts,outdir,first=first,indices=indices,
           logdir=logdir,tag=tag_,dry=dry,verb=verbosity)
  

if __name__ == '__main__':
  from argparse import ArgumentParser
  usage  = """Submit jobs to generate GENSIM samples."""
  user   = getpass.getuser()
  outdir = "/eos/user/%s/%s/GENSIM"%(user[0],user)
  parser = ArgumentParser(prog='submit_fragment',description=usage,epilog="Good luck!")
  parser.add_argument('fragments',        type=str, nargs='+',
                      metavar='FILE',     help="fragment to submit" )
  parser.add_argument('-n', '--nevents',  dest='nevts', default=100,
                                          help="number of event to be generated per job, default=%(default)s")
  parser.add_argument('-N', '--njobs',    type=int, default=2,
                                          help="number of jobs to submit")
  parser.add_argument('-s', '--first',    type=int,
                                          help="first index of job")
  parser.add_argument('-i', '--index',    dest="indices", nargs='+', default=[ ],
                      metavar='INDEX',    help="indices to run over, list of integers or range start:end, e.g. 1:100" )
  #parser.add_argument('-c', '--ncores',   type=int, default=2,
  #                                        help="number of core in each job")
  #parser.add_argument('-q', '--queue',    choices=['all.q','short.q','long.q'], default=None,
  #                    metavar='QUEUE',    help="job queue" )
  parser.add_argument('-t', '--tag',      type=str, default="",
                                          help="extra tag for output")
  parser.add_argument('-o', '--outdir',   type=str, default=outdir,
                                          help="extra tag for output, default=%(default)s")
  parser.add_argument('-d', '--dry',      action='store_true',
                                          help="dry run: do not submit job to batch")
  #parser.add_argument(      '--slc6',     action='store_true',
  #                                        help="specify scl6")
  parser.add_argument('-v', '--verbose',  dest='verbosity', type=int, nargs='?', const=1, default=0,
                                          help="set verbosity, default=%(default)s" )
  args = parser.parse_args()
  #print(">>> ")
  main(args)
  print(">>> Done")
  

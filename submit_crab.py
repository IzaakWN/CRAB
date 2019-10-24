#! /usr/bin/env python
# Author: Izaak Neutelings (October, 2019)
from CRABClient.UserUtilities import getUsernameFromSiteDB
from CRABClient.UserUtilities import config as crabconfig
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from httplib import HTTPException
from utils import filterSamplesWithPattern, formatTag, bold
import re


def main(args):
  
  years   = args.years
  psets   = args.psets if args.psets else [ 
    #"pset_miniAOD_rerun.py",
    "pset_nanoAODv5.py",
  ]
  samples = args.samples
  force   = args.force
  test    = args.test
  tag     = "DeepTau2017v2p1"
  
  for pset in psets:
    
    # SAMPLES
    if 'nanoaod' in pset.lower():
      import samples_nanoAOD
      samplesets = samples_nanoAOD.samples
    else:
      import samples_miniAOD
      samplesets = samples_miniAOD.samples
    
    # SUBMIT
    for year in years:
      datasets = samplesets.get(year,[])
      if samples:
        datasets = filterSamplesWithPattern(datasets,samples)
      submitSampleToCRAB(year,datasets,pset=pset,tag=tag,test=test,force=force)
  


def submitSampleToCRAB(year,samples,**kwargs):
  """Create a CRAB configuration and submit a given list of samples."""
  
  assert isinstance(samples,list), "Samples list should be a list or tuple! Given %s"%samples
  
  # USER OPTIONS
  year          = year
  test          = kwargs.get('test',       0)
  force         = kwargs.get('force',      False)
  psetName      = kwargs.get('pset',       "pset_miniAOD_rerun.py")
  pluginName    = 'Analysis' #'PrivateMC'
  splitting     = 'Automatic' # 'FileBased'
  tag           = kwargs.get('tag',        "")
  instance      = kwargs.get('instance',   'global')
  nevents       = -1
  unitsPerJob   = 1 # files per job for 'FileBased'
  njobs         = -1
  ncores        = kwargs.get('ncores',     1) # make sure nCores > nThreads in pset.py
  maxRunTime    = kwargs.get('maxRunTime', 6*60) #1250 # minutes
  priority      = kwargs.get('priority',   10)
  workArea      = 'crab_projects'
  datatier      = 'nanoAOD' if 'nanoaod' in psetName.lower() else 'miniAOD'
  outdir        = '/store/user/%s/%s_%s%s'%(getUsernameFromSiteDB(),datatier,year,formatTag(tag))
  publish       = True #and False
  site          = 'T2_CH_CSCS'
  
  # OVERRIDE
  if test>0:
    splitting    = 'FileBased'
    unitsPerJob  = 1 # files per job
    njobs        = int(test)
    outdir      += '_test'
    publish      = False
  if splitting=='Automatic':
    unitsPerJob  = -1
    njobs        = -1
    maxRunTime   = -1
  
  # PRINT
  print ">>> "+'='*70
  print ">>> year        = '%s"%year
  print ">>> psetName    = '%s'"%bold(psetName)
  print ">>> pluginName  = '%s'"%pluginName
  print ">>> splitting   = '%s'"%splitting
  print ">>> tag         = '%s'"%bold(tag)
  print ">>> nevents     = %s"%nevents
  print ">>> unitsPerJob = %s"%unitsPerJob
  print ">>> njobs       = %s"%njobs
  print ">>> nCores      = %s"%ncores
  print ">>> maxRunTime  = %s"%maxRunTime
  print ">>> priority    = %s"%priority
  print ">>> workArea    = '%s'"%workArea
  print ">>> site        = '%s'"%site
  print ">>> outdir      = '%s'"%outdir
  print ">>> publish     = %r"%publish
  print ">>> "+'='*70
  
  if len(samples)==0:
    print ">>> No samples given..."
    print ">>> "
    return
  
  # CRAB CONFIGURATION
  config = crabconfig()
  config.General.workArea           = workArea
  config.General.transferOutputs    = True
  config.General.transferLogs       = False
  
  config.JobType.pluginName         = pluginName
  config.JobType.psetName           = psetName
  config.JobType.pyCfgParams        = [ "year=%s"%year, "nThreads=%s"%ncores ]
  config.JobType.numCores           = ncores
  if maxRunTime>0:
    config.JobType.maxJobRuntimeMin = maxRunTime # minutes
  config.JobType.priority           = priority
  
  config.Data.splitting             = splitting
  if unitsPerJob>0:
    config.Data.unitsPerJob         = unitsPerJob
    if njobs>0:
      config.Data.totalUnits        = unitsPerJob * njobs
  config.Site.storageSite           = site
  config.Data.outLFNDirBase         = outdir
  config.Data.publication           = publish
  
  for dataset in samples:
    request  = (datatier.lower().replace('aod','')+'_'+shortenDASPath(dataset))[:100]
    inputDBS = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/"%('phys03' if dataset.endswith('/USER') else instance)
    outtag   = createDatasetOutTag(dataset,tag=tag)
    print ">>> "+'-'*5+" Submitting... "+'-'*50
    print ">>> request     = '%s'"%bold(request)
    print ">>> dataset     = '%s'"%bold(dataset)
    print ">>> inputDBS    = '%s'"%inputDBS
    print ">>> outtag      = '%s'"%outtag
    print ">>> "+'-'*70
    config.General.requestName    = request # max. 100 characters
    config.Data.inputDataset      = dataset
    config.Data.inputDBS          = inputDBS
    #config.Data.outputPrimaryDataset = 'LQ_test' # only for 'PrivateMC'
    config.Data.outputDatasetTag  = outtag
    print str(config).rstrip('\n')
    if force:
      print ">>> Do you want to submit this job to CRAB? [y/n]? force"
      print ">>> Submitting..."
      submitCRABConfig(config)
    else:
      while True:
        submit = raw_input(">>> Do you want to submit this job to CRAB? [y/n]? ")
        if any(s in submit.lower() for s in ['quit','exit']):
          print ">>> Exiting..."
          exit(0)
        elif 'force' in submit.lower():
          submit = 'y'
          force = True
        if 'y' in submit.lower():
          print ">>> Submitting..."
          submitCRABConfig(config)
          break
        elif 'n' in submit.lower():
          print ">>> Not submitting."
          break
        else:
          print ">>> '%s' is not a valid answer, please choose 'y' or 'n'."%submit
    print ">>> "
  


def executeCRABCommand(command,**kwargs):
  """Submit a command and catch exceptions."""
  try:
    crabCommand(command,**kwargs)
  except HTTPException as hte:
    print "Failed submitting task: %s"%(hte.headers)
  except ClientException as cle:
    print "Failed submitting task: %s"%(cle)
  
def submitCRABConfig(config):
  """Submit a single config."""
  executeCRABCommand('submit',config=config)
  


def createDatasetOutTag(dataset,tag=''):
  """Create dataset output tag from DAS path."""
  outtags = dataset.strip('/').split('/')
  assert len(outtags)>=2, "Invalid DAS path '%s'!"%(dataset)
  outtag  = outtags[1]
  if tag:
    outtag += '_'+tag.lstrip('_')
  return outtag
  
def createRequest(string,year=None,tag=""):
  """Create request."""
  request = string.replace('pset_','').replace('.py','')
  if year and str(year) not in request:
    request += "_%s"%(year)
  return request
  
hashpattern = re.compile(r"-(?!v)[0-9a-z]{5,}$")
def shortenDASPath(daspath):
  """Shorten a long DAS path."""
  replace = [
    ('Autumn18',          "RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15"),
    ('Autumn18FlatPU',    "RunIIAutumn18MiniAOD-FlatPU0to70_102X_upgrade2018_realistic_v15"),
    ('Autumn18FlatPURAW', "RunIIAutumn18MiniAOD-FlatPU0to70RAW_102X_upgrade2018_realistic_v15"),
    ('Fall17',            "RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14"),
    ('Fall17newPMX',      "RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14"),
    ('Fall17RECOSIM',     "RunIIFall17MiniAODv2-PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14"),
    ('Fall17v2',          "RunIIFall17MiniAODv2-PU2017_12Apr2018_v2_94X_mc2017_realistic_v14"),
    ('Summer16',          "RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3"),
    ("MG",                "madgraph"),
    ("PY",                "pythia"),
    ("",                  "_13TeV"),
    ("",                  "Tune"),
  ]
  daspath = '_'.join(daspath.split('/')[1:-1])
  for short, long in replace:
    daspath = daspath.replace(long,short)
  daspath = hashpattern.sub("",daspath)
  return daspath
  
def getCampaign(daspath):
  """Return a simple campaign label."""
  for campaign in [ 'Summer16', 'Fall17', 'Autumn18' ]:
    if campaign in daspath:
      return campaign
  return daspath
  


if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('-f', '--force',   dest='force', action='store_true', default=False,
                                         help="submit jobs without asking confirmation" )
  parser.add_argument('-y', '--year',    dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2017], action='store',
                      metavar="YEAR",    help="select year" )
  parser.add_argument('-s', '--sample',  dest='samples', type=str, nargs='+', default=[ ], action='store',
                      metavar="DATASET", help="samples to submit" )
  parser.add_argument('-p', '--pset',    dest='psets', type=str, nargs='+', default=[ ], action='store',
                      metavar="SCRIPT",  help="PSet scripts to submit" )
  parser.add_argument('-t', '--test',    dest='test', type=int, nargs='?', default=-1, const=1,
                      metavar="NJOBS",   help="submit test job(s)" )
  args = parser.parse_args()
  print ">>> "
  main(args)
  #print ">>> "
  


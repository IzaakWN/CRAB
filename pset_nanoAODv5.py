#! /usr/bin/env cmsRun
# Author: Yuta Takahashi & Izaak Neutelings (October, 2019)
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options:
#  step1 --filein dbs:/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/MINIAODSIM --fileout file:SUS-RunIISummer16NanoAODv5-00085.root --mc --eventcontent NANOEDMAODSIM --datatier NANOAODSIM --conditions 102X_mcRun2_asymptotic_v7 --step NANO --nThreads 2 --era Run2_2016,run2_nanoAOD_94X2016 --python_filename SUS-RunIISummer16NanoAODv5-00085_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 100
#  step1 --filein dbs:/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM --fileout file:MUO-RunIIFall17NanoAODv5-00001.root --mc --eventcontent NANOEDMAODSIM --datatier NANOAODSIM --conditions 102X_mc2017_realistic_v7 --step NANO --nThreads 2 --era Run2_2017,run2_nanoAOD_94XMiniAODv2 --python_filename MUO-RunIIFall17NanoAODv5-00001_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 100
#  step1 --filein dbs:/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM --fileout file:MUO-RunIIAutumn18NanoAODv5-00014.root --mc --eventcontent NANOEDMAODSIM --datatier NANOAODSIM --conditions 102X_upgrade2018_realistic_v19 --step NANO --nThreads 2 --era Run2_2018,run2_nanoAOD_102Xv1 --python_filename MUO-RunIIAutumn18NanoAODv5-00014_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 100
print ">>> %s start pset_nanoAODv5.py %s"%('-'*15,'-'*15)
import FWCore.ParameterSet.Config as cms
from utils import formatTag
from eras import globaltags, eras

# DEFAULTS
sample     = "" #"test"
index      = -1
year       = 2017
maxEvents  = -1
nThreads   = 1
director   = "file:root://xrootd-cms.infn.it/"
infiles    = [
  #"file:miniAOD_rerun_%s_%s_%s.root"%(sample,year,index)
  #"file:input/VLQ-p_M1100_2018_rerun.root",
  director+'/store/mc/RunIISummer16MiniAODv3/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/120000/ACDA5D95-3EDF-E811-AC6F-842B2B6AEE8B.root',
  director+'/store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/70000/0256D125-5A44-E811-8C69-44A842CFD64D.root',
  director+"/store/mc/RunIIAutumn18MiniAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/102X_upgrade2018_realistic_v15-v1/100000/08540B6C-AA39-3F49-8FFE-8771AD2A8885.root",
  director+'/store/data/Run2016C/SingleElectron/MINIAOD/17Jul2018-v1/40000/F22B7438-4B8C-E811-A008-0242AC130002.root',
  director+'/store/data/Run2016D/SingleElectron/MINIAOD/17Jul2018-v1/40000/C66CFA48-E18B-E811-A984-3417EBE64B25.root',
  director+'/store/data/Run2016F/SingleElectron/MINIAOD/17Jul2018-v1/50000/5626FF00-1D8B-E811-AA3F-AC1F6B0F6FCE.root',
  director+'/store/data/Run2016H/SingleElectron/MINIAOD/17Jul2018-v1/00000/D0FB608B-5F8A-E811-8FBF-003048FFD7A4.root',
  director+'/store/data/Run2017B/SingleElectron/MINIAOD/31Mar2018-v1/60000/66EAEA69-3E37-E811-BC12-008CFAC91CD4.root',
  director+'/store/data/Run2017C/SingleElectron/MINIAOD/31Mar2018-v1/90000/4075BED6-9D37-E811-9EE6-0025905B85CC.root',
  director+'/store/data/Run2017D/SingleElectron/MINIAOD/31Mar2018-v1/80000/C0051DB1-EE38-E811-AE60-E0071B74AC10.root',
  director+'/store/data/Run2017E/SingleElectron/MINIAOD/31Mar2018-v1/90000/24DC3796-C338-E811-BA7E-00266CFFBEB4.root',
  director+'/store/data/Run2017F/SingleElectron/MINIAOD/31Mar2018-v1/100000/C05D396F-A437-E811-A49D-0025905A6118.root',
  director+'/store/data/Run2018A/EGamma/MINIAOD/17Sep2018-v2/120000/D0C18EBB-8DD7-EC4F-9C1B-CA3EAD44D993.root',
  director+'/store/data/Run2018B/EGamma/MINIAOD/17Sep2018-v1/00000/ADB4BB53-A766-E546-80C7-E2E0058062CD.root',
  director+'/store/data/Run2018C/EGamma/MINIAOD/17Sep2018-v1/110000/16D0608A-36CE-7543-93A4-DD42EA7A417B.root',
  director+'/store/data/Run2018C/EGamma/MINIAOD/17Sep2018-v1/110000/492125B7-444F-844F-A6CD-87045AC0487E.root',
  director+'/store/data/Run2018D/EGamma/MINIAOD/PromptReco-v2/000/320/500/00000/703D2061-0096-E811-A12F-FA163EBDCF4F.root',
  #director+'/store/data/Run2018A/SingleMuon/MINIAOD/17Sep2018-v2/00000/11697BCC-C4AB-204B-91A9-87F952F9F2C6.root',
  #director+'/store/data/Run2018B/SingleMuon/MINIAOD/17Sep2018-v1/100000/7FA66CD1-3158-F94A-A1E0-27BECABAC34A.root',
  #director+'/store/data/Run2018C/SingleMuon/MINIAOD/17Sep2018-v1/110000/8DB2B7A5-F627-2144-8F8F-180A8DA0E90D.root',
  #director+'/store/data/Run2018D/SingleMuon/MINIAOD/PromptReco-v2/000/320/569/00000/3C8C28E7-1A96-E811-BA8D-02163E012DD8.root',
]
dtype      = 'mc' #'data' #if any('/store/data/' in f for f in infiles) else mc
nanoAOD    = '14Dec2018'

# USER OPTIONS
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('analysis')
options.register('year',      year,      mytype=VarParsing.varType.int)
options.register('nThreads',  nThreads,  mytype=VarParsing.varType.int)
options.register('events',    maxEvents, mytype=VarParsing.varType.int)
options.register('sample',    sample,    mytype=VarParsing.varType.string)
options.register('dtype',     dtype,     mytype=VarParsing.varType.string)
options.parseArguments()
year      = options.year
dtype     = options.dtype
nThreads  = options.nThreads
maxEvents = options.events
sample    = options.sample
globaltag = globaltags[dtype]['NanoAODv5'].get(year,'auto:phase1_2017_realistic')
era = eras['NanoAODv5'].get(year,None)
if index>0:
  outfile = "file:nanoAOD_%s%s_%s.root"%(year,formatTag(sample),index)
else:
  outfile = "file:nanoAOD_%s%s.root"%(year,formatTag(sample))
if   year==2016: infiles = filter(lambda f: 'RunIISummer16' in f or '/Run2016' in f or '_2016_' in f,infiles)
elif year==2017: infiles = filter(lambda f: 'RunIIFall17'   in f or '/Run2017' in f or '_2017_' in f,infiles)
elif year==2018: infiles = filter(lambda f: 'RunIIAutumn'   in f or '/Run2018' in f or '_2018_' in f,infiles)
if   dtype=='data': infiles = filter(lambda f: '/store/mc/'   not in f,infiles)
elif dtype=='mc':   infiles = filter(lambda f: '/store/data/' not in f,infiles)

print ">>> sample    = '%s'"%sample
print ">>> index     = %s"%index
print ">>> year      = %s"%year
print ">>> dtype     = '%s'"%dtype
print ">>> maxEvents = %s"%maxEvents
print ">>> globaltag = '%s'"%globaltag
print ">>> infiles   = %s"%infiles
print ">>> outfile   = %s"%outfile
print ">>> "+'-'*55

process = cms.Process(nanoAOD,era)

# IMPORT of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
if dtype=='mc':
  process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
#process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

# INPUT
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, globaltag, '')
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(maxEvents))
process.source = cms.Source("PoolSource",
  fileNames = cms.untracked.vstring(*infiles),
  #eventsToProcess = cms.untracked.VEventRange('1:1-1:10','2:1-2:10'), # only check few events and runs
  secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
)

# PRODUCTION INFO
process.configurationMetadata = cms.untracked.PSet(
  annotation = cms.untracked.string('step1 nevts:10000'),
  name = cms.untracked.string('Applications'),
  version = cms.untracked.string('$Revision: 1.19 $')
)

# OUTPUT
if dtype=='mc':
  process.NANOAODSIMoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
      dataTier = cms.untracked.string('NANOAODSIM'),
      filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string(
      outfile
    ),
    outputCommands = process.NANOAODSIMEventContent.outputCommands,
    fakeNameForCrab = cms.untracked.bool(True)
  )
  ###process.NANOEDMAODSIMoutput = cms.OutputModule("PoolOutputModule",
  ###    compressionAlgorithm = cms.untracked.string('LZMA'),
  ###    compressionLevel = cms.untracked.int32(9),
  ###    dataset = cms.untracked.PSet(
  ###        dataTier = cms.untracked.string('NANOAODSIM'),
  ###        filterName = cms.untracked.string('')
  ###    ),
  ###    fileName = cms.untracked.string('file:EXO-RunIIAutumn18NanoAODv4-00116.root'),
  ###    outputCommands = process.NANOAODSIMEventContent.outputCommands
  ###)
else:
  process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string(
      outfile
    ),
    outputCommands = process.NANOAODEventContent.outputCommands
)

# Path and EndPath definitions
if dtype=='mc':
  process.nanoAOD_step = cms.Path(process.nanoSequenceMC)
  process.endjob_step = cms.EndPath(process.endOfProcess)
  process.NANOAODSIMoutput_step = cms.EndPath(process.NANOAODSIMoutput)
  #process.NANOEDMAODSIMoutput_step = cms.EndPath(process.NANOEDMAODSIMoutput)
  output_step = process.NANOAODSIMoutput_step
else:
  process.nanoAOD_step = cms.Path(process.nanoSequence)
  process.endjob_step = cms.EndPath(process.endOfProcess)
  process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)
  output_step = process.NANOAODoutput_step

# SCHEDULE
#process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOEDMAODSIMoutput_step)
process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,output_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
if dtype=='mc':
  process.particleLevelSequence.remove(process.genParticles2HepMCHiggsVtx)
  process.particleLevelSequence.remove(process.rivetProducerHTXS)
  process.particleLevelTables.remove(process.HTXSCategoryTable)

# Setup FWK for multithreaded
process.options.numberOfThreads = cms.untracked.uint32(nThreads)
process.options.numberOfStreams = cms.untracked.uint32(0)

# PROCESS CUSTOMIZATION
from Configuration.DataProcessing.Utils import addMonitoring
if dtype=='mc':
  from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeMC as nanoAOD_customize
else:
  from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeData as nanoAOD_customize
process = nanoAOD_customize(process)
process = addMonitoring(process)

# COMMAND LINE CUSTOMIZATION
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process) # early deletion of temporary data products to reduce peak memory need

print ">>> %s done pset_nanoAODv5.py %s"%('-'*15,'-'*16)
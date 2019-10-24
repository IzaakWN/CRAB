#! /usr/bin/env cmsRun
# Author: Yuta Takahashi & Izaak Neutelings (October, 2019)
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options:
#  step1 --filein dbs:/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/MINIAODSIM --fileout file:SUS-RunIISummer16NanoAODv5-00085.root --mc --eventcontent NANOEDMAODSIM --datatier NANOAODSIM --conditions 102X_mcRun2_asymptotic_v7 --step NANO --nThreads 2 --era Run2_2016,run2_nanoAOD_94X2016 --python_filename SUS-RunIISummer16NanoAODv5-00085_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 100
#  step1 --filein dbs:/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM --fileout file:MUO-RunIIFall17NanoAODv5-00001.root --mc --eventcontent NANOEDMAODSIM --datatier NANOAODSIM --conditions 102X_mc2017_realistic_v7 --step NANO --nThreads 2 --era Run2_2017,run2_nanoAOD_94XMiniAODv2 --python_filename MUO-RunIIFall17NanoAODv5-00001_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 100
#  step1 --filein dbs:/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM --fileout file:MUO-RunIIAutumn18NanoAODv5-00014.root --mc --eventcontent NANOEDMAODSIM --datatier NANOAODSIM --conditions 102X_upgrade2018_realistic_v19 --step NANO --nThreads 2 --era Run2_2018,run2_nanoAOD_102Xv1 --python_filename MUO-RunIIAutumn18NanoAODv5-00014_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 100
print ">>> "+"%s start pset_nanoAODv5.py %s"%('-'*15,'-'*15)
import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
from utils import formatTag

# DEFAULTS
sample     = "" #"test"
index      = -1
year       = 2018
maxEvents  = -1
nThreads   = 1
director   = "file:root://xrootd-cms.infn.it/"
infiles    = [
  #"file:miniAOD_rerun_%s_%s_%s.root"%(sample,year,index)
  "file:input/VLQ-p_M1100_2018_rerun.root",
]
nanoAOD    = '14Dec2018'
globaltags = {
  # https://docs.google.com/presentation/d/1YTANRT_ZeL5VubnFq7lNGHKsiD7D3sDiOPNgXUYVI0I/edit#slide=id.g61f8771f52_33_8
  'default': 'auto:phase1_2017_realistic',
  2016:      '102X_mcRun2_asymptotic_v7',
  2017:      '102X_mc2017_realistic_v7', #'94X_mc2017_realistic_v14',
  2018:      '102X_upgrade2018_realistic_v19', #'102X_upgrade2018_realistic_v20', #'102X_upgrade2018_realistic_v15',
}
eras = {
  2016: eras.run2_nanoAOD_94X2016,
  2017: eras.run2_nanoAOD_94XMiniAODv2,
  2018: eras.run2_nanoAOD_102Xv1,
}

# USER OPTIONS
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('analysis')
options.register('year',     year,     mytype=VarParsing.varType.int)
options.register('nThreads', nThreads, mytype=VarParsing.varType.int)
options.parseArguments()
year     = options.year
nThreads = options.nThreads
###import sys
###args = sys.argv
####assert len(args)>=4, "Only %s arguments given, please provide 4!"%(len(args))
###if len(args)>=4:
###  sample = args[2]
###  index  = args[3]
globaltag = globaltags.get(year,'auto:phase1_2017_realistic')
era = eras.get(year,None)
if index>0:
  outfile = "file:nanoAOD_%s%s_%s.root"%(formatTag(sample),year,index)
else:
  outfile = "file:nanoAOD_%s_%s.root"%(formatTag(sample),year)

print ">>> sample    = '%s'"%sample
print ">>> index     = %s"%index
print ">>> year      = '%s"%year
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
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

# INPUT
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, globaltag, '')
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(maxEvents))
process.source = cms.Source("PoolSource",
  fileNames = cms.untracked.vstring(*infiles),
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

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.nanoSequenceMC)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODSIMoutput_step = cms.EndPath(process.NANOAODSIMoutput)
#process.NANOEDMAODSIMoutput_step = cms.EndPath(process.NANOEDMAODSIMoutput)

# SCHEDULE
#process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOEDMAODSIMoutput_step)
process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOAODSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# Setup FWK for multithreaded
process.options.numberOfThreads = cms.untracked.uint32(nThreads)
process.options.numberOfStreams = cms.untracked.uint32(0)

# PROCESS CUSTOMIZATION
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeMC
from Configuration.DataProcessing.Utils import addMonitoring
process = nanoAOD_customizeMC(process)
process = addMonitoring(process)

# COMMAND LINE CUSTOMIZATION
process.particleLevelSequence.remove(process.genParticles2HepMCHiggsVtx);process.particleLevelSequence.remove(process.rivetProducerHTXS);process.particleLevelTables.remove(process.HTXSCategoryTable)
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process) # early deletion of temporary data products to reduce peak memory need

print '%s done pset_nanoAODv5.py %s'%('-'*15,'-'*16)
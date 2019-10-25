#! /usr/bin/env cmsRun
# Author: Yuta Takahashi & Izaak Neutelings (October, 2019)
# Produce pat::Tau collection with the new DNN Tau-Ids from miniAOD 12Apr2018_94X_mc2017
# dasgoclient --limit=0 --query="dataset=/DYJetsToLL_M-50_TuneC*_13TeV-madgraphMLM-pythia8/*NanoAODv5*/NANOAOD*"
print ">>> "+"%s start pset_miniAOD_rerun.py %s"%('-'*15,'-'*15)
import FWCore.ParameterSet.Config as cms
from utils import formatTag

# DEFAULTS
sample         = "" #"test"
index          = -1
year           = 2018
minimalOutput  = False
maxEvents      = 1000
nThreads       = 2
updatedTauName = "slimmedTausNewID"
director       = "file:root://xrootd-cms.infn.it/"
infiles        = [
  #director+"/store/mc/RunIISummer16MiniAODv3/PairVectorLQ_InclusiveDecay_M-1100_TuneCP2_13TeV-madgraph-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/240000/1850729C-C68B-E911-8FFD-7CD30ACE15D0.root",
  #director+"/store/mc/RunIIFall17MiniAODv2/PairVectorLQ_InclusiveDecay_M-1100_TuneCP2_13TeV-madgraph-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/30000/CE874F0A-1988-E911-9804-AC1F6B23C7DA.root",
  #director+"/store/mc/RunIIAutumn18MiniAOD/PairVectorLQ_InclusiveDecay_M-1100_TuneCP2_13TeV-madgraph-pythia8/MINIAODSIM/102X_upgrade2018_realistic_v15-v1/30000/F3649753-9038-CF4B-A178-BD03655BE7BD.root",
  "file:input/VLQ-p_M1100_%s.root"%year,
  #"file:miniAOD_%s_%s_%s.root"%(sample,year,index),
]
globaltags = {
  # https://docs.google.com/presentation/d/1YTANRT_ZeL5VubnFq7lNGHKsiD7D3sDiOPNgXUYVI0I/edit#slide=id.g61f8771f52_33_8
  'default': 'auto:phase1_2017_realistic',
  2016:      '94X_mcRun2_asymptotic_v3',
  2017:      '94X_mc2017_realistic_v17', #'94X_mc2017_realistic_v14',
  2018:      '102X_upgrade2018_realistic_v20', #'102X_upgrade2018_realistic_v15',
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
if index>0:
  outfile = "file:miniAOD_rerun_%s%s_%s.root"%(year,formatTag(sample),index)
else:
  outfile = "file:miniAOD_rerun_%s%s.root"%(year,formatTag(sample))

print ">>> sample    = '%s'"%sample
print ">>> index     = '%s'"%index
print ">>> year      = '%s"%year
print ">>> maxEvents = %s"%maxEvents
print ">>> globaltag = '%s'"%globaltag
print ">>> infiles   = %s"%infiles
print ">>> outfile   = %s"%outfile
print ">>> "+'-'*69

process = cms.Process('TauID')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.Geometry.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')

# GLOBAL TAG
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, globaltag, '')

# INPUT
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(maxEvents) )
process.source = cms.Source('PoolSource', 
  fileNames = cms.untracked.vstring(*infiles),
  #eventsToProcess = cms.untracked.VEventRange('1:1-1:10','2:1-2:10')
)

# ADD new TauIDs
import RecoTauTag.RecoTau.tools.runTauIdMVA as tauIdConfig
tauIdEmbedder = tauIdConfig.TauIDEmbedder(
                  process, cms, debug = False,
                  updatedTauName = updatedTauName,
                  toKeep = [
                    #"2017v2", "dR0p32017v2", "newDM2017v2", "againstEle2018"
                    "deepTau2017v2p1",
                  ])
tauIdEmbedder.runTauID()

# OUTPUT
process.out = cms.OutputModule("PoolOutputModule",
  fileName = cms.untracked.string(
    outfile
  ),
  compressionAlgorithm = cms.untracked.string('LZMA'),
  compressionLevel = cms.untracked.int32(4),
  outputCommands = cms.untracked.vstring('drop *')
)
if not minimalOutput:
  print("Store full MiniAOD EventContent")
  from Configuration.EventContent.EventContent_cff import MINIAODSIMEventContent
  from PhysicsTools.PatAlgos.slimming.MicroEventContent_cff import MiniAODOverrideBranchesSplitLevel
  process.out.outputCommands = MINIAODSIMEventContent.outputCommands
  process.out.overrideBranchesSplitLevel = MiniAODOverrideBranchesSplitLevel
process.out.outputCommands.append("keep *_"+updatedTauName+"_*_*")

# PATH
process.p = cms.Path(
  process.rerunMvaIsolationSequence * getattr(process,updatedTauName)
)
process.endjob = cms.EndPath(process.endOfProcess)
process.outpath = cms.EndPath(process.out)

# SCHEDULE
process.schedule = cms.Schedule(process.p,process.endjob,process.outpath)

# PRINT OUT
process.load('FWCore.MessageLogger.MessageLogger_cfi')
if process.maxEvents.input.value()>10:
  process.MessageLogger.cerr.FwkReport.reportEvery = process.maxEvents.input.value()//10
if process.maxEvents.input.value()>10000 or process.maxEvents.input.value()<0:
  process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.options = cms.untracked.PSet(
  wantSummary = cms.untracked.bool(False),
  numberOfThreads = cms.untracked.uint32(nThreads),
  numberOfStreams = cms.untracked.uint32(0)
)

print ">>> "+"%s done pset_miniAOD_rerun.py %s"%('-'*15,'-'*16)
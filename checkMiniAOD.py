#! /usr/bin/env python
# Author: Izaak Neutelings (August 2019)
# Description: Check miniAOD by doing some print-out
# Source:
#  https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD2016#Example_code_accessing_all_high
#  https://github.com/kschweiger/ToolBox/blob/master/ROOTBox/checkMiniAODEventContent.py
#  https://github.com/kschweiger/HLTBTagging/blob/master/nTuples/ntuplizerHLT_phaseI.py
# Triggers:
#  https://github.com/cms-sw/cmssw/blob/a41ba6cb802a727726f33a31be291ca441534016/DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h
#  https://github.com/cms-sw/cmssw/blob/master/DataFormats/HLTReco/interface/TriggerTypeDefs.h
#  https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATTrigger#Original_Data_Sources (TODO)
#  help(ROOT.pat.TriggerObjectStandAlone)
from DataFormats.FWLite import Handle, Events
from argparse import ArgumentParser
from ROOT import gROOT
#gROOT.Macro("getHLTConfigProvider.C+")

parser = ArgumentParser()
parser.add_argument('-n', '--nmax', dest='nmax', action='store', type=int, default=20,
                                    help="maximum number of events")
args = parser.parse_args()

trigObjTypes = {
  0: 'none', 81: 'photon', 82: 'electron', 83: 'muon', 84: 'tau',
  85: 'jet', 86: 'bjet', 87: 'MET', 88: 'MET', 89: 'ak8jet', 90: 'ak8jet',
  91: 'track',
}
filters = { }



def checkTauObjects(filename,nmax):
    print ">>> checkTauObjects: %s"%(filename)
    taus, tauLabel = Handle("std::vector<pat::Tau>"), "slimmedTaus"
    events = Events(filename)
    for ievent, event in enumerate(events,1):
      if ievent>nmax: break
      print ">>> %s event %1d %s"%('-'*10,ievent,'-'*60)
      event.getByLabel(tauLabel,taus)
      for itau, tau in enumerate(taus.product()):
        ###if tau.pt()<20: continue
        #print "tau  %2d: pt %4.1f, dxy signif %.1f"%(itau,tau.pt(),tau.dxy_Sig())
        print ">>>   tau  %2d: pt %4.1f, dxy signif %.1f, ID(byTightIsolationMVArun2v1DBoldDMwLT) %.1f, lead candidate pt %.1f, pdgId %d "%(
                    itau,tau.pt(),tau.dxy_Sig(), tau.tauID("byTightIsolationMVArun2v1DBoldDMwLT"), tau.leadCand().pt(), tau.leadCand().pdgId())
    print '-'*80
    


def checkTriggerPaths(filename,nmax):
    print ">>> checkTriggerPaths: %s"%(filename)
    mytrignames = ['HLT_IsoMu','HLT_Ele','PFTau']
    triggerBits, triggerBitLabel = Handle("edm::TriggerResults"), "TriggerResults::HLT"
    events = Events(filename)
    for ievent, event in enumerate(events,1):
      if ievent>nmax: break
      print ">>> %s event %1d %s"%('-'*10,ievent,'-'*60)
      event.getByLabel(triggerBitLabel,triggerBits)
      triggerNames = event.object().triggerNames(triggerBits.product())
      for itrig, trigname in enumerate(triggerNames.triggerNames(),1):
        if 'HLT_' not in trigname: continue
        if not any(p in trigname for p in mytrignames): continue
        index = triggerNames.triggerIndex(trigname)
        fired = triggerBits.product().accept(index)
        if fired:
          print ">>>   trigger %2d: %s"%(itrig,bold(trigname+" (fired)"))
        else:
          print ">>>   trigger %2d: %s"%(itrig,trigname)
    print '-'*80
    


def checkTriggerObjects(filename,nmax):
    print ">>> checkTriggerObjects: %s"%(filename)
    mytrignames   = ['Tau'] #['Ele','IsoMu','Tau']
    mytrigfilters = [ ]
    mytrigtypes   = [84] #[82,83,84]
    ptmin         = 20
    print ">>>   %-14s = %s"%('mytrignames',mytrignames)
    print ">>>   %-14s = %s"%('mytrigtypes',mytrigtypes)
    print ">>>   %-14s = %s"%('mytrigfilters',mytrigfilters)
    print ">>>   %-14s = %s"%('ptmin',ptmin)
    triggerBits, triggerBitLabel = Handle("edm::TriggerResults"), "TriggerResults::HLT"
    triggerObjects, triggerObjectLabel = Handle("std::vector<pat::TriggerObjectStandAlone>"), "slimmedPatTrigger"
    events = Events(filename)
    for ievent, event in enumerate(events,1):
      if ievent>nmax: break
      ###print ">>> %s event %1d %s"%('-'*10,ievent,'-'*60)
      event.getByLabel(triggerBitLabel,triggerBits)
      event.getByLabel(triggerObjectLabel,triggerObjects)
      #triggerNames = event.object().triggerNames(triggerBits.product())
      for itrig, trigobj in enumerate(triggerObjects.product(),1):
        if trigobj.pt()<ptmin: continue
        if not any(t in mytrigtypes for t in trigobj.triggerObjectTypes()): continue
        trigobj.unpackNamesAndLabels(event.object(),triggerBits.product())
        if not any(isTauTrigger(n) for n in trigobj.pathNames()): continue
        ###types = [t for t in trigobj.triggerObjectTypes()]
        ###print ">>>   trigfilter %2d: pt %4.1f, type %s"%(itrig,trigobj.pt(),types)
        for trigfilter in trigobj.filterLabels():
          ###if not any(p in trigfilter for p in mytrignames): continue
          ###print ">>>     filter %s"%trigfilter
          if trigfilter not in filters:
            filters[trigfilter] = { }
          for trigname in trigobj.pathNames():
            if trigname in filters[trigfilter]:
              filters[trigfilter][trigname] += 1
            else:
              filters[trigfilter][trigname]  = 1
        ###for trigname in trigobj.pathNames():
        ###  print ">>>     path   %s"%trigname
    ###print '-'*80
    

def isTauTrigger(string):
  if 'PFTau' not in string:
    return False
  return any(p in string for p in ['Ele','IsoMu','Double'])
  


def bold(string):
  return '\033[1m'+string+'\033[0m'
  


def main():
    
    nmax     = args.nmax
    director = "root://xrootd-cms.infn.it/"
    
    filenames = [
      #"miniAOD_test_1_rerun.root",
      "/store/mc/RunIIAutumn18MiniAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/102X_upgrade2018_realistic_v15-v1/100000/08540B6C-AA39-3F49-8FFE-8771AD2A8885.root",
    ]
    
    for filename in filenames:
      if '/store/' in filename and 'root:' not in filename:
        filename = director+filename
      checkTauObjects(filename,nmax=nmax)
      ###checkTriggerPaths(filename,nmax=nmax)
      ###checkTriggerObjects(filename,nmax=nmax)
    
    ###for filter, paths in sorted(filters.items()):
    ###  print ">>>\n>>> filter %s"%filter
    ###  for path, hits in sorted(paths.items(),key=lambda x: x[1]):
    ###    print ">>>   %3d %s"%(hits,path)
    ###print ">>> "
    


if __name__ == '__main__':
    main()
    


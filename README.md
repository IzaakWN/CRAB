# CRAB

Process `miniAOD` or `nanoAOD` files with `CRAB3`.


## Installation

First, get this repository:
```
git clone https://github.com/IzaakWN/CRAB CRAB
cd CRAB
```
then get the relevant `CMSSW`, e.g.:
```
CMSSW=CMSSW_10_2_16_patch1
export SCRAM_ARCH=slc6_amd64_gcc700
cmsrel $CMSSW
cd $CMSSW/src
cmsenv
scram b -j4
cd ../..
```
When you want to use CRAB with `SLC6`, you need to do:
```
source $VO_CMS_SW_DIR/crab3/crab_slc6.sh
```
or if you are using `SLC7`,
```
source $VO_CMS_SW_DIR/crab3/crab_slc6.sh
```


### DeepTauID
In case you want to use `DeepTau2017v2p1` in `102X` samples,
```
CMSSW=CMSSW_10_2_16_patch1
export SCRAM_ARCH=slc6_amd64_gcc700
cmsrel $CMSSW
cd $CMSSW/src/
cmsenv
git cms-merge-topic -u cms-tau-pog:CMSSW_10_2_X_tau-pog_DeepTau2017v2
git cms-merge-topic -u cms-tau-pog:CMSSW_10_2_X_tau-pog_deepTauVetoPCA
sed 's/idDeepTau2017v2/idDeepTau2017v2p1/g' PhysicsTools/NanoAOD/python/taus_cff.py -i
sed 's/rawDeepTau2017v2/rawDeepTau2017v2p1/g' PhysicsTools/NanoAOD/python/taus_cff.py -i
scram b -j 4
cd ../..
```


### Environment setup

With each new shell session, do something like
```
source $VO_CMS_SW_DIR/cmsset_default.sh
source $VO_CMS_SW_DIR/crab3/crab_slc6.sh
export SCRAM_ARCH=slc6_amd64_gcc700
cd CMSSW_10_2_16_patch1/src
cmsenv
cd ../..
```


## Local run

Reprocess `miniAOD` to add `DeepTau2017v2p1` with
```
cmsRun pset_miniAOD_rerun.py
```

Process `miniAOD` to `nanoAODv5` with
```
cmsRun pset_nanoAODv5.py
```



## Submit

Collect your favorite samples in the respective python file, sorted in a dictionary per year:
```
samples_miniAOD.py
samples_nanoAOD.py
```

Then you can submit with
```
./submit_crab.py -y 2017
```

To filter a specific sample, do e.g.
```
./submit_crab.py -y 2017 -s DY*Jets
```


## Notes

### NanoAOD

* **working book**: https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD
* **2016 `9_4_X`**: https://cms-nanoaod-integration.web.cern.ch/integration/master/mc94X2016_doc.html
* **2017 `9_4_X`**: https://cms-nanoaod-integration.web.cern.ch/integration/master/mc94X_doc.html
* **2018 `10_2_X`**: https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/mc102X_doc.html

More [notes](https://www.evernote.com/l/Ac8PKYGpaJxJArj4eng5ed95_wvpzwSNTgc).


### Samples

[PPD Run II summary table](https://docs.google.com/presentation/d/1YTANRT_ZeL5VubnFq7lNGHKsiD7D3sDiOPNgXUYVI0I/edit#slide=id.g4dfd66f53d_1_7)
* **2016**: [list](samples_2016.cfg), [DAS](https://cmsweb.cern.ch/das/request?view=plain&limit=50&instance=prod%2Fglobal&input=dataset%3D%2F*%2FRunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic*%2FNANOAODSIM), [notes](https://www.evernote.com/l/Ac9nVeF2tcdJI7R-is1KPT2Ukv7A260zNX0)
* **2017**: [list](samples_2017.cfg), [DAS](https://cmsweb.cern.ch/das/request?view=plain&limit=50&instance=prod%2Fglobal&input=dataset+dataset%3D%2F*%2F*94X*_realistic_v14*%2FNANOAOD*), [notes](https://www.evernote.com/l/Ac8WfL3Mzx1MrKdm1LfIOl-F-j7NeScPKxs)
* **2018**: [list](samples_2018.cfg), [DAS](https://cmsweb.cern.ch/das/request?view=plain&limit=50&instance=prod%2Fglobal&input=%2F*%2FRunIIAutumn18NanoAODv4-Nano14Dec2018*%2FNANOAODSIM), [notes](https://www.evernote.com/l/Ac9yyi7wtg9LaYgxOIz11jFyzLV0ztkemtE)

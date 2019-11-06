#! /usr/bin/env python
# Author: Izaak Neutelings (November, 2019)
# Source:
#   git clone git@github.com:cms-sw/genproductions.git genproductions
#   cd genproductions/bin/MadGraph5_aMCatNLO/
#   ./gridpack_generation.sh <process name without _proc_card.dat> <card dir>
import os, re, glob
import itertools
import subprocess
from utils import formatTag, bold, error
from create_cards import makeCardLabel, makeCardName, makeCard


def main(args):
  
  carddir    = args.carddir
  sample     = args.sample
  years      = args.years
  cardlabel  = args.cardlabel
  masses     = args.masses
  params     = args.params
  tag        = args.tag
  test       = args.test
  cmsswdir   = "/work/ineuteli/production/LQ_Legacy/CMSSW_10_2_16_patch1" # TODO: automatic or user-set
  genproddir = "genproductions/bin/MadGraph5_aMCatNLO"
  workdir    = "%s/src/%s"%(cmsswdir,genproddir)
  assert os.path.isdir(cmsswdir), error("CMSSW directory '%s' does not exists!"%(cmsswdir))
  assert os.path.isdir(workdir), error("Working directory '%s' does not exists!"%(workdir))
  oldcarddir = carddir[:]
  
  # CHECK environment
  assert not os.getenv('CMSSW_BASE'), error("A CMSSW environment is set. Please retry in a clean shell session.")
  assert os.getenv('CMS_PATH'), error("No CMS default environment set! Please do 'source $VO_CMS_SW_DIR/cmsset_default.sh' first.")
  
  # CREATE POINTS
  if masses:
    keys   = ['MASS']
    params = [('MASS',masses)] #{ 'MASS': masses }
  else:
    keys   = [ ]
    params = [ ]
  if args.params:
    for param in args.params.split(':'):
      assert '=' in param, "Invalid format '%s'; no '=' for '%s'"%(args.params,param)
      param, values = param[:param.index('=')], param[param.index('=')+1:].split(',')
      assert param not in keys, error("Key '%s' defined multiple times!"%param)
      keys.append(param)
      params.append((param,values))
      #params[param] = values
  if not cardlabel:
    cardlabel = '_'.join(k[0]+'$'+k for k in keys)
  if 'OUTPUT' not in keys:
    keys.append('OUTPUT')
    params.append(('OUTPUT',["$SAMPLE_%s"%cardlabel]))
  if params:
    points    = list(itertools.product(*[v for k, v in params]))
    pattern   = os.path.join(carddir,"%s_template*.dat"%(sample))
    templates = glob.glob(pattern)
    assert templates, error("Did not find any template cards '%s' in %s!"%(os.path.basename(pattern),carddir))
  else:
    points    = [ ]
    templates = [ ]
  
  # PRINT
  print ">>> "+'='*90
  print ">>> cmsswdir    = '%s'"%cmsswdir
  print ">>> genproddir  = '%s'"%genproddir
  print ">>> workdir     = '%s'"%workdir
  print ">>> sample      = '%s'"%sample
  print ">>> carddir     = '%s'"%bold(carddir)
  print ">>> params      = %s"%', '.join("%s: %s"%(bold(k),l) for k, l in params)
  print ">>> templates   = '%s'"%"', '".join(bold(os.path.basename(t)) for t in templates)
  print ">>> "+'='*90
  
  # GENERATE
  if points:
    samplenames = [ ]
    for values in points:
      kwargs = { }
      for key, value in zip(keys,values):
        kwargs[key] = value
      for template in templates:
        cardname = makeCardName(template,cardlabel,**kwargs)
        makeCard(template,cardname,**kwargs)
      samplenames.append("%s_%s"%(sample,makeCardLabel(cardlabel,**kwargs)))
    carddir    = os.path.relpath(carddir,workdir)
    os.chdir(workdir)
    for samplename in samplenames:
      generateGridpack(carddir,samplename)
  else:
    carddir    = os.path.relpath(carddir,workdir)
    os.chdir(workdir)
    generateGridpack(carddir,sample)
  


def generateGridpack(carddir,sample,**kwargs):
  """Create a CRAB configuration and submit a given list of samples."""
  
  cards = [os.path.basename(f) for f in glob.glob("%s/%s_*.dat"%(carddir,sample))]
  
  # PRINT
  print ">>> "
  print ">>> "+'-'*100
  #print ">>> year        = %s"%year
  print ">>> sample      = '%s'"%bold(sample)
  print ">>> cards       = '%s'"%"', '".join(c.replace(sample,'*') for c in cards)
  #print ">>> carddir     = '%s'"%bold(carddir)
  extraopts = ""#%()
  command = './gridpack_generation.sh %s %s'%(sample,carddir)
  command = command.rstrip()
  print ">>> "+bold(command)
  #subprocess.Popen(command, shell=True)
  os.system(command)
  print ">>> "+'-'*100
  


if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('carddir',           type=str, action='store',
                       metavar='CARDDIR',  help="directoy with cards" )
  parser.add_argument('sample',            type=str, action='store',
                       metavar='SAMPLE',   help="name of sample" )
  #parser.add_argument('-f', '--force',     action='store_true', default=False,
  #                                         help="submit jobs without asking confirmation" )
  #parser.add_argument('-c', '--copy',      action='store_true', default=False,
  #                                         help="copy cards into new directory in the same directory as gridpack_generation.sh" )
  parser.add_argument('-y', '--year',      dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2017], action='store',
                                           help="select year" )
  parser.add_argument('-m', '--mass',      dest='masses', type=int, nargs='+', default=[ ], action='store',
                                           help="generate this mass points" )
  parser.add_argument('-t', '--tag',       type=int, nargs='?', default=-1, const=1,
                                           help="tag" )
  parser.add_argument('-T', '--test',      type=int, nargs='?', default=-1, const=1,
                      metavar="NJOBS",     help="submit test job(s)" )
  parser.add_argument('-n', '--cardlabel', type=str, action='store', default=None,
                                           help="card label replacing" )
  parser.add_argument('-p', '--param',     dest='params', default="",
                      metavar="PARAMS",    help="single string of parameters separated by colons,"+\
                                                "each with a list of values separated commas" )
  args = parser.parse_args()
  print ">>> "
  main(args)
  print ">>> "
  


#! /usr/bin/env python
# Author: Izaak Neutelings (November 2019)
# Usage:
#  ./create_cards.py cards/LQ_template_*.dat -n '$NAME_$MASS_L$LAMBDA_NNPDF31_LO' -m 1000 -p LAMBDA=0.1,1.0,1.5:PDF=315200
# Source:
#   git clone git@github.com:cms-sw/genproductions.git genproductions
#   cd genproductions/bin/MadGraph5_aMCatNLO/
# Examples
#   ./create_cards.py cards/ScalarLQ_Single/*template*dat -m 800 1100 1500 -p 'LAMBDA=0.5,1.0,1.5,2.0,2.5'
from __future__ import print_function # for python3 compatibility
import os, re, glob, math
import itertools
from collections import OrderedDict
from utils import formatTag, bold, error, warning, green, ensuredir
paramrexp   = re.compile(r"\$([a-zA-Z0-9.-]+)") #re.compile(r"\$(\w+)")
defaultrexp = re.compile(r"(\$\{(\w+)=([^}]+)\})")
cardrexp    = re.compile(r"(.+)(_[^_]+(?<!_card)(?<!_FKS_params)\.dat|_[^_]+_card\.dat|_FKS_params\.dat)$") # *_run_card.dat, *_custumizecards.dat, ...
  

def computeBWCutoff(model,mass,lambd,default=15,Gamma=0):
  """Ensure the BW cutoff is not too large and only captures the BW peak for resonant LQ production."""
  if not Gamma:
    if 'scalar' in model.lower():
      Gamma = lambd**2*mass/(16*math.pi)
    else:
      Gamma = lambd**2*mass/(24*math.pi)
  mcut = default
  mmin = mass-mcut*Gamma # window cut
  #print(">>> mass=%s, lamda=%s, Gamma=%s, mmin=%s"%(mass,lambd,Gamma,mmin))
  flat = 0.51*mass # maximum window cut, flat in lambda
  if mmin<flat:
    mcut = max(8,round(2*flat/Gamma))/2.0
    #mcut = max(default,round(2*flat/Gamma)/2.0)
  return mcut
  

def getcards(carddir,name):
  """Find all cards of a given sample in a directory."""
  cards = [ ]
  for card in glob.glob("%s/%s_*.dat"%(carddir,name)):
    card = os.path.basename(card)
    match = cardrexp.match(card)
    if match and match.group(1)!=name:
      continue
    cards.append(card)
  return cards
  

def getname(template):
  """Get the sample name from a card name
     e.g. 'LQ_M500' for 'LQ_M500_proc_card.dat'."""
  template = os.path.basename(template) # remove indir
  if '_template_' in template: # e.g. 'LQ_template_proc_card.dat'
    index1 = template.rindex('_template_')
    name = template[index1:]
  elif template.endswith('_card.dat') and template.count('_')>=2:  # e.g. 'LQ_proc_card.dat'
    index1 = template.rindex('_',0,len(template)-len('_card.dat'))
    name = template[index1:]
  ###elif template.count('_')>=1: # e.g. 'LQ_proc.dat'
  ###  index1 = template.rindex('_')
  ###  index2 = index1+1
  ###elif outdir: # get name from outdir
  ###  name = os.path.basename(s.rstrip('/'))
  ###  card = os.path.basename(template) # e.g. 'proc_card.dat'
  ###elif indir.replace('card/','').replace('cards/','').count('/')>=1: # get name from parent directory of template
  ###  name = indir.replace('card/','').replace('cards/','').rstrip('/'))
  ###  card = os.path.basename(template) # e.g. 'proc_card.dat'
  else: # prevent overwriting template
    raise IOError(error("Template card %r does not have a correct format. It should contain 'template', or at least '*_*_card.dat'."%(template)))
  ###template = os.path.basename(template)
  ###if 'template' in template:
  ###  samplename = template[:template.index('template')].rstrip('_')
  ###else:
  ###  match = cardrexp.match(template)
  ###  if match:
  ###    samplename = match.group(1)
  ###  else:
  ###    samplename = template.rstrip('.dat')
  ###    print(warning("getname: Did not find sample name in '%s'!"%samplename,pre=">>> "))
  ###elif template.endswith('_card.dat') and template.count('_')>=2:
  ###  index = template.rindex('_',0,len(template)-len('_card.dat'))
  ###  samplename = template[:index]
  ###elif template.count('_')>=1:
  ###  index = template.rindex('_')
  ###  samplename = template[:index]
  ###else:
  ###  samplename = template.rstrip('.dat')
  ###  print(warning("getname: Did not find sample name in '%s'!"%samplename,pre=">>> "))
  return name
  

def getcardname(template):
  """Get the model/process name and cardname from a card template,
     e.g. ('LQ_M500','proc_card.dat') for 'LQ_M500_proc_card.dat'."""
  template = os.path.basename(template) # remove indir
  if '_template_' in template: # e.g. 'LQ_template_proc_card.dat'
    index1 = template.rindex('_template_')
    index2 = index1+10
  elif template.endswith('_card.dat') and template.count('_')>=2:  # e.g. 'LQ_proc_card.dat'
    index1 = template.rindex('_',0,len(template)-len('_card.dat'))
    index2 = index1+1
  else: # prevent overwriting template
    raise IOError(error("Template card %r does not have a correct format. It should contain 'template', or at least '*_*_card.dat'."%(template)))
  name = template[:index1]
  card = template[index2:] # e.g. 'proc_card.dat', 'custumizecards.dat' ...
  return name, card
  

def subplaceholders(label,**params):
  """Make card label from given label template with placeholders."""
  for key in paramrexp.findall(label):
    if key in params:
      label = label.replace('$'+key,str(params[key]).replace('.','p'))
    else:
      print(warning("subplaceholders: No parameter given for placeholder key '$%s' in card label '%s'"%(key,label),pre=">>> "))
  #for key, value in params.iteritems():
  #  label = label.replace('$'+key,str(value).replace('.','p'))
  #assert 'template' in template, "Template '%s' does not contain 'template'"%(template)
  return label
  

def createcardname(template,cardname,outdir=None,verb=1,**params):
  """Make card name from given template and card label.
  Replace placeholders in label with given parameter values, e.g. M$MASS
  Templates must adhere to one of the following formats:
    $NAME_template_*.dat, or
    $NAME_*_card.dat, $NAME_*.dat where * does not contain any '_'
  """
  indir = os.path.dirname(template)
  template = os.path.basename(template) # remove indir
  name, card = getcardname(template) # get model/process name from datacard template
  if 'NAME' in params:
    if params['NAME']!=name: # check for consistency
      print(warning("createcardname: Given name %r does not match template %r (=> name=%r)..."%(params['NAME'],template,name),pre=">>> "))
    name = params['NAME']
  else: # set name for first time
    params['NAME'] = name
  assert name, "Could not parse %r to create name for datacard"%(template)
  assert card, "Could not parse %r to create datacard extension"%(template)
  cardname_ = subplaceholders(cardname,**params)
  cardfname = cardname_+'_'+card # replace parameter placeholders
  if outdir:
    params['CARDNAME'] = cardname_
    outdir = subplaceholders(outdir,**params)
    ensuredir(outdir)
    cardfname = os.path.join(outdir,os.path.basename(cardfname))
  else: # rejoin with indir
    cardfname = os.path.join(indir,os.path.basename(cardfname))
  if verb>=2:
    print(">>> createcardname: name=%r, cardname=%r, card=%r, outdir=%r, cardname=%r"%(name,cardname_,card,outdir,cardfname))
  return name, cardname_, cardfname
  

def createcard(template,cardname,outdir=None,verb=0,**params):
  """Create datacards from single template, replacing placeholders with given parameter values."""
  assert os.path.isfile(template), error("Input card '%s' does not exist!"%template)
  
  # CARD NAME
  name, cardname, cardfname = createcardname(template,cardname,outdir=outdir,verb=verb,**params)
  ###if outdir:
  ###  ensuredir(outdir)
  ###  #cardfname = os.path.join(outdir,os.path.basename(cardfname))
  
  if any(isinstance(v,str) and '$NAME' in v for k,v in params.items()) and 'NAME' not in params:
    params['NAME'] = name ###getname(template)
  
  def makeParamValue(key,value):
    """Local help function to replace placeholders in parameter values."""
    if not isinstance(value,str) or '$' not in value:
      return str(value)
    return subplaceholders(value,**params)
  
  # FIX BWCUTOFF for high lambda LQ samples
  lambd = float(params.get('LAMBDA',0))
  mass  = float(params.get('MASS',0))
  ###if 'LQ' in template and 'BWCUTOFF' not in params and lambd>=1.5 and mass>0:
  ###  params['BWCUTOFF'] = computeBWCutoff(template,mass,lambd)
  ###  if verb>=1:
  ###    print(">>> createcard: Computed bwcutoff=%s for mass=%s, lambda=%s"%(params['BWCUTOFF'],mass,lambd))
  
  # REPLACE
  if verb>=2:
    print(">>> Replacing placeholders in '%s'..."%(green(template)))
  lines = [ ]
  with open(template,'r') as file:
    for i, line in enumerate(file.readlines(),1):
      linenum = "L%d:"%i
      if '$' in line:
        for key in paramrexp.findall(line):  # e.g. '$LAMBDA'
          if key in params: # found placeholder
            value   = makeParamValue(key,params[key])
            pattern = '$'+key
            line    = line.replace(pattern,value)
            if verb>=1:
              print(">>>   %-4s replacing '%s' -> '%s'"%(linenum,pattern,value))
          else: # found unknown placeholder
            if 'DEFAULT_PDF_MEMBERS' in line: continue # ignore placeholder known to MadGraph
            if verb>=1:
              print(">>>   %-4s Found unknown placeholder key '$%s'; no value given"%(linenum,key))
        for pattern, key, value in defaultrexp.findall(line): # e.g. '${LAMBDA=1.0}'
          value = makeParamValue(key,params.get(key,value))
          line  = defaultrexp.sub(value,line)
          if verb>=1:
            print(">>>   %-4s replacing '%s' -> '%s'"%(linenum,pattern,value)+("" if key in params else " (default)"))
      lines.append(line)
  
  # WRITE
  if verb>=2:
    print(">>> Writing '%s'..."%(green(cardfname)))
  with open(cardfname,'w') as file:
    for line in lines:
      file.write(line)
  if verb>=1:
    print('>>> Written file "%s"'%(green(cardfname)))
    print(">>> "+'-'*85)
  
  return name, cardname, cardfname
  

def createcards(templates,cardname,masses,params,outdir,verb=0):
  """Main routine: create datacards from given templates and parameters."""
  
  # PARSE PARAMETER DICT
  paramdict = parseparams(params,masses=masses,cardname=cardname)
  if not cardname:
    cardname = paramdict['OUTPUT'] # e.g. $NAME_M$MASS_L$LAMBDA"
  if not isinstance(templates,list):
    templates = [templates]
  
  # EXPAND TEMPLATES if only directory is given:
  for template in templates[:]:
    if not any(template.endswith(e) for e in ['.dat','.txt']): # assume is directory
      assert os.path.exists(template), "Directory %r does not exist!"%(template)
      templates_ = glob.glob(os.path.join(template,"*.dat")) # get template files
      assert len(templates_)>0, "Did not find any data cards in %r..."%(template)
      index = templates.index(template)
      templates = templates[:index]+templates_+templates[index+1:] # insert template files
  
  # CREATE POINTS (all possible combinations of parameter values)
  points = list(itertools.product(*[[v] if isinstance(v,str) else list(v) for k, v in paramdict.items()]))
  
  # PRINT
  if verb>=1:
    print(">>> "+'='*90)
    print(">>> templates  = %s"%', '.join(bold(t) for t in templates))
    print(">>> cardname   = %r"%cardname)
    print(">>> massses    = %s"%masses)
    print(">>> params     = %s"%', '.join("%s: %s"%(bold(k),l) for k, l in paramdict.items()))
    if verb>=2:
      print(">>> points     = %r"%points)
    print(">>> "+'='*90)
  
  # CREATE CARDS
  names = [ ] # set to avoid doubles
  for values in points:
    kwargs = { }
    for key, value in zip(paramdict.keys(),values):
      kwargs[key] = value
    for template in templates:
      name, _, _ = createcard(template,cardname,outdir,verb=verb,**kwargs)
      if name not in names:
        names.append(name)
  
  return names
  

def parseparams(params,masses=[],cardname=None):
  """Parse parameters and return ordered dictionary placeholder key
  with a list of parameter values, e.g.
    parseparams([1000,1500,2000],'LAMBDA=0.5,1.0,1.5:PDF=315200')
    returns { 'MASS': [1000,1500,2000], 'LAMBDA': [1.0,1.5], 'PDF': [315200],
              'OUTPUT': '$NAME_M$MASS_L$LAMBDA' }
  """
  paramdict = OrderedDict()
  if masses: # special type of parameter
    paramdict['MASS'] = masses #{ 'MASS': masses }
  if isinstance(params,str):
    for param in params.split(':'):
      assert '=' in param, "Invalid format %r; no '=' for %r"%(params,param)
      param, values = param[:param.index('=')], param[param.index('=')+1:].split(',')
      assert param not in paramdict, error("Key %r defined multiple times!"%param)
      paramdict[param] = values
      #paramdict[param] = values
  elif isinstance(params,dict):
    for key, values in params.items():
      paramdict[key] = values
  else:
    raise TypeError("params must be string or dictionary! Received %r of type=%r..."%(params,type(params)))
  if not cardname: # for labeling the sample and cards
    cardname = "$NAME"
    if paramdict:
      cardname += '_'+"_".join(k[0]+'$'+k for k in paramdict.keys())
  if 'OUTPUT' not in paramdict: # output directory
    paramdict['OUTPUT'] = cardname
  return paramdict
  

def main(args):
  templates  = args.templates # e.g. cards/LQ/LQ_template*.dat
  cardname   = args.cardname # e.g. $NAME_M$MASS_L$LAMBDA"
  masses     = args.masses
  params     = args.params
  outdir     = args.outdir
  verbosity  = args.verbosity
  createcards(templates,cardname,masses,params,outdir,verb=verbosity)
  

if __name__ == '__main__':
  from argparse import ArgumentParser
  description = '''Create MadGraph cards from templates that contain placeholder with $ signs.
  Default parameter values can be set with the following format: ${LAMBDA=1.0}.
  E.g. $MASS, ${LAMBDA=1.0} and $PDF in cards with 'template' in the name:
  ./create_cards.py LQ_template_*.dat -n '$SAMPLE_$MASS_L$LAMBDA_LOPDF' -m 500 -p LAMBDA=0.5,1.0,1.5:PDF=315200'''
  parser = ArgumentParser(prog="create_cards",description=description,epilog="Good luck!")
  parser.add_argument('templates',         type=str, nargs='+', action='store',
                       metavar='TEMPLATE', help="template cards" )
  parser.add_argument('-m', '--mass',      dest='masses', type=int, nargs='+', default=[ ], action='store',
                                           help="generate this mass points" )
  parser.add_argument('-n', '--cardname',  type=str, action='store', default=None,
                                           help="card name (placeholders allowed)" )
  parser.add_argument('-o', '--outdir',    type=str, action='store', default=None,
                                           help="output directory" )
  parser.add_argument('-p', '--param',     dest='params', default="",
                      metavar='PARAMS',    help="single string of placeholder keys for parameter separated by colons,"+\
                                                "each with a list of values separated commas, e.g. LAMBDA=0.5,1.0,1.5:PDF=315200" )
  parser.add_argument('-v', "--verbose",   dest='verbosity', type=int, nargs='?', const=2, default=1,
                                           help="set level of verbosity, default=%(default)s" )
  args = parser.parse_args()
  print(">>> ")
  main(args)
  print(">>> ")
  

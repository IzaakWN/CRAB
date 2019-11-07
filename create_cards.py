#! /usr/bin/env python
# Author: Izaak Neutelings (November, 2019)
# Usage:
#  ./create_cards.py cards/LQ_template_*.dat -n '$MASS_L$LAMBDA_NNPDF31_LO' -m 1000 -p LAMBDA=0.1,1.0,1.5:PDF=315200
# Source:
#   git clone git@github.com:cms-sw/genproductions.git genproductions
#   cd genproductions/bin/MadGraph5_aMCatNLO/
#   ./gridpack_generation.sh <process name without _proc_card.dat> <card dir>
import os, re, glob
import itertools
from utils import formatTag, bold, error, warning, green
parampattern   = re.compile(r"\$([a-zA-Z0-9.-]+)") #re.compile(r"\$(\w+)")
defaultpattern = re.compile(r"(\$\{(\w+)=([^}]+)\})")
cardpattern    = re.compile(r"(.+)(_[^_]+(?<!_card)(?<!_FKS_params)\.dat|_[^_]+_card\.dat|_FKS_params\.dat)$") # *_run_card.dat, *_custumizecards.dat, ...

def main(args):
  
  templates  = args.templates
  cardlabel  = args.cardlabel
  masses     = args.masses
  outdir     = args.outdir
  
  # CREATE POINTS
  if masses:
    keys   = ['MASS']
    params = [('MASS',masses)] #{ 'MASS': masses }
  else:
    keys   = [ ]
    params = [ ]
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
  points = list(itertools.product(*[v for k, v in params]))
  
  # PRINT
  print ">>> "+'='*90
  print ">>> templates   = %s"%', '.join(bold(t) for t in templates)
  print ">>> cardlabel   = '%s'"%cardlabel
  print ">>> massses     = %s"%masses
  print ">>> params      = %s"%', '.join("%s: %s"%(bold(k),l) for k, l in params)
  print ">>> "+'='*90
  
  # SUBMIT
  for values in points:
    kwargs = { }
    for key, value in zip(keys,values):
      kwargs[key] = value
    for template in templates:
      cardname = makeCardName(template,cardlabel,outdir,**kwargs)
      makeCard(template,cardname,outdir,verbose=True,**kwargs)
  

def getCards(carddir, sample):
  """Find all cards of a given sample in a directory."""
  cards = [ ]
  for card in glob.glob("%s/%s_*.dat"%(carddir,sample)):
    card = os.path.basename(card)
    match = cardpattern.match(card)
    if match and match.group(1)!=sample:
      continue
    cards.append(card)
  return cards
  
def getSampleName(template):
  """Get the sample name from a card name,
  e.g. 'LQ_M500' for 'LQ_M500_proc_card.dat'."""
  template = os.path.basename(template)
  if 'template' in template:
    samplename = template[:template.index('template')].rstrip('_')
  else:
    match = cardpattern.match(template)
    if match:
      samplename = match.group(1)
    else:
      samplename = template.rstrip('.dat')
      print warning("getSampleName: Did not find sample name in '%s'!"%samplename)
  ###elif template.endswith('_card.dat') and template.count('_')>=2:
  ###  index = template.rindex('_',0,len(template)-len('_card.dat'))
  ###  samplename = template[:index]
  ###elif template.count('_')>=1:
  ###  index = template.rindex('_')
  ###  samplename = template[:index]
  ###else:
  ###  samplename = template.rstrip('.dat')
  ###  print warning("getSampleName: Did not find sample name in '%s'!"%samplename)
  return samplename
  
def makeCardLabel(label,**params):
  """Make card label from given label template with placeholders."""
  for key in parampattern.findall(label):
    if key in params:
      label = label.replace('$'+key,str(params[key]).replace('.','p'))
    else:
      print warning("No parameter given for key '$%s' in card label '%s'"%(key,label))
  #for key, value in params.iteritems():
  #  label = label.replace('$'+key,str(value).replace('.','p'))
  #assert 'template' in template, "Template '%s' does not contain 'template'"%(template)
  return label
  
def makeCardName(template,cardlabel,outdir=None,**params):
    """Make card name from given template and label.
    Replace placeholders in label with given parameters, e.g. M$MASS
    Templates must adhere to one of the following formats:
      $SAMPLE_template_*.dat, or
      $SAMPLE_*_card.dat, $SAMPLE_*.dat where * does not contain '_'
    """
    label = makeCardLabel(cardlabel,**params)
    if 'template' in template:
      cardname = template.replace('template',label)
    elif template.endswith('_card.dat') and template.count('_')>=2:
      index = template.rindex('_',0,len(template)-len('_card.dat'))
      cardname = template[:index]+'_'+label+template[index:]
    elif template.count('_')>=1:
      index = template.rindex('_')
      cardname = template[:index]+'_'+label+template[index:]
    elif not outdir: # prevent overwriting template
      raise IOError(error("Template card '%s' does not have a correct format. It should contain 'template', or at least one '_'."%(template)))
    if outdir:
      cardname = os.path.join(outdir,os.path.basename(cardname))
    return cardname
    
def makeCard(template, cardname, outdir=None, verbose=False, **params):
    """Replace placeholders in template with values."""
    assert os.path.isfile(template), error("Input card '%s' does not exist!"%template)
    
    # CARD NAME
    if outdir:
      cardname = os.path.join(outdir,os.path.basename(cardname))
    #cardname = makeCardName(template,cardlabel,outdir,**params)
    
    def makeParamValue(key,value):
      """Local help function to replace placeholders in parameter values."""
      if not isinstance(value,str) or '$' not in value:
        return str(value)
      if '$SAMPLE' in value and 'SAMPLE' not in params:
        params['SAMPLE'] = getSampleName(template)
      return makeCardLabel(value,**params)
    
    # PRINT
    ###print ">>> "+'-'*85
    ###print ">>> template    = %s"%template
    ###print ">>> cardname    = '%s'"%cardname
    ###print ">>> params      = %s"%params
    ###print ">>> "+'-'*85
    
    # REPLACE
    if verbose:
      print ">>> makeCard: replacing in '%s'..."%(green(template))
    else:
      print ">>> makeCard: writing '%s'..."%(green(os.path.basename(cardname)))
    lines = [ ]
    with open(template,'r') as file:
      for i, line in enumerate(file.readlines(),1):
        if '$' in line:
          for key in parampattern.findall(line):
            if key in params:
              value   = makeParamValue(key,params[key])
              pattern = '$'+key
              line    = line.replace(pattern,value)
              print ">>>   L%d: replacing '%s' -> '%s'"%(i,pattern,value)
            else:
              print ">>>   L%d: Found no given value for '$%s'"%(i,key)
          for pattern, key, value in defaultpattern.findall(line):
              value = makeParamValue(key,params.get(key,value))
              line  = defaultpattern.sub(value,line)
              print ">>>   L%d: replacing '%s' -> '%s'"%(i,pattern,value)+("" if value in params else " (default)")
        lines.append(line)
    
    # WRITE
    with open(cardname,'w') as file:
      for line in lines:
        file.write(line)
    if verbose:
      print '>>> makeCard: written file "%s"'%(green(cardname))
      print ">>> "+'-'*85
    


if __name__ == '__main__':
  from argparse import ArgumentParser
  description = '''Create MadGraph cards from templates that contain placeholder with $ signs.
  Default parameter values can be set with the following format: ${LAMBDA=1.0}.
  E.g. $MASS, ${LAMBDA=1.0} and $PDF in cards with 'template' in the name:
  ./create_cards.py LQ_template_*.dat -n '$MASS_L$LAMBDA_LOPDF' -m 500 -p LAMBDA=0.1,1.0,1.5:PDF=315200'''
  parser = ArgumentParser(prog="create_cards",description=description) #,epilog="Succes!")
  parser.add_argument('templates',         type=str, nargs='+', action='store',
                       metavar='TEMPLATE', help="template cards" )
  parser.add_argument('-m', '--mass',      dest='masses', type=int, nargs='+', default=[ ], action='store',
                                           help="generate this mass points" )
  parser.add_argument('-n', '--cardlabel', type=str, action='store', default=None,
                                           help="card label replacing" )
  parser.add_argument('-o', '--outdir',    type=str, action='store', default=None,
                                           help="output directory" )
  parser.add_argument('-p', '--param',     dest='params', default="",
                      metavar='PARAMS',    help="single string of parameters separated by colons,"+\
                                                "each with a list of values separated commas" )
  args = parser.parse_args()
  print ">>> "
  main(args)
  print ">>> "
  


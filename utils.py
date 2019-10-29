# Author: Izaak Neutelings (October, 2019)
from fnmatch import fnmatch
import Utilities.General.cmssw_das_client as dasclient

def green(string,**kwargs):
  return "\x1b[0;32;40m%s\033[0m"%string

def bold(string,**kwargs):
  return "\033[1m%s\033[0m"%string
  
def warning(string,**kwargs):
  """Print warning with color."""
  pre    = kwargs.get('pre',  "") + "\033[1m\033[93mWarning!\033[0m \033[93m"
  title  = kwargs.get('title',"")
  if title: pre = "%s%s: "%(pre,title)
  string = "%s%s\033[0m"%(pre,string)
  print string.replace('\n','\n'+' '*(len(pre)-18))
  

def formatTag(tag):
  """Format a tag, such that it always starts with one '_'."""
  if tag and tag[0]!='_':
    tag = '_'+tag
  return tag
  


def matchSampleToPattern(sample,patterns):
  """Match sample name to some pattern, using glob wildcards '*' or '?'."""
  sample = sample.lstrip('/')
  if not isinstance(patterns,list):
    patterns = [patterns]
  for pattern in patterns:
    if any(p in pattern for p in ['*','?','[','^']):
      if fnmatch(sample,pattern+'*'):
        return True
    else:
      if pattern in sample[:len(pattern)+1]:
        return True
  return False
  
def filterSamplesWithPattern(strings,patterns,veto=False):
  """Filter list of strings according to some given pattern(s)."""
  if veto:
    newlist = [s for s in strings if not matchSampleToPattern(s,patterns)]
  else:
    newlist = [s for s in strings if matchSampleToPattern(s,patterns)]
  return newlist
  


def getSampleSites(dataset,instance=None):
  """Get the sites a given dataset (DAS path) is stored on."""
  query = "site dataset=%s"%(dataset)
  if not instance and dataset.endswith('/USER'):
    instance = 'phys03'
  if instance:
    query += " instance=prod/%s"%instance
  print query
  data  = dasclient.get_data(query)['data']
  print data
  sites = [ ]
  for d in data:
    for site in d['site']:
      if 'TAPE' not in site.get('se','') and site['name'] not in sites:
        sites.append(str(site['name']))
  return sites
  

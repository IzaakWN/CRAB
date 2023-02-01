# Author: Izaak Neutelings (October 2019)
import os
from fnmatch import fnmatch
#if os.getenv('CMSSW_BASE'):
#  import Utilities.General.cmssw_das_client as dasclient

def ensuredir(dirname):
  """Make directory if it does not exist."""
  if not os.path.exists(dirname):
    os.makedirs(dirname)
    print('>>> made directory "%s"'%(dirname))
    if not os.path.exists(dirname):
      print('>>> failed to make directory "%s"'%(dirname))
  return dirname
  
def green(string,**kwargs):
  return "\x1b[0;32;40m%s\033[0m"%string
  
def bold(string,**kwargs):
  return "\033[1m%s\033[0m"%string
  
def error(string,**kwargs):
  return "\x1b[1;31;40m%s\033[0m"%string
  

def subkey(string,**kwargs):
  """Replace keys with '$'."""
  for key, value in sorted(kwargs.items(),key=lambda x: -len(x[0])):
    if '${'+key in string: # BASH variable expansions
      matches = re.findall(r"\$\{%s:(\d*):(\d+)\}"%(key),string)
      for a, b in matches:
        substr = value[int(a or 0):int(b)]
        string = re.sub(r"\$\{%s:%s:%s\}"%(key,a,b),substr,string)
    string = string.replace('$'+key,str(value))
  return string
  

def warning(string,**kwargs):
  """Print warning with color."""
  pre    = kwargs.get('pre',  "") + "\033[1m\033[93mWarning!\033[0m \033[93m"
  title  = kwargs.get('title',"")
  if title: pre = "%s%s: "%(pre,title)
  string = "%s%s\033[0m"%(pre,string)
  return string.replace('\n','\n'+' '*(len(pre)-18))
  

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
  import Utilities.General.cmssw_das_client as dasclient
  query = "site dataset=%s"%(dataset)
  if not instance and dataset.endswith('/USER'):
    instance = 'phys03'
  if instance:
    query += " instance=prod/%s"%instance
  data  = dasclient.get_data(query)['data']
  sites = [ ]
  for d in data:
    for site in d['site']:
      if 'TAPE' not in site.get('se','') and site['name'] not in sites:
        sites.append(str(site['name']))
  return sites
  

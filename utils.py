# Author: Izaak Neutelings (October, 2019)
from fnmatch import fnmatch

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
    if '*' in pattern or '?' in pattern:
      if fnmatch(sample,pattern+'*'):
        return True
    else:
      if pattern in sample[:len(pattern)+1]:
        return True
  return False
  
def filterSamplesWithPattern(strings,patterns):
  """Filter list of strings according to some given pattern(s)."""
  newlist = [s for s in strings if matchSampleToPattern(s,patterns)]
  return newlist
#!/usr/bin/env python
#
## higher-level shell utilities
# adapted from Mike McKerns' gsl.infect.utils
# by mmckerns@caltech.edu

"""
higher-level shell utilities for user environment and filesystem exploration
"""

from __future__ import absolute_import
import os
from . import shutils
from ._disk import kbytes, disk_used

#NOTE: broke backward compatibility January 17, 2014
#      seperator --> separator
def pattern(list=[],separator=';'):
    '''pattern([list,separator]); Generate a filter pattern from list of strings

    The returned filter is a string, with items seperated by separator'''
    filter = ''
    for item in list:
        filter += '%s%s' % (str(item),str(separator))
    return filter.rstrip(str(separator))

_varprog = None
def expandvars(string,ref=None,secondref={}):
    """expandvars(string[,ref,secondaryref]); expand shell variables in string

    Expand shell variables of form $var and ${var}.  Unknown variables
    are left unchanged. If a reference dictionary (ref) is provided,
    restrict the lookup to ref. A second reference dictionary (secondref)
    can also be provided for failover searches. If ref is not provided,
    lookup variables defined in the user\'s environment variables.

    For example:
        >>> expandvars(\'found:: $PYTHONPATH\')
        \'found:: .:/Users/foo/lib/python3.4/site-packages\'

        >>> expandvars(\'found:: $PYTHONPATH\', ref={})
        \'found:: $PYTHONPATH\'
    """
    if ref is None: ref = os.environ
    refdict = {}
    refdict.update(secondref)
    refdict.update(ref)
    global _varprog
    if '$' not in string:
        return string
    if not _varprog:
        import re
        _varprog = re.compile(r'\$(\w+|\{[^}]*\})')
    i = 0
    while True:
        m = _varprog.search(string, i)
        if not m:
            break
        i, j = m.span(0)
        name = m.group(1)
        if name[:1] == '{' and name[-1:] == '}':
            name = name[1:-1]
        if name in refdict:
            tail = string[j:]
            string = string[:i] + refdict[name]
            i = len(string)
            string = string + tail
        else:
            i = j
    return string

#NOTE: broke backward compatibility January 17, 2014
#      vdict --> ref
def getvars(path,ref=None):
    '''getvars(path[,ref]); Get a dictionary of all variables defined in path

    Extract shell variables of form $var and ${var}.  Unknown variables
    will raise an exception. If a reference dictionary (ref) is provided,
    first try the lookup in ref.  Failover from ref will lookup variables
    defined in the user\'s environment variables.

    For example:
        >>> getvars(\'$HOME/stuff\')
        {\'HOME\': \'/Users/foo\'}
    '''
    #what about using os.path.expandvars ?
    if ref is None: ref = {}
    ndict = {}
    dirs = path.split(os.sep)
    for dir in dirs:
        if '$' in dir:
            key = dir.split('$')[1].lstrip('{').rstrip('}')
            #get value from ref, or failing...
            try:
                ndict[key] = ref[key]
            #get value from os.environ, or failing... raise a KeyError
            except KeyError:
                ndict[key] = os.environ[key]
    return ndict

def convert(files,platform=None,pathsep=None):
    '''convert(files[,platform,pathsep])
    Convert text files to given platform type (os.linesep is not good enough)'''
    if not platform: platform = os.name
    if not pathsep: pathsep = os.pathsep
    MAC = '\r'
    WIN = '\r\n'
    LIN = '\n'
    linesep = [WIN,MAC,LIN]
    #os.name ==> ['posix','nt','os2','mac','ce','riscos']
    if platform in ['linux2','linux','unix','lin','posix','riscos']: #???
        newlinesep = LIN
    elif platform in ['windows','mswindows','win','dos','nt','os2','ce']: #???
        newlinesep = WIN
    elif platform in ['mac','macosx']: #???
        newlinesep = MAC
    else:
        print("Error: Platform '%s' not recognized" % platform)
        return 2 # Error 2: platform not recognized
    allconverted = 0 # Success
    for file in files.split(pathsep):
        try:
            infile = open(file, 'r')
            filestring = infile.read()
            infile.close()
            for i in linesep:
                filestring = filestring.replace(i, newlinesep)
            outfile = open(file, 'w')
            outfile.write(filestring)
            outfile.close()
            print("Converted '%s' to '%s' format" % (file,platform))
        except:
            print("File conversion failed for '%s'" % (file))
            allconverted = 1 # Error 1: file conversion failed
    return allconverted

def replace(file,sub={},outfile=None):
    '''replace(file,[sub,outfile]); Replace text {old:new} in the given file

    file: path to original file
    sub: dictionary of strings to replace, with entries of {old:new}
    outfile: if an outfile is given, don't overwrite the original file

    replace uses regular expressions, thus a pattern may be given as old text.
    Note this function can fail if order of substitution is important.'''
    #XXX: use OrderedDict instead... would enable ordered substitutions
    if outfile == None: outfile = file
    input = open(file, 'r')
    filestring = input.read()
    input.close()
    import re
    for old,new in sub.items():
        filestring = re.compile(old).sub(new,filestring)
    output = open(outfile, 'w')
    output.write(filestring)
    output.close()
    return

def index_slice(sequence,start,stop,step=1,sequential=False,inclusive=False):
    '''index_slice(sequence,start,stop[,step,sequential,inclusive]);
    Get the slice for a sequence, where the slice indicies are determined
    by the positions of \'start\' and \'stop\' within the sequence.

    If start is not found in the sequence, slice from the beginning. If stop
    is not found in the sequence, slice to the end. If inclusive=False,
    slicing will be performed with standard conventions (i.e. include start,
    but not stop); if inclusive=True, stop will be included. If sequential,
    then stop will not be searched for before start.'''
    if start in sequence:
        begin = sequence.index(start)
    else: begin = None
    if sequential: here = None
    else: here = begin
    if stop in sequence[here:]:
        end = sequence[here:].index(stop)
        if here: end += here
    else: end = None
    if inclusive and end != None: end += 1
    return slice(begin,end,step)

def index_join(sequence,start,stop,step=1,sequential=True,inclusive=True):
    '''index_join(sequence,start,stop[,step,sequential,inclusive]);
    Slices a list of strings, then joins the remaining strings.

    If start is not found in the sequence, slice from the beginning. If stop
    is not found in the sequence, slice to the end. If inclusive=False,
    slicing will be performed with standard conventions (i.e. include start,
    but not stop); if inclusive=True, stop will be included. If sequential,
    then stop will not be searched for before start.'''
    islice = index_slice(sequence,start,stop,step,sequential,inclusive)
    return ''.join(sequence[islice])

#NOTE: broke backward compatibility January 17, 2014
#      firstval=False --> all=False
def findpackage(package,root=None,all=False):
    '''findpackage(package[,root,all]); Get path(s) for a source distribution

    root: path string of top-level directory to search
    all: if True, return list of paths where package is found

    findpackage will do standard pattern matching for names of packages,
    attempting to match the head directory of the distribution'''
    if not root: root = os.curdir
    print('searching %s...' % root)
    if package[0] != os.sep: package = os.sep+package
    packdir,basedir = os.path.split(package)
    targetdir = shutils.find(basedir,root,recurse=1,type='d')
    #print("targetdir: "+targetdir)
    #remove invalid candidate directories (and 'BLD_ROOT' & 'EXPORT_ROOT')
    bldroot = shutils.env('BLD_ROOT',all=False)
    exproot = shutils.env('EXPORT_ROOT',all=False)
    remlist = []
    import fnmatch
    for dir in targetdir:
        if (not fnmatch.fnmatch(dir,'*'+package)) or \
           (not fnmatch.fnmatch(os.path.basename(dir),basedir)) or \
           ((bldroot) and (bldroot in dir)) or \
           ((exproot) and (exproot in dir)):
            remlist.append(dir) #build list of bad matches
    for dir in remlist:
        targetdir.remove(dir)
    if targetdir: print('%s found' % package)
    else: print('%s not found' % package)
    if all:
        return targetdir
    return select(targetdir,counter=os.sep,minimum=True,all=False)

#NOTE: broke backward compatibility January 18, 2014
#      minimum=True --> minimum=False
def select(iterable,counter='',minimum=False,reverse=False,all=True):
    '''select(iterable[,counter,minimum,reverse,all]); Find items in iterable
    with the minimum/maximum count of the given counter.

    iterable: an iterable of iterables (e.g. a list of lists, list of strings)
    counter: the item to count (e.g. counter=\'3\' counts occurances of \'3\')
    minimum: if True, find items with minimum count; if False, find maximum
    reverse: if True, reverse order of the results; if False, maintain order
    all: if False, only return the first result

    For example:
        >>> z = [\'zero\',\'one\',\'two\',\'three\',\'4\',\'five\',\'six\',\'seven\',\'8\',\'9/81\']
        >>> select(z, counter=\'e\')
        [\'three\', \'seven\']
        >>> select(z, counter=\'e\', minimum=True)
        [\'two\', \'4\', \'six\', \'8\', \'9/81\']
        >>>
        >>> y = [[1,2,3],[4,5,6],[1,3,5]]
        >>> select(y, counter=3)
        [[1, 2, 3], [1, 3, 5]]
        >>> select(y, counter=3, minumim=True, all=False)
        [4, 5, 6]
    '''
    itype = type(iterable)
    m = []
    for item in iterable:
        try: count = item.count(counter)
        except TypeError: count = 0  # catches '33'.count(3) --> 0
        except AttributeError: # catches 33.count(3) --> 0 (or 1)
            count = 1 if item == counter else 0
        m.append(count)
    if reverse:
        m.reverse()
        iterable.reverse()
    if not m:
        if all == True:
            return itype([])
        else:
            return None
    if minimum:
        x = min(m)
    else: x = max(m)
    if not all:
        return iterable[m.index(x)]
    shortlist = []
    tmp = []
    for item in iterable: tmp.append(item)
    occurances = m.count(x)
    for i in range(occurances):
        shortlist.append(tmp.pop(m.index(x)))
        m.pop(m.index(x))
    return itype(shortlist)

#NOTE: broke backward compatibility January 18, 2014
#      minimum=True --> minimum=False
def selectdict(dict,counter='',minimum=False,all=True):
    '''selectdict(dict[,counter,minimum,all]); Return a dict of items with
    the minimum/maximum count of the given counter.

    dict: dict with iterables as values (e.g. values are strings or lists)
    counter: the item to count (e.g. counter=\'3\' counts occurances of \'3\')
    minimum: if True, find items with minimum count; if False, find maximum
    all: if False, return a dict with only one item

    For example:
        >>> z = [\'zero\',\'one\',\'two\',\'three\',\'4\',\'five\',\'six\',\'seven\',\'8\',\'9/81\']
        >>> z = dict(enumerate(z))
        >>> selectdict(z, counter=\'e\')
        {3: \'three\', 7: \'seven\'}
        >>> selectdict(z, counter=\'e\', minimum=True)
        {8: \'8\', 9: \'9/81\', 2: \'two\', 4: \'4\', 6: \'six\'}
        >>>
        >>> y = {1: [1,2,3], 2: [4,5,6], 3: [1,3,5]}
        >>> selectdict(y, counter=3)
        {1: [1, 2, 3], 3: [1, 3, 5]}
        >>> selectdict(y, counter=3, minumim=True)
        {2: [4, 5, 6]}
    '''
    keys,values = zip(*dict.items())
    shortlist = select(values,counter,minimum,all=all)
    if not all:
        x = list(values).index(shortlist)
        return {keys[x]: values[x]}
    shortdict = {}
    for i in range(len(values)):
        if values[i] in shortlist:
            shortdict.update({keys[i]: values[i]})
    return shortdict

#NOTE: broke backward compatibility January 18, 2014
#      forceSSH --> loopback
def remote(path,host=None,user=None,loopback=False):
    """remote(path[,host,user,loopback]); Build string for remote connection
    of the form [[user@]host:]path.

    path: path string for location of target on (remote) filesystem
    host: string name/ip address of (remote) host
    user: user name on (remote) host
    loopback: if True, and host=None, then use host=localhost"""
    if loopback and not host: host = 'localhost'
    if host:
        path = '%s:%s' % (host,path)
        if user:
            path = '%s@%s' % (user,path)
    return path

#NOTE: broke backward compatibility January 18, 2014
#      forceSSH  --> loopback
#      useOption --> login_flag          
def parse_remote(path,loopback=False,login_flag=False):
    """parse_remote(path[,loopback,login_flag]); Parse remote connection string
    of the form [[user@]host:]path to a tuple of (user, host, path).

    path: remote connection string
    loopback: if True, and no host is found, then return host=localhost
    login_flag: if True, prepend user name with \'-l\'"""
    dpath = path.split(':')[-1]
    rhost = path.split(':')[0]
    if rhost == dpath:
        if loopback: return '','localhost',dpath
        return '','',dpath
    dhost = rhost.split('@')[-1]
    duser = rhost.split('@')[0]
    if duser == dhost: return '',dhost,dpath
    if login_flag: duser = '-l '+duser
    return duser,dhost,dpath


# backward compatability
makefilter = pattern
getVars = getvars
replaceText = replace
getLines = index_join
makeTarget = remote
parseTarget = parse_remote
prunelist = select
prunedict = selectdict


if __name__=='__main__':
    pass


# End of file 

import os
import bz2
import gzip
import logging
import shutil
import sys

from csv import DictReader
from collections import Iterable, OrderedDict, namedtuple
from os import path

log = logging.getLogger(__name__)


def mkdir(dirpath, clobber=False):
    """
    Create a (potentially existing) directory without errors. Raise
    OSError if directory can't be created. If clobber is True, remove
    dirpath if it exists.
    """

    if clobber:
        shutil.rmtree(dirpath, ignore_errors=True)

    try:
        os.mkdir(dirpath)
    except OSError as msg:
        pass

    if not os.path.exists(dirpath):
        raise OSError('Failed to create %s' % dirpath)

    return dirpath

Path = namedtuple('Path', ['dir', 'fname'])


def walker(dir):
    """Recursively traverse direcory `dir`. For each tuple containing
    (path, dirs, files) return a named tuple with attributes (dir,
    fname) for each file name in `files`.
    """

    for (pth, dirs, files) in os.walk(dir):
        for fname in files:
            yield Path(pth, fname)


def munge_path(pth):
    """
    Get date, machine, run, assay, version, 
    141104_HA0194_OPX55
    141006_HA0189_OncoPlex51    
    """
    parts = pth.split('_')
    run_info = ['run_date', 'machineID_run', 'project']
    if len(parts) < 3:
        raise ValueError(
            'Incorrect path given. Must be in the format of YYMMDD_MachineIDRun#_Project')

    return zip(run_info, parts)


class Opener(object):
    """Factory for creating file objects

    Keyword Arguments:
        - mode -- A string indicating how the file is to be opened. Accepts the
            same values as the builtin open() function.
        - bufsize -- The file's desired buffer size. Accepts the same values as
            the builtin open() function.
    """

    def __init__(self, mode='r', bufsize=-1):
        self._mode = mode
        self._bufsize = bufsize

    def __call__(self, string):
        if string is sys.stdout or string is sys.stdin:
            return string
        elif string == '-':
            return sys.stdin if 'r' in self._mode else sys.stdout
        elif string.endswith('.bz2'):
            return bz2.BZ2File(string, self._mode, self._bufsize)
        elif string.endswith('.gz'):
            return gzip.open(string, self._mode, self._bufsize)
        else:
            return open(string, self._mode, self._bufsize)

    def __repr__(self):
        args = self._mode, self._bufsize
        args_str = ', '.join(repr(arg) for arg in args if arg != -1)
        return '{}({})'.format(type(self).__name__, args_str)


def opener(pth, mode='r', bufsize=-1):
    return Opener(mode, bufsize)(pth)


def multi_split(source, splitlist):
    """
    Function to split a string given a string of multiple split points
    """
    output = []
    atsplit = True
    if source == None:
        return None
    else:
        for char in source:
            if char in splitlist:
                atsplit = True
            else:
                if atsplit:
                    output.append(char)
                    atsplit = False
                else:
                    output[-1] = output[-1] + char
    return output

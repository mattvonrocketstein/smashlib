""" smashlib.venv

    TODO: abstract this code to goulash and write tests
"""
import types
import os, sys, glob
from unipath import FSPath

from smashlib.python import opj, ope, expanduser, abspath
from smashlib.util import truncate_fpath

get_path   = lambda: os.environ['PATH']
get_venv   = lambda: os.environ['VIRTUAL_ENV']
to_vbin    = lambda venv: opj(venv, 'bin')
to_vlib    = lambda venv: opj(venv, 'lib')
venv_bin   = lambda cmd: opj(to_vbin(get_venv()), cmd)

def is_venv(dir):
    """ naive.. but seems to work
        TODO: find a canonical version of this function or refine it
    """
    if FSPath( opj(dir, 'bin', 'activate_this.py')).exists():
        return dir


def contains_venv(_dir, report=None):
    """ ascertain whether _dir is, or if it contains, a venv.
        returns the first matching path according to the heuritic:

          1) if the directoy is a venv, return it
          2) if the directory has subdir(s) that are venvs, return the first
          3) no venv found?  return None
    """
    _dir = abspath(expanduser(_dir))
    print _dir
    if is_venv(_dir):
        return _dir
    else:
        count = 1
        for dirpath,dirnames,filenames in os.walk(_dir):#).walk(top_down=False):
            # trick to make sure we dont process .git/.tox first, etc
            dirnames = [x for x in reversed(sorted(dirnames))]
            for subdir in dirnames:
                count+=1
                subdir = opj(dirpath, subdir)
                if is_venv(subdir):
                    return subdir
        if report is not None:
            assert callable(report)
            msg = "contains_venv({0}):"
            report(msg.format(_dir))
            msg = "  searched {0} subdirectories: found no python venv's"
            msg = msg.format(count)
            report(msg)

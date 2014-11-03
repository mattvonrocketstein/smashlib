"""
"""
def get_smash():
    ip = get_ipython()
    try:
        return ip._smash
    except AttributeError:
        raise Exception("load smash first")

from smashlib.python import get_env, opd, ops, opj, ope, expanduser

def home():
    return get_env('HOME')

import re

def truncate_fpath(fpath):
    return fpath.replace(home(), '~')

def split_on_unquoted_semicolons(txt):
    PATTERN = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
    return PATTERN.split(txt)[1::2]


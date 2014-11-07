""" smashlib.util

    Keep imports simple to avoid cycles!
    Safe, simple packages only (no ipython imports in here)
"""
import re

from smashlib.python import get_env, opd, ops, opj, ope, expanduser

from smashlib.util.reflect import from_dotpath

def load_user_config(env):
    from smashlib.data import user_config
    sandbox = env.copy();
    sandbox.update(__file__=user_config)
    execfile(user_config, sandbox)

def get_smash():
    ip = get_ipython()
    try:
        return ip._smash
    except AttributeError:
        raise Exception("load smash first")

def home():
    return get_env('HOME')

def truncate_fpath(fpath):
    return fpath.replace(home(), '~')

def split_on_unquoted_semicolons(txt):
    PATTERN = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
    return PATTERN.split(txt)[1::2]

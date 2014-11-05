""" smashlib.util

    Keep imports simple to avoid cycles!
"""
import re

from smashlib.python import get_env, opd, ops, opj, ope, expanduser
from IPython.utils.coloransi import TermColors

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

class receives_event(object):
    """ note: should only be used with imethods """
    def __init__(self, channel):
        self.channel = channel

    def __call__(self, fxn):
        def newf(himself, bus, *args, **kargs):
            if get_smash().verbose_events:
                zargs=args[0] if len(args)==1 else args
                msg = '{0}!{1}{2} @{3} ={4}'.format(
                    TermColors.LightPurple,
                    self.channel,
                    TermColors.Normal,
                    fxn.__name__,
                    zargs)
                if msg[:77]!=msg:
                    msg += '...'
                    msg=msg[:77]
                print msg
            return fxn(himself, *args, **kargs)
        newf._subscribe_to = self.channel
        return newf

def split_on_unquoted_semicolons(txt):
    PATTERN = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
    return PATTERN.split(txt)[1::2]

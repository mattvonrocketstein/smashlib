""" ipy_liquidprompt
"""
import os
from smashlib.v2 import Reporter
from smashlib.ipy_cd_hooks import CHANNEL

lp_f = os.path.join(os.path.dirname(__file__), 'liquidprompt')

class LiquidPrompt(Reporter):
    def init(self):
        self.smash.bus.subscribe(CHANNEL, self.cd_hook)

    def cd_hook(self, bus, new_dir, *args, **kargs):
        print '\n'+self.get_prompt().strip()

    def get_prompt(self):
        return os.popen(u'bash '+lp_f).read()

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    lp = LiquidPrompt(ip)
    ip._smash.lp = lp
    return lp

def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    pass

""" ipy_liquidprompt
"""
import os
import subprocess
from subprocess import PIPE
from smashlib.v2 import Reporter
from smashlib.ipy_cd_hooks import CHANNEL as C_CD_EVENT
from IPython.utils.traitlets import Bool

lp_f = os.path.join(os.path.dirname(__file__), 'liquidprompt')
C_UPDATE_PROMPT_REQUEST = 'udpate_prompt_request'

class LiquidPrompt(Reporter):
    """ this extension requires ipy_cd_hook """

    float    = Bool(True, config=True, help="add more space between prompts")

    def init(self):
        self.smash.bus.subscribe(C_CD_EVENT, self.cd_hook_event)
        self.smash.bus.subscribe(C_UPDATE_PROMPT_REQUEST,
                                 self.update_prompt_event)
        self.update_prompt()

    def cd_hook_event(self, bus, new_dir, *args, **kargs):
        self.update_prompt()

    def update_prompt_event(self, bus, request_from):
        self.update_prompt()

    def update_prompt(self):
        tmp = self.get_prompt().strip()
        if self.float==True:
            tmp = '\n' + tmp
        tmp = tmp + '\n>'
        self.shell.prompt_manager.in_template = tmp

    def get_prompt(self):
        cmd = unicode('bash '+lp_f)
        env = dict(
            TERM='xterm',
            PS1="",
            USER=os.environ['USER'],
            BASH_VERSION='4.3.11(1)-release',
            VIRTUAL_ENV=os.environ['VIRTUAL_ENV'],
            )
        tmp = subprocess.Popen(cmd, shell=True, env=env, stdout=PIPE)
        o,e = tmp.communicate()
        return o.decode('utf-8')

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    lp = LiquidPrompt(ip)
    ip._smash.lp = lp
    return lp

def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    print 'not implemented yet'
